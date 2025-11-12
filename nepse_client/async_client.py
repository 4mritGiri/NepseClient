"""
Asynchronous NEPSE client implementation.

This module provides a non-blocking, asynchronous interface to the NEPSE API,
suitable for concurrent operations and high-performance applications.
"""

import asyncio
import logging
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any, Optional, Union, cast

import httpx
import tqdm.asyncio

from .client import _NepseBase
from .dummy_id_manager import AsyncDummyIDManager
from .exceptions import NepseAuthenticationError, NepseNetworkError, NepseValidationError
from .token_manager import AsyncTokenManager


logger = logging.getLogger(__name__)


class AsyncNepseClient(_NepseBase):
    """
    Asynchronous client for NEPSE API.

    This client provides non-blocking async methods to access Nepal Stock Exchange
    data, enabling concurrent operations and better performance for bulk requests.

    Args:
       logger: Optional custom logger instance
       mask_request_data: Whether to mask sensitive data in logs (default: True)
       timeout: Request timeout in seconds (default: 100.0)

    Example:
       Basic usage::

          import asyncio
          from nepse_client import AsyncNepseClient

          async def main():
                client = AsyncNepseClient()

                # Get market status
                status = await client.getMarketStatus()
                print(f"Market is {status['isOpen']}")

                # Concurrent requests
                status, summary, gainers = await asyncio.gather(
                   client.getMarketStatus(),
                   client.getSummary(),
                   client.getTopGainers()
                )

          asyncio.run(main())

    Note:
       All methods are coroutines and must be awaited. The client automatically
       manages authentication tokens and handles token expiration.
    """

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        mask_request_data: bool = True,
        timeout: float = 100.0,
    ):
        """Initialize asynchronous NEPSE client."""
        super().__init__(
            AsyncTokenManager,
            AsyncDummyIDManager,
            logger=logger,
            mask_request_data=mask_request_data,
            timeout=timeout,
        )
        self.init_client(tls_verify=self._tls_verify)

    def init_client(self, tls_verify: bool) -> None:
        """
        Initialize async HTTP client with specified settings.

        Args:
           tls_verify: Whether to verify TLS certificates
        """
        self.client = httpx.AsyncClient(
            verify=tls_verify,
            http2=False,  # HTTP/2 can cause issues with some servers
            timeout=self.timeout,
            follow_redirects=True,
        )
        self.logger.debug(f"Async HTTP client initialized (TLS verify: {tls_verify})")

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup resources."""
        await self.close()

    async def close(self) -> None:
        """Close HTTP client and cleanup resources."""
        if hasattr(self, "client"):
            await self.client.aclose()
            self.logger.debug("Async HTTP client closed")

    # Private helper methods

    async def _retry_request(self, request_func, *args, max_retries: int = 3, **kwargs) -> Any:
        """
        Retry a request with exponential backoff.

        Args:
           request_func: Async function to retry
           max_retries: Maximum number of retry attempts
           *args, **kwargs: Arguments to pass to request_func

        Returns:
           Response from request_func

        Raises:
           NepseNetworkError: If all retries fail
        """
        for attempt in range(max_retries):
            try:
                return await request_func(*args, **kwargs)
            except (
                httpx.RemoteProtocolError,
                httpx.ReadError,
                httpx.ConnectError,
            ) as e:
                if attempt == max_retries - 1:
                    self.logger.error(f"Request failed after {max_retries} attempts: {e}")
                    raise NepseNetworkError(
                        f"Network error after {max_retries} retries: {e}"
                    ) from e

                wait_time = 2**attempt  # Exponential backoff
                self.logger.warning(
                    f"Request failed (attempt {attempt + 1}/{max_retries}), "
                    f"retrying in {wait_time}s..."
                )
                await asyncio.sleep(wait_time)

            except NepseAuthenticationError:
                self.logger.info("Token expired, refreshing...")
                await self.token_manager.update()
                # Retry immediately after token refresh
                return await request_func(*args, **kwargs)

    async def requestGETAPI(self, url: str, include_authorization_headers: bool = True) -> Any:
        """
        Make async GET request to NEPSE API.

        Args:
           url: API endpoint URL
           include_authorization_headers: Whether to include auth headers

        Returns:
           Parsed response data
        """

        async def _make_request():
            headers = (
                await self.getAuthorizationHeaders()
                if include_authorization_headers
                else {**self.headers, "User-Agent": self.get_random_user_agent()}
            )
            response = await self.client.get(
                self.get_full_url(api_url=url),
                headers=headers,
            )
            return self.handle_response(response)

        return await self._retry_request(_make_request)

    async def requestPOSTAPI(self, url: str, payload_generator) -> Any:
        """
        Make async POST request to NEPSE API.

        Args:
           url: API endpoint URL
           payload_generator: Async function to generate payload

        Returns:
           Parsed response data
        """

        async def _make_request():
            payload = {"id": await payload_generator()}
            response = await self.client.post(
                self.get_full_url(api_url=url),
                headers=await self.getAuthorizationHeaders(),
                json=payload,
                # data=payload,
            )
            return self.handle_response(response, request_data=payload)

        return await self._retry_request(_make_request)

    async def getAuthorizationHeaders(self) -> dict[str, str]:
        """
        Get headers with authorization token.

        Returns:
           Dictionary of HTTP headers
        """
        access_token = await self.token_manager.getAccessToken()
        return {
            "Authorization": f"Salter {access_token}",
            "Content-Type": "application/json",
            **self.headers,
            "User-Agent": self.get_random_user_agent(),
        }

    # Payload ID generators

    async def getPOSTPayloadIDForScrips(self) -> int:
        """Generate payload ID for scrip-related requests."""
        dummy_id = self.getDummyID()
        return int(self.getDummyData()[dummy_id] + dummy_id + 2 * date.today().day)

    async def getPOSTPayloadID(self) -> int:
        """Generate general payload ID."""
        e = await self.getPOSTPayloadIDForScrips()
        # Wait for token manager update to complete
        await self.token_manager.update_completed.wait()

        salt_index = 3 if e % 10 < 5 else 1
        return int(
            e
            + self.token_manager.salts[salt_index] * date.today().day
            - self.token_manager.salts[salt_index - 1]
        )

    async def getPOSTPayloadIDForFloorSheet(
        self, business_date: Optional[Union[str, date]] = None
    ) -> int:
        """
        Generate payload ID for floor sheet requests.

        Args:
           business_date: Business date (YYYY-MM-DD string or date object)

        Returns:
           Payload ID integer
        """
        e = await self.getPOSTPayloadIDForScrips()
        # Wait for token manager update to complete
        await self.token_manager.update_completed.wait()

        # Parse business_date
        if business_date is None:
            day = date.today().day
        elif isinstance(business_date, (date, datetime)):
            day = business_date.day
        else:
            try:
                parsed_date = datetime.strptime(str(business_date), "%Y-%m-%d")
                day = parsed_date.day
            except ValueError as ex:
                raise NepseValidationError(
                    f"Invalid date format: {business_date}. Expected YYYY-MM-DD.",
                    field="business_date",
                    value=business_date,
                ) from ex

        salt_index = 1 if e % 10 < 4 else 3
        return int(
            e
            + self.token_manager.salts[salt_index] * day
            - self.token_manager.salts[salt_index - 1]
        )

    # Override base methods with async versions

    async def getMarketStatus(self) -> dict[str, Any]:  # type: ignore[override]
        """Get current market status (open/closed)."""
        return cast(
            dict[str, Any], await self.requestGETAPI(url=self.api_end_points["nepse_open_url"])
        )

    async def getPriceVolume(self) -> list[dict[str, Any]]:  # type: ignore[override]
        """Get current price and volume data for all securities."""
        return cast(
            list[dict[str, Any]],
            await self.requestGETAPI(url=self.api_end_points["price_volume_url"]),
        )

    async def getSummary(self) -> dict[str, Any]:  # type: ignore[override]
        """Get market summary with turnover, trades, etc."""
        return cast(
            dict[str, Any], await self.requestGETAPI(url=self.api_end_points["summary_url"])
        )

    async def getTopGainers(self) -> list[dict[str, Any]]:  # type: ignore[override]
        """Get list of top gaining stocks."""
        return cast(
            list[dict[str, Any]],
            await self.requestGETAPI(url=self.api_end_points["top_gainers_url"]),
        )

    async def getTopLosers(self) -> list[dict[str, Any]]:  # type: ignore[override]
        """Get list of top losing stocks."""
        return cast(
            list[dict[str, Any]],
            await self.requestGETAPI(url=self.api_end_points["top_losers_url"]),
        )

    async def getTopTenTradeScrips(self) -> list[dict[str, Any]]:  # type: ignore[override]
        """Get top 10 scrips by trade volume."""
        return cast(
            list[dict[str, Any]],
            await self.requestGETAPI(url=self.api_end_points["top_ten_trade_url"]),
        )

    async def getTopTenTransactionScrips(self) -> list[dict[str, Any]]:  # type: ignore[override]
        """Get top 10 scrips by transaction count."""
        return cast(
            list[dict[str, Any]],
            await self.requestGETAPI(url=self.api_end_points["top_ten_transaction_url"]),
        )

    async def getTopTenTurnoverScrips(self) -> list[dict[str, Any]]:  # type: ignore[override]
        """Get top 10 scrips by turnover."""
        return cast(
            list[dict[str, Any]],
            await self.requestGETAPI(url=self.api_end_points["top_ten_turnover_url"]),
        )

    async def getSupplyDemand(self) -> dict[str, Any]:  # type: ignore[override]
        """Get supply and demand data."""
        return cast(
            dict[str, Any], await self.requestGETAPI(url=self.api_end_points["supply_demand_url"])
        )

    async def getNepseIndex(self) -> dict[str, Any]:  # type: ignore[override]
        """Get NEPSE index data."""
        return cast(
            dict[str, Any], await self.requestGETAPI(url=self.api_end_points["nepse_index_url"])
        )

    async def getNepseSubIndices(self) -> list[dict[str, Any]]:  # type: ignore[override]
        """Get all NEPSE sub-indices."""
        return cast(
            list[dict[str, Any]],
            await self.requestGETAPI(url=self.api_end_points["nepse_subindices_url"]),
        )

    async def getLiveMarket(self) -> dict[str, Any]:  # type: ignore[override]
        """Get live market data."""
        return cast(
            dict[str, Any], await self.requestGETAPI(url=self.api_end_points["live-market"])
        )

    async def getTradingAverage(  # type: ignore[override]
        self, business_date: Optional[str] = None, nDays: int = 180
    ) -> dict[str, Any]:
        """Get trading average data."""
        params = []
        if business_date:
            params.append(f"businessDate={business_date}")
        if nDays:
            params.append(f"nDays={nDays}")

        query_string = "&".join(params)
        url = f"{self.api_end_points['trading-average']}?{query_string}"
        return cast(dict[str, Any], await self.requestGETAPI(url=url))

    # Company and Security data methods

    async def getCompanyList(self) -> list[dict[str, Any]]:
        """Get list of all listed companies."""
        self.company_list = await self.requestGETAPI(url=self.api_end_points["company_list_url"])
        return list(self.company_list)

    async def getSecurityList(self) -> list[dict[str, Any]]:
        """Get list of all securities (non-delisted)."""
        self.security_list = await self.requestGETAPI(url=self.api_end_points["security_list_url"])
        return list(self.security_list)

    async def getCompanyIDKeyMap(self, force_update: bool = False) -> dict[str, int]:
        """Get mapping of company symbols to IDs."""
        if self.company_symbol_id_keymap is None or force_update:
            company_list = await self.getCompanyList()
            self.company_symbol_id_keymap = {
                company["symbol"]: company["id"] for company in company_list
            }
        return self.company_symbol_id_keymap.copy()

    async def getSecurityIDKeyMap(self, force_update: bool = False) -> dict[str, int]:
        """Get mapping of security symbols to IDs."""
        if self.security_symbol_id_keymap is None or force_update:
            security_list = await self.getSecurityList()
            self.security_symbol_id_keymap = {
                security["symbol"]: security["id"] for security in security_list
            }
        return self.security_symbol_id_keymap.copy()

    async def getSectorScrips(self) -> dict[str, list[str]]:
        """Get scrips grouped by sector."""
        if self.sector_scrips is None:
            company_info_dict = {
                company["symbol"]: company for company in await self.getCompanyList()
            }
            sector_scrips = defaultdict(list)

            for security in await self.getSecurityList():
                symbol = security["symbol"]
                company_info = company_info_dict.get(symbol)

                if company_info:
                    sector_name = company_info["sectorName"]
                    sector_scrips[sector_name].append(symbol)
                else:
                    sector_scrips["Promoter Share"].append(symbol)

            self.sector_scrips = dict(sector_scrips)

        return dict(self.sector_scrips)

    async def getCompanyDetails(self, symbol: str) -> dict[str, Any]:
        """Get detailed information for a specific company."""
        symbol = symbol.upper()
        company_id = (await self.getSecurityIDKeyMap())[symbol]
        url = f"{self.api_end_points['company_details']}{company_id}"
        return cast(
            dict[str, Any],
            await self.requestPOSTAPI(url=url, payload_generator=self.getPOSTPayloadIDForScrips),
        )

    async def getCompanyPriceVolumeHistory(
        self,
        symbol: str,
        start_date: Optional[Union[str, date]] = None,
        end_date: Optional[Union[str, date]] = None,
    ) -> dict[str, Any]:
        """Get price and volume history for a company."""
        # Convert strings to date objects
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d").date()

        # Default dates
        end_date = end_date or date.today()
        start_date = start_date or (end_date - timedelta(days=365))

        symbol = symbol.upper()
        company_id = (await self.getSecurityIDKeyMap())[symbol]

        url = (
            f"{self.api_end_points['company_price_volume_history']}{company_id}"
            f"?size=500&startDate={start_date}&endDate={end_date}"
        )

        result = await self.requestGETAPI(url=url)
        return cast(dict[str, Any], result.get("content", result))

    async def getDailyScripPriceGraph(self, symbol: str) -> dict[str, Any]:
        """Get daily price graph data for a scrip."""
        symbol = symbol.upper()
        company_id = (await self.getSecurityIDKeyMap())[symbol]
        url = f"{self.api_end_points['company_daily_graph']}{company_id}"
        return cast(
            dict[str, Any],
            await self.requestPOSTAPI(url=url, payload_generator=self.getPOSTPayloadIDForScrips),
        )

    # Floor sheet methods

    async def getFloorSheet(self, show_progress: bool = False) -> list[dict[str, Any]]:
        """
        Get complete floor sheet data.

        Args:
           show_progress: Show progress bar during download

        Returns:
           List of all floor sheet records
        """
        url = (
            f"{self.api_end_points['floor_sheet']}"
            f"?size={self.floor_sheet_size}&sort=contractId,desc"
        )

        # Get first page
        sheet = await self.requestPOSTAPI(
            url=url, payload_generator=self.getPOSTPayloadIDForFloorSheet
        )

        first_page = sheet["floorsheets"]["content"]
        total_pages = sheet["floorsheets"]["totalPages"]

        # Create tasks for remaining pages
        tasks = [self._getFloorSheetPageNumber(url, page_num) for page_num in range(1, total_pages)]

        # Execute with optional progress bar
        if show_progress:
            remaining_pages = await tqdm.asyncio.tqdm.gather(*tasks)
        else:
            remaining_pages = await asyncio.gather(*tasks)

        # Combine all pages
        all_pages = [first_page] + remaining_pages
        return cast(list[dict[str, Any]], [row for page in all_pages for row in page])

    async def _getFloorSheetPageNumber(self, url: str, page_number: int) -> list[dict[str, Any]]:
        """
        Get a specific page of floor sheet data.

        Args:
           url: Base floor sheet URL
           page_number: Page number to fetch

        Returns:
           List of records for the page
        """
        current_sheet = await self.requestPOSTAPI(
            url=f"{url}&page={page_number}",
            payload_generator=self.getPOSTPayloadIDForFloorSheet,
        )
        return cast(
            list[dict[str, Any]], current_sheet["floorsheets"]["content"] if current_sheet else []
        )

    async def getFloorSheetOf(
        self,
        symbol: str,
        business_date: Optional[Union[str, date]] = None,
    ) -> list[dict[str, Any]]:
        """Get floor sheet for a specific company."""
        symbol = symbol.upper()
        company_id = (await self.getSecurityIDKeyMap())[symbol]

        if business_date:
            if isinstance(business_date, str):
                business_date = date.fromisoformat(business_date)
        else:
            business_date = date.today()

        url = (
            f"{self.api_end_points['company_floorsheet']}{company_id}"
            f"?businessDate={business_date}&size={self.floor_sheet_size}"
            f"&sort=contractid,desc"
        )

        sheet = await self.requestPOSTAPI(
            url=url, payload_generator=self.getPOSTPayloadIDForFloorSheet
        )

        if not sheet:
            return []

        floor_sheets = sheet["floorsheets"]["content"]
        total_pages = sheet["floorsheets"]["totalPages"]

        # Fetch remaining pages concurrently
        if total_pages > 1:
            tasks = [
                self.requestPOSTAPI(
                    url=f"{url}&page={page_num}",
                    payload_generator=self.getPOSTPayloadIDForFloorSheet,
                )
                for page_num in range(1, total_pages)
            ]
            remaining_sheets = await asyncio.gather(*tasks)

            for sheet in remaining_sheets:
                floor_sheets.extend(sheet["floorsheets"]["content"])

        return cast(list[dict[str, Any]], floor_sheets)

    async def getSymbolMarketDepth(self, symbol: str) -> dict[str, Any]:
        """Get market depth for a symbol."""
        symbol = symbol.upper()
        company_id = (await self.getSecurityIDKeyMap())[symbol]
        url = f"{self.api_end_points['market-depth']}{company_id}/"
        return cast(dict[str, Any], await self.requestGETAPI(url=url))


__all__ = ["AsyncNepseClient"]
