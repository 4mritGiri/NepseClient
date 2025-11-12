"""
Synchronous NEPSE client implementation.

This module provides a blocking, synchronous interface to the NEPSE API,
suitable for scripts, notebooks, and applications that don't require concurrency.
"""

import logging
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any, Optional, Union, cast

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
                self.logger.warning(
                    f"Request failed (attempt {attempt + 1}/{max_retries}), retrying..."
                )
            except NepseAuthenticationError:
                self.logger.info("Token expired, refreshing...")
                self.token_manager.update()
                # Retry immediately after token refresh
                return request_func(*args, **kwargs)

    def _build_query_params(self, **kwargs) -> str:
        """Helper function to build query parameters string.

        Args:
            **kwargs: Key-value pairs for query parameters

        Returns:
            str: Query string with non-None values
        """
        params = []
        for key, value in kwargs.items():
            print(key, value)
            if value is not None:
                params.append(f"{key}={value}")
        return "&".join(params)

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
                self.getAuthorizationHeaders()
                if include_authorization_headers
                else {**self.headers, "User-Agent": self.get_random_user_agent()}
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
                json=payload,
                # data=payload,
            )
            return self.handle_response(response, request_data=payload)

        return self._retry_request(_make_request)

    def getAuthorizationHeaders(self) -> dict[str, str]:
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
            "User-Agent": self.get_random_user_agent(),
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
        return int(
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
        return int(
            e
            + self.token_manager.salts[salt_index] * day
            - self.token_manager.salts[salt_index - 1]
        )

    # Company and Security data methods

    def getCompanyList(self) -> list[dict[str, Any]]:
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

    def getSecurityList(self) -> list[dict[str, Any]]:
        """
        Get list of all securities (non-delisted).

        Returns:
           List of security dictionaries
        """
        self.security_list = self.requestGETAPI(url=self.api_end_points["security_list_url"])
        return list(self.security_list)

    def getCompanyIDKeyMap(self, force_update: bool = False) -> dict[str, int]:
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

    def getSecurityIDKeyMap(self, force_update: bool = False) -> dict[str, int]:
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

    def getSectorScrips(self) -> dict[str, list[str]]:
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

    def getCompanyDetails(self, symbol: str) -> dict[str, Any]:
        """
        Get detailed information for a specific company.

        Args:
           symbol: Company stock symbol (e.g., "NABIL")

        Returns:
           Dictionary with company details

        Raises:
           KeyError: If symbol not found
        """
        if symbol is None:
            raise NepseValidationError("symbol is required", field="symbol")
        symbol = symbol.upper()
        company_id = self.getSecurityIDKeyMap()[symbol]
        url = f"{self.api_end_points['company_details']}{company_id}"
        return cast(
            dict[str, Any],
            self.requestPOSTAPI(url=url, payload_generator=self.getPOSTPayloadIDForScrips),
        )

    def getCompanyFinancialDetails(self, company_id: Optional[str] = None) -> list[dict[str, Any]]:
        """
        Get financial details for a specific company.

        Args:
            company_id (str, optional): The unique identifier for the company.
                                        If not provided, the behavior depends on
                                        the API endpoint's default or requirements.

        Returns:
            list: A list of dictionaries containing financial details for the company.
                Each dictionary might include keys like 'period', 'financialMetrics',
                'applicationDocumentDetailsList', etc., as returned by the API.
                Returns an empty list if no data is found or an error occurs
                during the API request or processing.

                The 'applicationDocumentDetailsList' within each item may be
                augmented with 'fullFilePath' and 'fullEncryptedPath' keys for
        """
        url = f"{self.api_end_points['company-financial']}/{company_id}"

        data = list(self.requestGETAPI(url=url) or [])
        base_file_url = self.get_full_url(self.api_end_points["application-fetch-files"])
        base_sec_file_url = self.get_full_url(self.api_end_points["fetch-security-files"])

        for item in data:
            try:
                application_doc_list = item.get("applicationDocumentDetailsList", [])

                if not isinstance(application_doc_list, list):
                    continue

                for doc in application_doc_list:
                    encrypted_id = doc.get("encryptedId")
                    file_path = doc.get("filePath")
                    if file_path:
                        doc["fullFilePath"] = f"{base_sec_file_url}{file_path}"
                    if encrypted_id:
                        doc["fullEncryptedPath"] = f"{base_file_url}{encrypted_id}"
            except (AttributeError, TypeError, KeyError):
                continue

        return data

    def getCompanyAGM(self, company_id: Optional[str] = None) -> list[dict[str, Any]]:
        """
        Get Annual General Meeting (AGM) information for a specific company.

        Args:
            company_id (str, optional): The unique identifier for the company.
                                        If not provided, the behavior depends on
                                        the API endpoint's default or requirements.

        Returns:
            list: A list of dictionaries containing AGM details for the company.
                Each dictionary might include keys like 'meetingDate', 'agenda',
                'applicationDocumentDetailsList', etc., as returned by the API.
                Returns an empty list if no data is found or an error occurs
                during the API request or processing.

                The 'applicationDocumentDetailsList' within each item may be
                augmented with a 'fullFilePath' key for document access.
        """
        url = f"{self.api_end_points['company-agm']}/{company_id}"

        data = list(self.requestGETAPI(url=url) or [])
        base_file_url = self.get_full_url(self.api_end_points["application-fetch-files"])

        for item in data:
            try:
                application_doc_list = item.get("applicationDocumentDetailsList", [])

                if not isinstance(application_doc_list, list):
                    continue

                for doc in application_doc_list:
                    encrypted_id = doc.get("encryptedId")
                    if encrypted_id:
                        doc["fullFilePath"] = f"{base_file_url}{encrypted_id}"
            except (AttributeError, TypeError, KeyError):
                continue

        return data

    def getCompanyDividend(self, company_id: Optional[str] = None) -> list[dict[str, Any]]:
        """
        Get dividend information for a specific company.

        Args:
            company_id (str, optional): The unique identifier for the company.
                                        If not provided, the behavior depends on
                                        the API endpoint's default or requirements.

        Returns:
            list: A list of dictionaries containing dividend details for the company.
                Each dictionary might include keys like 'dividendType', 'rate',
                'applicationDocumentDetailsList', etc., as returned by the API.
                Returns an empty list if no data is found or an error occurs
                during the API request or processing.

                The 'applicationDocumentDetailsList' within each item may be
                augmented with a 'fullFilePath' key for document access.
        """
        url = f"{self.api_end_points['company-dividend']}/{company_id}"

        data = list(self.requestGETAPI(url=url) or [])
        base_file_url = self.get_full_url(self.api_end_points["application-fetch-files"])

        for item in data:
            try:
                application_doc_list = item.get("applicationDocumentDetailsList", [])

                if not isinstance(application_doc_list, list):
                    continue

                for doc in application_doc_list:
                    encrypted_id = doc.get("encryptedId")
                    if encrypted_id:
                        doc["fullFilePath"] = f"{base_file_url}{encrypted_id}"
            except (AttributeError, TypeError, KeyError):
                continue

        return data

    def getCompanyMarketDepth(self, company_id: Optional[str] = None) -> list[dict[str, Any]]:
        """
        Get market depth information for a specific company.

        Market depth typically includes buy and sell orders at various price levels.

        Args:
            company_id (str, optional): The unique identifier (symbol or code)
                                        for the company/security.
                                        If not provided, the behavior depends on
                                        the API endpoint's default or requirements.

        Returns:
            list: A list containing market depth data for the company.
                The structure of the data depends on the API response,
                but it usually includes buy/sell orders with prices and volumes.
                Returns an empty list if no data is found or an error occurs
                during the API request.
        """
        url = f"{self.api_end_points['company-market-depth']}/{company_id}"
        data = self.requestGETAPI(url=url) or []
        return data

    def getCompanyPriceVolumeHistory(
        self,
        symbol: str,
        start_date: Optional[Union[str, date]] = None,
        end_date: Optional[Union[str, date]] = None,
    ) -> dict[str, Any]:
        """
        Get price and volume history for a company.

        Args:
           symbol: Company symbol
           start_date: Start date (YYYY-MM-DD or date object)
           end_date: End date (YYYY-MM-DD or date object)

        Returns:
           Dictionary with paginated history data
        """
        # Default end_date to today
        if end_date is None:
            end_date_date = date.today()
        elif isinstance(end_date, str):
            end_date_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        else:
            end_date_date = end_date  # already a date

        # Default start_date to one year before end_date
        if start_date is None:
            start_date_date = end_date_date - timedelta(days=365)
        elif isinstance(start_date, str):
            start_date_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        else:
            start_date_date = start_date

        symbol = symbol.upper()
        company_id = self.getSecurityIDKeyMap()[symbol]

        url = (
            f"{self.api_end_points['company_price_volume_history']}{company_id}"
            f"?size=500&startDate={start_date_date}&endDate={end_date_date}"
        )
        result = self.requestGETAPI(url=url)
        assert isinstance(result, dict)
        return result

    def getDailyScripPriceGraph(self, symbol: str) -> dict[str, Any]:
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
        return cast(
            dict[str, Any],
            self.requestPOSTAPI(url=url, payload_generator=self.getPOSTPayloadIDForScrips),
        )

    # Floor sheet methods

    def getFloorSheet(
        self,
        show_progress: bool = False,
        paginated: bool = False,
        page: Optional[int] = None,
    ) -> Union[list[dict[str, Any]], list[list[dict[str, Any]]], dict[str, Any]]:
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
            return cast(
                Union[list[dict[str, Any]], list[list[dict[str, Any]]], dict[str, Any]],
                sheet["floorsheets"],
            )

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
        size: int = 500,
    ) -> list[dict[str, Any]]:
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

        query_string = self._build_query_params(
            businessDate=business_date, size=size or self.floor_sheet_size
        )
        url = f"{self.api_end_points['company_floorsheet']}{company_id}?{query_string}&sort=contractid,desc"

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

        return cast(list[dict[str, Any]], floor_sheets)

    def getSymbolMarketDepth(self, symbol: str) -> dict[str, Any]:
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
        return cast(dict[str, Any], self.requestGETAPI(url=url))

    # Additional data methods (continued in next message due to length)

    def getHolidayList(self, year: int = 2025) -> list[dict[str, Any]]:
        """Get list of market holidays for specified year."""
        query_string = self._build_query_params(year=year)
        url = f"{self.api_end_points['holiday-list']}?{query_string}"
        self.holiday_list = self.requestGETAPI(url=url)
        return list(self.holiday_list)

    def getDebentureAndBondList(self, bond_type: str = "debenture") -> list[dict[str, Any]]:
        """Get list of debentures and bonds."""
        query_string = self._build_query_params(type=bond_type)
        url = f"{self.api_end_points['debenture-and-bond']}?{query_string}"
        return cast(list[dict[str, Any]], self.requestGETAPI(url=url))

    def _process_news_item(
        self, item: dict, base_file_url: str, strip_tags_func, field_name: str, is_strip_tags: bool
    ) -> dict:
        """Helper function to process individual news items."""
        processed_item = item.copy()
        file_path = processed_item.get("filePath")

        if is_strip_tags and processed_item.get(field_name):
            processed_item[field_name] = strip_tags_func(processed_item[field_name])

        if file_path:
            processed_item["fullFilePath"] = f"{base_file_url}{file_path}"

        return processed_item

    def _validate_pagination_params(self, page: int, page_size: int) -> tuple[int, int]:
        """Validate and normalize pagination parameters."""
        try:
            page = int(page)
            page_size = int(page_size)
        except (ValueError, TypeError):
            print("Invalid page or page_size provided, defaulting to page 1, size 100.")
            page = 1
            page_size = 100

        page = max(1, page)
        page_size = max(1, page_size)

        return page, page_size

    def _calculate_pagination(self, processed_data: list, page: int, page_size: int) -> dict:
        """Calculate pagination metadata."""
        total_count = len(processed_data)
        total_pages = (total_count + page_size - 1) // page_size
        page = min(page, total_pages) if total_pages > 0 else 1

        start_index = (page - 1) * page_size
        end_index = start_index + page_size

        paginated_results = (
            [] if start_index >= total_count else processed_data[start_index:end_index]
        )

        return {
            "paginated_results": paginated_results,
            "total_pages": total_pages,
            "next_page": page + 1 if page < total_pages else None,
            "previous_page": page - 1 if page > 1 else None,
        }

    def getCompanyNewsList(
        self, page: int = 0, page_size: int = 100, is_strip_tags: bool = True
    ) -> dict[str, Any]:
        """Get list of company news."""
        from django.utils.html import strip_tags

        url = self.api_end_points["company-news"]
        raw_data = self.requestGETAPI(url=url) or []

        if not isinstance(raw_data, list):
            print(
                f"Warning: API response is not a list. Type: {type(raw_data)}. Attempting to convert."
            )
            try:
                raw_data = list(raw_data)
            except (TypeError, ValueError):
                print("Error: Could not convert API response to list. Returning empty results.")
                raw_data = []

        base_file_url = self.get_full_url(self.api_end_points["fetch-security-files"])
        processed_data = [
            self._process_news_item(item, base_file_url, strip_tags, "newsBody", is_strip_tags)
            for item in raw_data
            if isinstance(item, dict)
        ]

        total_count = len(processed_data)
        if total_count == 0:
            return {
                "results": [],
                "count": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "next_page": None,
                "previous_page": None,
            }

        page, page_size = self._validate_pagination_params(page, page_size)
        pagination = self._calculate_pagination(processed_data, page, page_size)

        return {
            "results": pagination["paginated_results"],
            "count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": pagination["total_pages"],
            "next_page": pagination["next_page"],
            "previous_page": pagination["previous_page"],
            "params": ["page: number", "pageSize: number", "isStripTags: bool"],
        }

    def getNewsAndAlertList(
        self, page: int = 0, page_size: int = 100, is_strip_tags: bool = True
    ) -> dict[str, Any]:
        """Get list of News and Alert."""
        from django.utils.html import strip_tags

        url = self.api_end_points["news-alerts"]
        raw_data = self.requestGETAPI(url=url) or []

        if not isinstance(raw_data, list):
            print(
                f"Warning: API response is not a list. Type: {type(raw_data)}. Attempting to convert."
            )
            try:
                raw_data = list(raw_data)
            except (TypeError, ValueError):
                print("Error: Could not convert API response to list. Returning empty results.")
                raw_data = []

        base_file_url = self.get_full_url(self.api_end_points["fetch-security-files"])
        processed_data = [
            self._process_news_item(item, base_file_url, strip_tags, "messageBody", is_strip_tags)
            for item in raw_data
            if isinstance(item, dict)
        ]

        total_count = len(processed_data)
        if total_count == 0:
            return {
                "results": [],
                "count": 0,
                "page": page,
                "page_size": page_size,
                "total_pages": 0,
                "next": None,
                "previous": None,
            }

        page, page_size = self._validate_pagination_params(page, page_size)
        pagination = self._calculate_pagination(processed_data, page, page_size)

        return {
            "results": pagination["paginated_results"],
            "count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": pagination["total_pages"],
            "next": pagination["next_page"],
            "previous": pagination["previous_page"],
            "params": ["page: number", "pageSize: number", "isStripTags: bool"],
        }

    def getPressRelease(self, page: int = 0, size: int = 20) -> dict[str, Any]:
        """Get list of Press release.

        Args:
            page (int, optional): _description_. Defaults to None.
            size (int, optional): _description_. Defaults to 20.

        Returns:
            dict[str, Any]: Response containing press releases with full file paths
        """
        query_string = self._build_query_params(page=page, size=size)
        url = f"{self.api_end_points['press-release']}?{query_string}"
        data = self.requestGETAPI(url=url)

        base_file_url = self.get_full_url(self.api_end_points["fetch-files"])

        # Handle nested list structure in content
        for item_list in data.get("content", []):
            if isinstance(item_list, list):
                for item in item_list:
                    if isinstance(item, dict):
                        file_path = item.get("noticeFilePath")
                        if file_path:
                            item["fullFilePath"] = f"{base_file_url}{file_path}"

        return cast(dict[str, Any], data)

    def getNepseNotice(self, page: int = 0, size: int = 10) -> dict[str, Any]:
        """Get NEPSE Notice data.

        Args:
            page (int, optional): _description_. Defaults to 0.
            size (int, optional): _description_. Defaults to 10.

        Returns:
            dict[str, Any]: _description_
        """
        query_string = self._build_query_params(page=page, size=size)
        url = f"{self.api_end_points['nepse-notice']}?{query_string}"

        data = self.requestGETAPI(url=url) or []
        base_file_url = self.get_full_url(self.api_end_points["fetch-files"])

        for item in data:
            try:
                content = item.get("content", {})
                file_path = content.get("noticeFilePath")
                if file_path:
                    item.setdefault("content", {})[
                        "fullNoticeFilePath"
                    ] = f"{base_file_url}{file_path}"
            except (AttributeError, TypeError):
                continue

        return cast(dict[str, Any], data)

    def getPriceVolumeHistory(self, business_date: Optional[str] = None) -> dict[str, Any]:
        """Get price volume history for a business date."""
        date_param = f"&businessDate={business_date}" if business_date else ""
        url = f"{self.api_end_points['todays_price']}?size=500{date_param}"
        response = self.requestPOSTAPI(
            url=url, payload_generator=self.getPOSTPayloadIDForFloorSheet
        )
        return cast(dict[str, Any], response)

    def getDailyNepseIndexGraph(self) -> list[Any]:
        """Get price volume history for a business date."""
        response = self.requestPOSTAPI(
            url=self.api_end_points["nepse_index_daily_graph"],
            payload_generator=self.getPOSTPayloadID,
        )
        return cast(list[Any], response)

    def getDailySensitiveIndexGraph(self) -> list[Any]:
        """Get NEPSE Daily Sensitive Index Graph.

        Returns:
            list[Any]: _description_
        """
        return cast(
            list[Any],
            self.requestPOSTAPI(
                url=self.api_end_points["sensitive_index_daily_graph"],
                payload_generator=self.getPOSTPayloadID,
            ),
        )

    def getDailyFloatIndexGraph(self) -> list[Any]:
        """Get NEPSE Daily Float Index Graph Data.

        Returns:
            list[Any]: _description_
        """
        return cast(
            list[Any],
            self.requestPOSTAPI(
                url=self.api_end_points["float_index_daily_graph"],
                payload_generator=self.getPOSTPayloadID,
            ),
        )

    def getDailySensitiveFloatIndexGraph(self) -> list[Any]:
        """Get NEPSE Daily Sensitive Float Index Graph Data.

        Returns:
            list[Any]: _description_
        """
        return cast(
            list[Any],
            self.requestPOSTAPI(
                url=self.api_end_points["sensitive_float_index_daily_graph"],
                payload_generator=self.getPOSTPayloadID,
            ),
        )

    def getDailyBankSubindexGraph(self) -> list[Any]:
        """Get NEPSE Daily Bank Subindex Graph Data.

        Returns:
            list[Any]: _description_
        """
        return cast(
            list[Any],
            self.requestPOSTAPI(
                url=self.api_end_points["banking_sub_index_graph"],
                payload_generator=self.getPOSTPayloadID,
            ),
        )

    def getDailyDevelopmentBankSubindexGraph(self) -> list[Any]:
        """Get NEPSE Development Bank Subindex Graph Data.

        Returns:
            list[Any]: _description_
        """
        return cast(
            list[Any],
            self.requestPOSTAPI(
                url=self.api_end_points["development_bank_sub_index_graph"],
                payload_generator=self.getPOSTPayloadID,
            ),
        )

    def getDailyFinanceSubindexGraph(self) -> list[Any]:
        """Get NEPSE Daily Finance Subindex Graph Data.

        Returns:
            list[Any]: _description_
        """
        return cast(
            list[Any],
            self.requestPOSTAPI(
                url=self.api_end_points["finance_sub_index_graph"],
                payload_generator=self.getPOSTPayloadID,
            ),
        )

    def getDailyHotelTourismSubindexGraph(self) -> list[Any]:
        """Gat NEPSE Daily Hotel Tourism Subindex Graph Data.

        Returns:
            list[Any]: _description_
        """
        return cast(
            list[Any],
            self.requestPOSTAPI(
                url=self.api_end_points["hotel_tourism_sub_index_graph"],
                payload_generator=self.getPOSTPayloadID,
            ),
        )

    def getDailyHydroSubindexGraph(self) -> list[Any]:
        """Get NEPSE Daily Hydro Subindex Graph Data.

        Returns:
            list[Any]: _description_
        """
        return cast(
            list[Any],
            self.requestPOSTAPI(
                url=self.api_end_points["hydro_sub_index_graph"],
                payload_generator=self.getPOSTPayloadID,
            ),
        )

    def getDailyInvestmentSubindexGraph(self) -> list[Any]:
        """Get NEPSE Daily Investment Subindex Graph Data.

        Returns:
            list[Any]: _description_
        """
        return cast(
            list[Any],
            self.requestPOSTAPI(
                url=self.api_end_points["investment_sub_index_graph"],
                payload_generator=self.getPOSTPayloadID,
            ),
        )

    def getDailyLifeInsuranceSubindexGraph(self) -> list[Any]:
        """Get NEPSE Daily Life Insurance Subindex Graph Data.

        Returns:
            list[Any]: _description_
        """
        return cast(
            list[Any],
            self.requestPOSTAPI(
                url=self.api_end_points["life_insurance_sub_index_graph"],
                payload_generator=self.getPOSTPayloadID,
            ),
        )

    def getDailyManufacturingSubindexGraph(self) -> list[Any]:
        """Get NEPSE Daily Manufacturing Subindex Graph Data.

        Returns:
            list[Any]: _description_
        """
        return cast(
            list[Any],
            self.requestPOSTAPI(
                url=self.api_end_points["manufacturing_sub_index_graph"],
                payload_generator=self.getPOSTPayloadID,
            ),
        )

    def getDailyMicrofinanceSubindexGraph(self) -> list[Any]:
        """Get NEPSE Daily Microfinance Subindex Graph Data.

        Returns:
            list[Any]: _description_
        """
        return cast(
            list[Any],
            self.requestPOSTAPI(
                url=self.api_end_points["microfinance_sub_index_graph"],
                payload_generator=self.getPOSTPayloadID,
            ),
        )

    def getDailyMutualfundSubindexGraph(self) -> list[Any]:
        """Get NEPSE Daily Mutual Fund Subindex Graph Data.

        Returns:
            list[Any]: _description_
        """
        return cast(
            list[Any],
            self.requestPOSTAPI(
                url=self.api_end_points["mutual_fund_sub_index_graph"],
                payload_generator=self.getPOSTPayloadID,
            ),
        )

    def getDailyNonLifeInsuranceSubindexGraph(self) -> list[Any]:
        """Get NEPSE Daily Non Life Insurance Subindex Graph data.

        Returns:
            list[Any]: _description_
        """
        return cast(
            list[Any],
            self.requestPOSTAPI(
                url=self.api_end_points["non_life_insurance_sub_index_graph"],
                payload_generator=self.getPOSTPayloadID,
            ),
        )

    def getDailyOthersSubindexGraph(self) -> list[Any]:
        """Get NEPSE Daily Other Subindex Graph Data.

        Returns:
            list[Any]: _description_
        """
        return cast(
            list[Any],
            self.requestPOSTAPI(
                url=self.api_end_points["others_sub_index_graph"],
                payload_generator=self.getPOSTPayloadID,
            ),
        )

    def getDailyTradingSubindexGraph(self) -> list[Any]:
        """Get NEPSE Daily Trading Subindex Graph Data.

        Returns:
            list[Any]: _description_
        """
        return cast(
            list[Any],
            self.requestPOSTAPI(
                url=self.api_end_points["trading_sub_index_graph"],
                payload_generator=self.getPOSTPayloadID,
            ),
        )


__all__ = ["NepseClient"]
