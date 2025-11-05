"""
NEPSE Client - A Python library for interacting with Nepal Stock Exchange.

This package provides both synchronous and asynchronous clients for accessing
NEPSE market data, company information, and trading details.
"""

from .sync_client import NepseClient
from .async_client import AsyncNepseClient
from .exceptions import (
   NepseError,
   NepseClientError,
   NepseServerError,
   NepseAuthenticationError,
   NepseNetworkError,
   NepseValidationError,
)

__version__ = "1.0.0"
__author__ = "Amrit Giri"
__all__ = [
   "NepseClient",
   "AsyncNepseClient",
   "NepseError",
   "NepseClientError",
   "NepseServerError",
   "NepseAuthenticationError",
   "NepseNetworkError",
   "NepseValidationError",
]
