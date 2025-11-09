"""
Custom exceptions for NEPSE Client.

This module provides a comprehensive exception hierarchy for handling
various error scenarios when interacting with the NEPSE API.
"""

from typing import Any, Optional


class NepseError(Exception):
    """
    Base exception class for all NEPSE-related errors.

    All custom exceptions in this library inherit from this class,
    allowing for easy catch-all error handling.

    Attributes:
       message: Human-readable error description
       status_code: HTTP status code (if applicable)
       response_data: Raw response data from the API
       request_data: Original request data
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Any] = None,
        request_data: Optional[dict[str, Any]] = None,
    ):
        """
        Initialize NepseError.

        Args:
           message: Error description
           status_code: HTTP status code
           response_data: Response from the API
           request_data: Original request data
        """
        super().__init__(message, status_code, response_data, request_data)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
        self.request_data = request_data

    def __str__(self) -> str:
        """Return string representation of the error."""
        base_msg = self.message
        if self.status_code:
            base_msg = f"[{self.status_code}] {base_msg}"
        return base_msg

    def __repr__(self) -> str:
        """Return detailed representation of the error."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"status_code={self.status_code}, "
            f"response_data={self.response_data!r})"
        )

    def to_dict(self) -> dict[str, Any]:
        """
        Convert exception to dictionary for logging/serialization.

        Returns:
           Dictionary representation of the exception
        """
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "status_code": self.status_code,
            "response_data": self.response_data,
        }


class NepseClientError(NepseError):
    """
    Raised when client sends an invalid request (4xx errors).

    This typically indicates:
    - Invalid parameters
    - Missing required fields
    - Malformed request data
    - Invalid company symbol

    Example:
       >>> try:
       ...     client.getCompanyDetails("INVALID")
       ... except NepseClientError as e:
       ...     print(f"Invalid request: {e}")
    """

    def __init__(
        self,
        message: str = "Invalid client request",
        status_code: int = 400,
        response_data: Optional[Any] = None,
        request_data: Optional[dict[str, Any]] = None,
    ):
        """Initialize the exception with a default message."""
        super().__init__(message, status_code, response_data, request_data)


class NepseAuthenticationError(NepseError):
    """
    Raised when access token has expired (401 Unauthorized).

    This exception is typically handled automatically by the client,
    which will refresh the token and retry the request.

    Note:
       Users usually don't need to handle this exception directly
       as the client manages token refresh automatically.
    """

    def __init__(
        self,
        message: str = "Authentication token expired",
        status_code: int = 401,
        response_data: Optional[Any] = None,
    ):
        """Initialize the exception with a default message."""
        super().__init__(message, status_code, response_data)


class NepseBadGatewayError(NepseError):
    """
    Raised when server returns 502 Bad Gateway.

    This typically indicates:
    - Server temporarily unavailable
    - Upstream server issues
    - Network problems between servers

    Recommended action: Retry the request after a short delay.
    """

    def __init__(
        self,
        message: str = "Bad Gateway - Server temporarily unavailable",
        status_code: int = 502,
        response_data: Optional[Any] = None,
    ):
        """Initialize the exception with a default message."""
        super().__init__(message, status_code, response_data)


class NepseServerError(NepseError):
    """
    Generic server error for 5xx status codes.

    This indicates an error on the NEPSE server side.
    Common causes:
    - Internal server error (500)
    - Service unavailable (503)
    - Gateway timeout (504)

    Recommended action: Retry with exponential backoff or contact support.
    """

    def __init__(
        self,
        message: str = "Server error occurred",
        status_code: int = 500,
        response_data: Optional[Any] = None,
    ):
        """Initialize the exception with a default message."""
        super().__init__(message, status_code, response_data)


class NepseNetworkError(NepseError):
    """
    Raised for general network or unexpected HTTP issues.

    This covers:
    - Connection timeouts
    - DNS resolution failures
    - SSL/TLS errors
    - Unexpected response formats
    - Network interruptions

    Recommended action: Check network connectivity and retry.
    """

    def __init__(
        self,
        message: str = "Network error occurred",
        status_code: Optional[int] = None,
        response_data: Optional[Any] = None,
    ):
        """Initialize the exception with a default message."""
        super().__init__(message, status_code, response_data)


