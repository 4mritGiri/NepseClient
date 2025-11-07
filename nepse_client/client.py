"""
Base client implementation for NEPSE API.

This module provides the foundation for both sync and async clients,
including common utilities, configuration loading, and response handling.
"""

import json
import logging
import pathlib
from datetime import datetime
from functools import singledispatch
from typing import Any, Dict, List, Optional, Type, Union

from .exceptions import (
    NepseAuthenticationError,
    NepseBadGatewayError,
    NepseClientError,
    NepseConfigurationError,
    NepseNetworkError,
    NepseServerError,
)


# Configure module logger
logger = logging.getLogger(__name__)


def mask_sensitive_data(
    data: Dict[str, Any], keys: tuple = ("token", "password", "Authorization")
) -> Dict[str, Any]:
    """
    Mask sensitive fields in data for safe logging.

    Args:
        data: Dictionary containing potentially sensitive data
        keys: Tuple of keys to mask

    Returns:
        Dictionary with masked sensitive values
    """
    masked = data.copy()
    for key in keys:
        if key in masked:
            masked[key] = "***MASKED***"
    return masked


@singledispatch
def safe_serialize(obj: Any) -> Union[str, Dict, List]:
    """
    Safely serialize objects for logging.

    Args:
        obj: Object to serialize

    Returns:
        Serialized representation
    """
    try:
        return str(obj)
    except Exception:
        return "<unserializable>"


@safe_serialize.register(dict)
def _(obj: Dict) -> str:
    """Serialize dictionary to JSON string."""
    return json.dumps(obj, default=safe_serialize)


@safe_serialize.register(list)
def _(obj: List) -> List:
    """Serialize list recursively."""
    return [safe_serialize(item) for item in obj]


