"""
NEPSE Client - A comprehensive Python library for Nepal Stock Exchange API.

This package provides both synchronous and asynchronous clients for accessing
NEPSE market data, company information, trading details, and more.

Example:
Synchronous usage::

   from nepse_client import NepseClient

   client = NepseClient()
   market_status = client.getMarketStatus()
   companies = client.getCompanyList()

Asynchronous usage::

   import asyncio
   from nepse_client import AsyncNepseClient

   async def main():
      client = AsyncNepseClient()
      market_status = await client.getMarketStatus()
      companies = await client.getCompanyList()

   asyncio.run(main())
"""

import importlib.metadata
import re

from .async_client import AsyncNepseClient
from .exceptions import (
    NepseAuthenticationError,
    NepseBadGatewayError,
    NepseClientError,
    NepseConfigurationError,
    NepseConnectionError,
    NepseDataNotFoundError,
    NepseError,
    NepseNetworkError,
    NepseRateLimitError,
    NepseServerError,
    NepseTimeoutError,
    NepseValidationError,
)
from .sync_client import NepseClient


try:
    pkg_metadata = importlib.metadata.metadata("nepse-client")
    # Read metadata from the installed package (from pyproject.toml)
    __name__ = pkg_metadata["Name"]
    __version__ = importlib.metadata.version("nepse-client")
    # Attempt to get Author from the Author-email field
    author_email_str = pkg_metadata["Author-email"]
    if author_email_str:
        # Extract name using regex, e.g., "Name <email>" -> "Name"
        match = re.match(r"^(.*?)\s+<.*>$", author_email_str)
        __author__ = match.group(1) if match else "Unknown"
    else:
        __author__ = "Unknown"
    __email__ = pkg_metadata["Author-email"]
    __license__ = pkg_metadata["License"]
except importlib.metadata.PackageNotFoundError:
    # Fallback values if package is not installed (e.g., during development)
    __name__ = "nepse-client"
    __version__ = "0.1.1"
    __author__ = "Amrit Giri"
    __email__ = "amritgiri.dev@gmail.com"
    __license__ = "MIT"


__all__ = [
    # Clients
    "NepseClient",
    "AsyncNepseClient",
    # Exceptions
    "NepseError",
    "NepseClientError",
    "NepseServerError",
    "NepseAuthenticationError",
    "NepseNetworkError",
    "NepseValidationError",
    "NepseBadGatewayError",
    "NepseRateLimitError",
    "NepseDataNotFoundError",
    "NepseTimeoutError",
    "NepseConnectionError",
    "NepseConfigurationError",
    # Metadata
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]


def get_client_info():
    """
    Get information about the NEPSE client package.

    Returns:
       dict: Package information including version, author, and features.

    Example:
       >>> from nepse_client import get_client_info
       >>> info = get_client_info()
       >>> print(info['version'])
       1.0.0
    """
    print(f"Name: {__name__}")
    print(f"Version: {__version__}")
    print(f"Author: {__author__}")
    print(f"Email: {__email__}")
    print(f"License: {__license__}")
    return {
        "name": __name__,
        "version": __version__,
        "author": __author__,
        "email": __email__,
        "license": __license__,
        "features": [
            "Synchronous and Asynchronous API",
            "Automatic token management",
            "Comprehensive error handling",
            "Type hints support",
            "Market data access",
            "Company information",
            "Trading data",
            "Floor sheet access",
        ],
        "python_requires": ">=3.11",
    }