class NepseValidationError(NepseError):
    """
    Raised when input validation fails before making API request.

    This is raised for client-side validation errors such as:
    - Invalid date formats
    - Out of range values
    - Missing required parameters
    - Invalid data types

    Example:
       >>> try:
       ...     client.getCompanyPriceVolumeHistory("NABIL", start_date="invalid")
       ... except NepseValidationError as e:
       ...     print(f"Validation error: {e}")
    """

    def __init__(
        self,
        message: str = "Input validation failed",
        field: Optional[str] = None,
        value: Optional[Any] = None,
    ):
        """
        Initialize validation error.

        Args:
           message: Error description
           field: Name of the invalid field
           value: Invalid value provided
        """
        full_message = message
        if field:
            full_message = f"{message} (field: {field})"
        super().__init__(full_message, None, None)
        self.field = field
        self.value = value


class NepseRateLimitError(NepseError):
    """
    Raised when API rate limit is exceeded (429 Too Many Requests).

    Attributes:
       retry_after: Seconds to wait before retrying (if provided by server)
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        status_code: int = 429,
        retry_after: Optional[int] = None,
    ):
        """
        Initialize rate limit error.

        Args:
           message: Error description
           status_code: HTTP status code
           retry_after: Seconds to wait before retry
        """
        if retry_after:
            message = f"{message}. Retry after {retry_after} seconds"
        super().__init__(message, status_code, None)
        self.retry_after = retry_after


class NepseDataNotFoundError(NepseError):
    """
    Raised when requested data is not found.

    This is used when:
    - Company symbol doesn't exist
    - No data available for requested date
    - Empty result sets

    Example:
       >>> try:
       ...     client.getFloorSheetOf("INVALID", "2024-01-01")
       ... except NepseDataNotFoundError as e:
       ...     print(f"Data not found: {e}")
    """

    def __init__(
        self,
        message: str = "Requested data not found",
        resource: Optional[str] = None,
    ):
        """
        Initialize data not found error.

        Args:
           message: Error description
           resource: Resource that was not found
        """
        if resource:
            message = f"{message}: {resource}"
        super().__init__(message, None)
        self.resource = resource


class NepseTimeoutError(NepseError):
    """
    Raised when request times out.

    This occurs when the server doesn't respond within the specified timeout period.

    Attributes:
       timeout: Timeout value in seconds
    """

    def __init__(
        self,
        message: str = "Request timeout",
        timeout: Optional[float] = None,
    ):
        """
        Initialize timeout error.

        Args:
           message: Error description
           timeout: Timeout value in seconds
        """
        if timeout:
            message = f"{message} after {timeout} seconds"
        """Initialize the exception with a default message."""
        super().__init__(message, None)
        self.timeout = timeout


class NepseConnectionError(NepseError):
    """
    Raised when connection to NEPSE server fails.

    This is different from NepseNetworkError as it specifically
    indicates inability to establish a connection.
    """

    def __init__(self, message: str = "Failed to connect to NEPSE server"):
        """Initialize the exception with a default message."""
        super().__init__(message)


class NepseConfigurationError(NepseError):
    """
    Raised when there's an issue with client configuration.

    This includes:
    - Missing required configuration files
    - Invalid configuration values
    - Corrupted data files
    """

    def __init__(self, message: str = "Configuration error"):
        """Initialize the exception with a default message."""
        super().__init__(message)


NepseErrorType = type[NepseError]

# Exception mapping for HTTP status codes
HTTP_STATUS_EXCEPTIONS: dict[int, NepseErrorType] = {
    400: NepseClientError,
    401: NepseAuthenticationError,
    404: NepseDataNotFoundError,
    429: NepseRateLimitError,
    502: NepseBadGatewayError,
    503: NepseServerError,
    504: NepseServerError,
}


def get_exception_for_status(
    status_code: int,
    message: str,
    response_data: Optional[Any] = None,
) -> NepseError:
    """
    Get appropriate exception class for HTTP status code.

    Args:
       status_code: HTTP status code
       message: Error message
       response_data: Response data from API

    Returns:
       Appropriate exception instance
    """
    exception_class: type[NepseError] = HTTP_STATUS_EXCEPTIONS.get(
        status_code,
        NepseServerError if 500 <= status_code < 600 else NepseError,
    )
    return exception_class(message, status_code, response_data)


__all__ = [
    "NepseError",
    "NepseClientError",
    "NepseAuthenticationError",
    "NepseBadGatewayError",
    "NepseServerError",
    "NepseNetworkError",
    "NepseValidationError",
    "NepseRateLimitError",
    "NepseDataNotFoundError",
    "NepseTimeoutError",
    "NepseConnectionError",
    "NepseConfigurationError",
    "get_exception_for_status",
]