class _NepseBase:
    """
    Base class for NEPSE client implementations.

    This class provides common functionality for both sync and async clients,
    including configuration loading, request handling, and response processing.

    Args:
        token_manager_class: Token manager class (sync or async)
        dummy_id_manager_class: Dummy ID manager class (sync or async)
        logger: Optional custom logger instance
        mask_request_data: Whether to mask sensitive data in logs
        timeout: Request timeout in seconds
    """

    def __init__(
        self,
        token_manager_class: Type,
        dummy_id_manager_class: Type,
        logger: Optional[logging.Logger] = None,
        mask_request_data: bool = True,
        timeout: float = 100.0,
    ):
        """Initialize the base client."""
        # Setup logging
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.mask_request_data = mask_request_data
        self.timeout = timeout

        # Initialize managers
        self.token_manager = token_manager_class(self)
        self.dummy_id_manager = dummy_id_manager_class(
            market_status_function=self.getMarketStatus,
            date_function=datetime.now,
        )

        # TLS verification flag
        self._tls_verify = True

        # Cache variables
        self.company_symbol_id_keymap: Optional[Dict[str, int]] = None
        self.security_symbol_id_keymap: Optional[Dict[str, int]] = None
        self.company_list: Optional[List[Dict]] = None
        self.security_list: Optional[List[Dict]] = None
        self.holiday_list: Optional[List[Dict]] = None
        self.sector_scrips: Optional[Dict[str, List[str]]] = None

        # Configuration
        self.floor_sheet_size = 500
        self.base_url = "https://nepalstock.com.np"

        # Load configuration files
        self._load_configurations()

    def _load_configurations(self) -> None:
        """Load API endpoints, dummy data, and headers from JSON files."""
        data_dir = pathlib.Path(__file__).parent / "data"

        try:
            # Load API endpoints
            self.api_end_points = self._load_json_file(data_dir / "API_ENDPOINTS.json")

            # Load dummy data
            self.dummy_data = self._load_json_file(data_dir / "DUMMY_DATA.json")

            # Load headers
            self.headers = self._load_json_file(data_dir / "HEADERS.json")
            self.headers["Host"] = self.base_url.replace("https://", "")
            self.headers["Referer"] = self.base_url

            self.logger.debug("Configuration files loaded successfully")

        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise NepseConfigurationError(f"Configuration loading failed: {e}") from e

    @staticmethod
    def _load_json_file(filepath: pathlib.Path) -> Union[Dict, List]:
        """
        Load and parse a JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            Parsed JSON data

        Raises:
            NepseConfigurationError: If file cannot be loaded
        """
        try:
            with open(filepath, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError as e:
            raise NepseConfigurationError(f"Configuration file not found: {filepath}") from e
        except json.JSONDecodeError as e:
            raise NepseConfigurationError(f"Invalid JSON in {filepath}: {e}") from e

    def get_full_url(self, api_url: str) -> str:
        """
        Construct full URL from API endpoint.

        Args:
            api_url: API endpoint path

        Returns:
            Complete URL
        """
        return f"{self.base_url}{api_url}"

    def getDummyData(self) -> List[int]:
        """
        Get dummy data array.

        Returns:
            List of dummy integers
        """
        return self.dummy_data

    def getDummyID(self) -> int:
        """
        Get dummy ID for current market state.

        Returns:
            Dummy ID integer

        Note:
            This must be implemented by subclasses (sync/async)
        """
        return self.dummy_id_manager.getDummyID()

    def handle_response(self, response: Any, request_data: Optional[Dict] = None) -> Any:
        """
        Process HTTP response and handle errors.

        Args:
            response: HTTP response object
            request_data: Optional request data for logging

        Returns:
            Parsed response data

        Raises:
            NepseClientError: For 4xx errors
            NepseAuthenticationError: For 401 errors
            NepseBadGatewayError: For 502 errors
            NepseServerError: For 5xx errors
            NepseNetworkError: For unexpected errors
        """
        self.logger.debug(
            f"HTTP {response.request.method} {response.url} - Status: {response.status_code}"
        )

        # Parse response data
        try:
            data = response.json()
        except ValueError:
            data = response.text.strip()

        # Prepare logging context
        log_context = {
            "url": str(response.url),
            "method": response.request.method,
            "status_code": response.status_code,
            "request_headers": dict(response.request.headers),
            "request_body": request_data or getattr(response.request, "body", None),
            "response_body": data,
        }

        # Mask sensitive data if enabled
        if self.mask_request_data and isinstance(log_context["request_body"], dict):
            log_context["request_body"] = mask_sensitive_data(log_context["request_body"])
        if self.mask_request_data and isinstance(log_context["request_headers"], dict):
            log_context["request_headers"] = mask_sensitive_data(log_context["request_headers"])

        # Handle response based on status code
        status_code = response.status_code

        if 200 <= status_code < 300:
            return data

        elif status_code == 400:
            msg = f"Client Error 400: {safe_serialize(data)}"
            self.logger.warning(msg, extra=log_context)
            raise NepseClientError(msg, status_code=status_code, response_data=data)

        elif status_code == 401:
            msg = f"Unauthorized (401): {safe_serialize(data)}"
            self.logger.warning(msg, extra=log_context)
            raise NepseAuthenticationError(msg, status_code=status_code, response_data=data)

        elif status_code == 502:
            msg = f"Bad Gateway (502): {safe_serialize(data)}"
            self.logger.error(msg, exc_info=True, extra=log_context)
            raise NepseBadGatewayError(msg, status_code=status_code, response_data=data)

        elif 500 <= status_code < 600:
            msg = f"Server Error {status_code}: {safe_serialize(data)}"
            self.logger.error(msg, exc_info=True, extra=log_context)
            raise NepseServerError(msg, status_code=status_code, response_data=data)

        else:
            msg = f"Unexpected HTTP status {status_code}: {safe_serialize(data)}"
            self.logger.critical(msg, exc_info=True, extra=log_context)
            raise NepseNetworkError(msg, status_code=status_code, response_data=data)

    # Configuration Methods

    def setTLSVerification(self, flag: bool = False) -> None:
        """
        Enable or disable TLS certificate verification.

        Args:
            flag: True to enable, False to disable

        Warning:
            Disabling TLS verification is insecure and should only be
            used for testing purposes.
        """
        self._tls_verify = flag
        self.init_client(tls_verify=flag)
        self.logger.warning(f"TLS verification set to: {flag}")

    # Abstract methods to be implemented by subclasses

    def init_client(self, tls_verify: bool) -> None:
        """Initialize HTTP client (must be implemented by subclass)."""
        raise NotImplementedError("Subclass must implement init_client")

    def requestGETAPI(self, url: str, include_authorization_headers: bool = True) -> Any:
        """Make GET request (must be implemented by subclass)."""
        raise NotImplementedError("Subclass must implement requestGETAPI")

    def requestPOSTAPI(self, url: str, payload_generator: Any) -> Any:
        """Make POST request (must be implemented by subclass)."""
        raise NotImplementedError("Subclass must implement requestPOSTAPI")

    # Common API methods (GET requests)False

    def getMarketStatus(self) -> Dict[str, Any]:
        """
        Get current market status (open/closed).

        Returns:
            Dictionary with market status information
        """
        return self.requestGETAPI(url=self.api_end_points["nepse_open_url"])

    def getPriceVolume(self) -> List[Dict[str, Any]]:
        """
        Get current price and volume data for all securities.

        Returns:
            List of price/volume records
        """
        return self.requestGETAPI(url=self.api_end_points["price_volume_url"])

    def getSummary(self) -> Dict[str, Any]:
        """
        Get market summary with turnover, trades, etc.

        Returns:
            Dictionary with market summary data
        """
        return self.requestGETAPI(url=self.api_end_points["summary_url"])

    def getTopGainers(self) -> List[Dict[str, Any]]:
        """
        Get list of top gaining stocks.

        Returns:
            List of top gainer records
        """
        return self.requestGETAPI(url=self.api_end_points["top_gainers_url"])

    def getTopLosers(self) -> List[Dict[str, Any]]:
        """
        Get list of top losing stocks.

        Returns:
            List of top loser records
        """
        return self.requestGETAPI(url=self.api_end_points["top_losers_url"])

    def getTopTenTradeScrips(self) -> List[Dict[str, Any]]:
        """Get top 10 scrips by trade volume."""
        return self.requestGETAPI(url=self.api_end_points["top_ten_trade_url"])

    def getTopTenTransactionScrips(self) -> List[Dict[str, Any]]:
        """Get top 10 scrips by transaction count."""
        return self.requestGETAPI(url=self.api_end_points["top_ten_transaction_url"])

    def getTopTenTurnoverScrips(self) -> List[Dict[str, Any]]:
        """Get top 10 scrips by turnover."""
        return self.requestGETAPI(url=self.api_end_points["top_ten_turnover_url"])

    def getSupplyDemand(self) -> Dict[str, Any]:
        """Get supply and demand data."""
        return self.requestGETAPI(url=self.api_end_points["supply_demand_url"])

    def getNepseIndex(self) -> Dict[str, Any]:
        """Get NEPSE index data."""
        return self.requestGETAPI(url=self.api_end_points["nepse_index_url"])

    def getNepseSubIndices(self) -> List[Dict[str, Any]]:
        """Get all NEPSE sub-indices."""
        return self.requestGETAPI(url=self.api_end_points["nepse_subindices_url"])

    def getLiveMarket(self) -> Dict[str, Any]:
        """Get live market data."""
        return self.requestGETAPI(url=self.api_end_points["live-market"])

    def getTradingAverage(
        self, business_date: Optional[str] = None, nDays: int = 180
    ) -> Dict[str, Any]:
        """
        Get trading average data.

        Args:
            business_date: Business date in YYYY-MM-DD format
            nDays: Number of days

        Returns:
            Trading average data
        """
        params = []
        if business_date:
            params.append(f"businessDate={business_date}")
        if nDays:
            params.append(f"nDays={nDays}")

        query_string = "&".join(params)
        url = f"{self.api_end_points['trading-average']}?{query_string}"
        return self.requestGETAPI(url=url)


__all__ = ["_NepseBase", "mask_sensitive_data", "safe_serialize"]
