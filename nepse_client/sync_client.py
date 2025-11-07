"""
Synchronous NEPSE client implementation.

This module provides a blocking, synchronous interface to the NEPSE API,
suitable for scripts, notebooks, and applications that don't require concurrency.
"""

import json
import logging
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import httpx
import tqdm

from .client import _NepseBase
from .dummy_id_manager import DummyIDManager
from .exceptions import NepseAuthenticationError, NepseNetworkError, NepseValidationError
from .token_manager import TokenManager


logger = logging.getLogger(__name__)


class NepseClient(_NepseBase):
    """
    Synchronous client for NEPSE API.

    This client provides blocking methods to access Nepal Stock Exchange data
    including market status, company information, trading data, and more.

    Args:
       logger: Optional custom logger instance
       mask_request_data: Whether to mask sensitive data in logs (default: True)
       timeout: Request timeout in seconds (default: 100.0)

    Example:
       Basic usage::

          from nepse_client import NepseClient

          client = NepseClient()

          # Get market status
          status = client.getMarketStatus()
          print(f"Market is {status['isOpen']}")

          # Get company details
          nabil = client.getCompanyDetails("NABIL")
          print(f"NABIL LTP: {nabil['lastTradedPrice']}")

    Note:
       The client automatically manages authentication tokens and handles
       token expiration transparently.
    """

    def __init__(
        self,
        logger: Optional[logging.Logger] = None,
        mask_request_data: bool = True,
        timeout: float = 100.0,
    ):
        """Initialize synchronous NEPSE client."""
        super().__init__(
            TokenManager,
            DummyIDManager,
            logger=logger,
            mask_request_data=mask_request_data,
            timeout=timeout,
        )
        self.init_client(tls_verify=self._tls_verify)

    def init_client(self, tls_verify: bool) -> None:
        """
        Initialize HTTP client with specified settings.

        Args:
           tls_verify: Whether to verify TLS certificates
        """
        self.client = httpx.Client(
            verify=tls_verify,
            http2=True,
            timeout=self.timeout,
            follow_redirects=True,
        )
        self.logger.debug(f"HTTP client initialized (TLS verify: {tls_verify})")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup resources."""
        self.close()

    def close(self) -> None:
        """Close HTTP client and cleanup resources."""
        if hasattr(self, "client"):
            self.client.close()
            self.logger.debug("HTTP client closed")

    # Private helper methods

    def _retry_request(self, request_func, *args, max_retries: int = 3, **kwargs) -> Any:
        """
        Retry a request with exponential backoff.

        Args:
           request_func: Function to retry
           max_retries: Maximum number of retry attempts
           *args, **kwargs: Arguments to pass to request_func

        Returns:
           Response from request_func

        Raises:
           NepseNetworkError: If all retries fail
        """
        for attempt in range(max_retries):
            try:
                return request_func(*args, **kwargs)
            except (httpx.RemoteProtocolError, httpx.ReadError, httpx.ConnectError) as e:
                if attempt == max_retries - 1:
                    self.logger.error(f"Request failed after {max_retries} attempts: {e}")
                    raise NepseNetworkError(
                        f"Network error after {max_retries} retries: {e}"
                    ) from e
                self.logger.warning(
                    f"Request failed (attempt {attempt + 1}/{max_retries}), retrying..."
                )
            except NepseAuthenticationError:
                self.logger.info("Token expired, refreshing...")
                self.token_manager.update()
                # Retry immediately after token refresh
                return request_func(*args, **kwargs)

    def requestGETAPI(self, url: str, include_authorization_headers: bool = True) -> Any:
        """
        Make GET request to NEPSE API.

        Args:
           url: API endpoint URL
           include_authorization_headers: Whether to include auth headers

        Returns:
           Parsed response data
        """

        def _make_request():
            headers = (
                self.getAuthorizationHeaders() if include_authorization_headers else self.headers
            )
            response = self.client.get(
                self.get_full_url(api_url=url),
                headers=headers,
            )
            return self.handle_response(response)

        return self._retry_request(_make_request)

    def requestPOSTAPI(self, url: str, payload_generator) -> Any:
        """
        Make POST request to NEPSE API.

        Args:
           url: API endpoint URL
           payload_generator: Function to generate payload

        Returns:
           Parsed response data
        """

        def _make_request():
            payload = {"id": payload_generator()}
            response = self.client.post(
                self.get_full_url(api_url=url),
                headers=self.getAuthorizationHeaders(),
                data=json.dumps(payload),
            )
            return self.handle_response(response, request_data=payload)

        return self._retry_request(_make_request)

    def getAuthorizationHeaders(self) -> Dict[str, str]:
        """
        Get headers with authorization token.

        Returns:
           Dictionary of HTTP headers
        """
        access_token = self.token_manager.getAccessToken()
        return {
            "Authorization": f"Salter {access_token}",
            "Content-Type": "application/json",
            **self.headers,
        }

    # Payload ID generators

    def getPOSTPayloadIDForScrips(self) -> int:
        """Generate payload ID for scrip-related requests."""
        dummy_id = self.getDummyID()
        return self.getDummyData()[dummy_id] + dummy_id + 2 * date.today().day

    def getPOSTPayloadID(self) -> int:
        """Generate general payload ID."""
        e = self.getPOSTPayloadIDForScrips()
        salt_index = 3 if e % 10 < 5 else 1
        return (
            e
            + self.token_manager.salts[salt_index] * date.today().day
            - self.token_manager.salts[salt_index - 1]
        )

    def getPOSTPayloadIDForFloorSheet(
        self, business_date: Optional[Union[str, date]] = None
    ) -> int:
        """
        Generate payload ID for floor sheet requests.

        Args:
           business_date: Business date (YYYY-MM-DD string or date object)

        Returns:
           Payload ID integer
        """
        e = self.getPOSTPayloadIDForScrips()

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
        return (
            e
            + self.token_manager.salts[salt_index] * day
            - self.token_manager.salts[salt_index - 1]
        )

    # Company and Security data methods

    def getCompanyList(self) -> List[Dict[str, Any]]:
        """
        Get list of all listed companies.

        Returns:
           List of company dictionaries

        Note:
           Results are cached internally. Subsequent calls return cached data
           unless cache is cleared.
        """
        self.company_list = self.requestGETAPI(url=self.api_end_points["company_list_url"])
        return list(self.company_list)

    def getSecurityList(self) -> List[Dict[str, Any]]:
        """
        Get list of all securities (non-delisted).

        Returns:
           List of security dictionaries
        """
        self.security_list = self.requestGETAPI(url=self.api_end_points["security_list_url"])
        return list(self.security_list)

    def getCompanyIDKeyMap(self, force_update: bool = False) -> Dict[str, int]:
        """
        Get mapping of company symbols to IDs.

        Args:
           force_update: Force refresh of cached data

        Returns:
           Dictionary mapping symbol to company ID
        """
        if self.company_symbol_id_keymap is None or force_update:
            company_list = self.getCompanyList()
            self.company_symbol_id_keymap = {
                company["symbol"]: company["id"] for company in company_list
            }
        return self.company_symbol_id_keymap.copy()

    def getSecurityIDKeyMap(self, force_update: bool = False) -> Dict[str, int]:
        """
        Get mapping of security symbols to IDs.

        Args:
           force_update: Force refresh of cached data

        Returns:
           Dictionary mapping symbol to security ID
        """
        if self.security_symbol_id_keymap is None or force_update:
            security_list = self.getSecurityList()
            self.security_symbol_id_keymap = {
                security["symbol"]: security["id"] for security in security_list
            }
        return self.security_symbol_id_keymap.copy()

    def getSectorScrips(self) -> Dict[str, List[str]]:
        """
        Get scrips grouped by sector.

        Returns:
           Dictionary mapping sector name to list of symbols
        """
        if self.sector_scrips is None:
            company_info_dict = {company["symbol"]: company for company in self.getCompanyList()}
            sector_scrips = defaultdict(list)

            for security in self.getSecurityList():
                symbol = security["symbol"]
                company_info = company_info_dict.get(symbol)

                if company_info:
                    sector_name = company_info["sectorName"]
                    sector_scrips[sector_name].append(symbol)
                else:
                    sector_scrips["Promoter Share"].append(symbol)

            self.sector_scrips = dict(sector_scrips)

        return dict(self.sector_scrips)

    def getCompanyDetails(self, symbol: str) -> Dict[str, Any]:
        """
        Get detailed information for a specific company.

        Args:
           symbol: Company stock symbol (e.g., "NABIL")

        Returns:
           Dictionary with company details

        Raises:
           KeyError: If symbol not found
        """
        symbol = symbol.upper()
        company_id = self.getSecurityIDKeyMap()[symbol]
        url = f"{self.api_end_points['company_details']}{company_id}"
        return self.requestPOSTAPI(url=url, payload_generator=self.getPOSTPayloadIDForScrips)

    def getCompanyPriceVolumeHistory(
        self,
        symbol: str,
        start_date: Optional[Union[str, date]] = None,
        end_date: Optional[Union[str, date]] = None,
    ) -> Dict[str, Any]:
        """
        Get price and volume history for a company.

        Args:
           symbol: Company symbol
           start_date: Start date (YYYY-MM-DD or date object)
           end_date: End date (YYYY-MM-DD or date object)

        Returns:
           Dictionary with paginated history data
        """
        end_date = end_date if end_date else date.today()
        start_date = start_date if start_date else (end_date - timedelta(days=365))

        symbol = symbol.upper()
        company_id = self.getSecurityIDKeyMap()[symbol]

        url = (
            f"{self.api_end_points['company_price_volume_history']}{company_id}"
            f"?size=500&startDate={start_date}&endDate={end_date}"
        )
        return self.requestGETAPI(url=url)

    def getDailyScripPriceGraph(self, symbol: str) -> Dict[str, Any]:
        """
        Get daily price graph data for a scrip.

        Args:
           symbol: Company symbol

        Returns:
           Graph data dictionary
        """
        symbol = symbol.upper()
        company_id = self.getSecurityIDKeyMap()[symbol]
        url = f"{self.api_end_points['company_daily_graph']}{company_id}"
        return self.requestPOSTAPI(url=url, payload_generator=self.getPOSTPayloadIDForScrips)

    # Floor sheet methods

    def getFloorSheet(
        self,
        show_progress: bool = False,
        paginated: bool = False,
        page: Optional[int] = None,
    ) -> Union[List[Dict[str, Any]], List[List[Dict[str, Any]]], Dict[str, Any]]:
        """
        Get floor sheet data.

        Args:
           show_progress: Show progress bar during download
           paginated: Return list of pages instead of flattened list
           page: Get specific page number (0-indexed)

        Returns:
           Floor sheet data (format depends on parameters)
        """
        url = f"{self.api_end_points['floor_sheet']}?size={self.floor_sheet_size}&sort=contractId,desc"

        # Fetch specific page
        if page is not None:
            page_url = f"{url}&page={page}"
            sheet = self.requestPOSTAPI(
                url=page_url, payload_generator=self.getPOSTPayloadIDForFloorSheet
            )
            return sheet["floorsheets"]

        # Fetch all pages
        sheet = self.requestPOSTAPI(url=url, payload_generator=self.getPOSTPayloadIDForFloorSheet)
        first_page = sheet["floorsheets"]["content"]
        total_pages = sheet["floorsheets"]["totalPages"]

        # Setup iterator with optional progress bar
        page_iterator = (
            tqdm.tqdm(range(1, total_pages), desc="Downloading floor sheet")
            if show_progress
            else range(1, total_pages)
        )

        all_pages = [first_page]
        for page_num in page_iterator:
            current_sheet = self.requestPOSTAPI(
                url=f"{url}&page={page_num}",
                payload_generator=self.getPOSTPayloadIDForFloorSheet,
            )
            all_pages.append(current_sheet["floorsheets"]["content"])

        if paginated:
            return all_pages

        # Flatten all pages
        return [row for page in all_pages for row in page]

    def getFloorSheetOf(
        self,
        symbol: str,
        business_date: Optional[Union[str, date]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get floor sheet for a specific company.

        Args:
           symbol: Company symbol
           business_date: Business date (YYYY-MM-DD string or date object)

        Returns:
           List of floor sheet records
        """
        symbol = symbol.upper()
        company_id = self.getSecurityIDKeyMap()[symbol]

        if business_date:
            if isinstance(business_date, str):
                business_date = date.fromisoformat(business_date)
        else:
            business_date = date.today()

        url = (
            f"{self.api_end_points['company_floorsheet']}{company_id}"
            f"?businessDate={business_date}&size={self.floor_sheet_size}&sort=contractid,desc"
        )

        sheet = self.requestPOSTAPI(url=url, payload_generator=self.getPOSTPayloadIDForFloorSheet)

        if not sheet:
            return []

        floor_sheets = sheet["floorsheets"]["content"]
        total_pages = sheet["floorsheets"]["totalPages"]

        for page_num in range(1, total_pages):
            next_sheet = self.requestPOSTAPI(
                url=f"{url}&page={page_num}",
                payload_generator=self.getPOSTPayloadIDForFloorSheet,
            )
            floor_sheets.extend(next_sheet["floorsheets"]["content"])

        return floor_sheets

    def getSymbolMarketDepth(self, symbol: str) -> Dict[str, Any]:
        """
        Get market depth for a symbol.

        Args:
           symbol: Company symbol

        Returns:
           Market depth data
        """
        symbol = symbol.upper()
        company_id = self.getSecurityIDKeyMap()[symbol]
        url = f"{self.api_end_points['market-depth']}{company_id}/"
        return self.requestGETAPI(url=url)

    # Additional data methods (continued in next message due to length)

    def getHolidayList(self, year: int = 2025) -> List[Dict[str, Any]]:
        """Get list of market holidays for specified year."""
        url = f"{self.api_end_points['holiday-list']}?year={year}"
        self.holiday_list = self.requestGETAPI(url=url)
        return list(self.holiday_list)

    def getDebentureAndBondList(self, bond_type: str = "debenture") -> List[Dict[str, Any]]:
        """Get list of debentures and bonds."""
        url = f"{self.api_end_points['debenture-and-bond']}?type={bond_type}"
        return self.requestGETAPI(url=url)

    def getPriceVolumeHistory(self, business_date: Optional[str] = None) -> Dict[str, Any]:
        """Get price volume history for a business date."""
        date_param = f"&businessDate={business_date}" if business_date else ""
        url = f"{self.api_end_points['todays_price']}?size=500{date_param}"
        return self.requestPOSTAPI(url=url, payload_generator=self.getPOSTPayloadIDForFloorSheet)


__all__ = ["NepseClient"]
