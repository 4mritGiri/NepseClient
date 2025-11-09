# nepse_client/token_manager.py
"""
Token management for NEPSE API authentication.

This module handles automatic token generation, refresh, and validation
for both synchronous and asynchronous clients.
"""

import asyncio
import logging
import pathlib
import time
from datetime import datetime
from typing import Any, Optional, cast

import pywasm

from .exceptions import NepseValidationError


logger = logging.getLogger(__name__)


class TokenParser:
    """
    Parse authentication tokens using WebAssembly module.

    This class uses a WASM module to decode and parse the authentication
    tokens returned by the NEPSE API.
    """

    def __init__(self):
        """Initialize token parser with WASM runtime."""
        self.runtime = pywasm.core.Runtime()
        wasm_path = pathlib.Path(__file__).parent / "data" / "css.wasm"

        try:
            self.wasm_module = self.runtime.instance_from_file(str(wasm_path))
            logger.debug("WASM module loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load WASM module: {e}")
            raise

    def parse_token_response(self, token_response: dict) -> tuple[str, str]:
        """
        Parse access and refresh tokens from API response.

        Args:
           token_response: Raw token response from API

        Returns:
           Tuple of (access_token, refresh_token)
        """
        salts = [
            token_response["salt1"],
            token_response["salt2"],
            token_response["salt3"],
            token_response["salt4"],
            token_response["salt5"],
        ]

        # Calculate indices for access token
        n = self.runtime.invocate(self.wasm_module, "cdx", salts)[0]
        access_token_l_index = self.runtime.invocate(
            self.wasm_module, "rdx", [salts[0], salts[1], salts[3], salts[2], salts[4]]
        )[0]
        o = self.runtime.invocate(
            self.wasm_module, "bdx", [salts[0], salts[1], salts[3], salts[2], salts[4]]
        )[0]
        p = self.runtime.invocate(
            self.wasm_module, "ndx", [salts[0], salts[1], salts[3], salts[2], salts[4]]
        )[0]
        q = self.runtime.invocate(
            self.wasm_module, "mdx", [salts[0], salts[1], salts[3], salts[2], salts[4]]
        )[0]

        # Calculate indices for refresh token
        salts_reversed = [salts[1], salts[0], salts[2], salts[4], salts[3]]
        a = self.runtime.invocate(
            self.wasm_module, "cdx", [salts[1], salts[0], salts[2], salts[4], salts[3]]
        )[0]
        b = self.runtime.invocate(
            self.wasm_module, "rdx", [salts[1], salts[0], salts[2], salts[3], salts[4]]
        )[0]
        c = self.runtime.invocate(
            self.wasm_module, "bdx", [salts[1], salts[0], salts[3], salts[2], salts[4]]
        )[0]
        d = self.runtime.invocate(
            self.wasm_module, "ndx", [salts[1], salts[0], salts[3], salts[2], salts[4]]
        )[0]
        e = self.runtime.invocate(
            self.wasm_module, "mdx", [salts[1], salts[0], salts[3], salts[2], salts[4]]
        )[0]
        print(salts_reversed)

        # Extract tokens
        access_token = token_response["accessToken"]
        refresh_token = token_response["refreshToken"]

        # Parse access token
        parsed_access_token = (
            access_token[0:n]
            + access_token[n + 1 : access_token_l_index]
            + access_token[access_token_l_index + 1 : o]
            + access_token[o + 1 : p]
            + access_token[p + 1 : q]
            + access_token[q + 1 :]
        )

        # Parse refresh token
        parsed_refresh_token = (
            refresh_token[0:a]
            + refresh_token[a + 1 : b]
            + refresh_token[b + 1 : c]
            + refresh_token[c + 1 : d]
            + refresh_token[d + 1 : e]
            + refresh_token[e + 1 :]
        )

        return (parsed_access_token, parsed_refresh_token)


class _TokenManagerBase:
    """
    Base class for token managers.

    Provides common functionality for managing authentication tokens,
    including validation and salt extraction.

    Args:
       nepse: Reference to parent NEPSE client
    """

    # Token validity period in seconds (45 seconds as per original)
    MAX_UPDATE_PERIOD = 45

    def __init__(self, nepse):
        """Initialize token manager."""
        self.nepse = nepse
        self.token_parser = TokenParser()

        # Token endpoints
        self.token_url = "/api/authenticate/prove"
        self.refresh_url = "/api/authenticate/refresh-token"

        # Token state
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.token_time_stamp: Optional[int] = None
        self.salts: Optional[list[int]] = None

    def isTokenValid(self) -> bool:
        """
        Check if current token is still valid.

        Returns:
           True if token is valid, False otherwise
        """
        if self.token_time_stamp is None:
            return False

        elapsed = int(time.time()) - self.token_time_stamp
        return elapsed < self.MAX_UPDATE_PERIOD

    def _getValidTokenFromJSON(self, token_response: dict) -> tuple[str, str, int, list[int]]:
        """
        Extract and validate token data from API response.

        Args:
           token_response: Raw token response from API

        Returns:
           Tuple of (access_token, refresh_token, timestamp, salts)
        """
        # Extract salts
        salts = [int(token_response[f"salt{i}"]) for i in range(1, 6)]

        # Parse tokens
        access_token, refresh_token = self.token_parser.parse_token_response(token_response)

        # Extract timestamp
        timestamp = int(token_response["serverTime"] / 1000)

        return (access_token, refresh_token, timestamp, salts)

    def __repr__(self) -> str:
        """Return the string representation of the token manager.

        Returns:
            str: Token Manager
        """
        if self.access_token is None or self.token_time_stamp is None:
            return "Token Manager: Not Initialized"

        timestamp_str = datetime.fromtimestamp(self.token_time_stamp).strftime("%Y-%m-%d %H:%M:%S")
        return (
            f"Token Manager:\n"
            f"  Access Token: {self.access_token[:20]}...\n"
            f"  Refresh Token: {self.refresh_token[:20] if self.refresh_token else ''}...\n"
            f"  Salts: {self.salts}\n"
            f"  Timestamp: {timestamp_str}\n"
            f"  Valid: {self.isTokenValid()}"
        )


class TokenManager(_TokenManagerBase):
    """
    Synchronous token manager.

    Manages authentication tokens for synchronous NEPSE client,
    automatically refreshing tokens when they expire.
    """

    def __init__(self, nepse):
        """Initialize synchronous token manager."""
        super().__init__(nepse)

    def getAccessToken(self) -> str:
        """
        Get valid access token, refreshing if necessary.

        Returns:
           Valid access token
        """
        if not self.isTokenValid():
            self.update()
        assert self.access_token is not None
        return self.access_token

    def getRefreshToken(self) -> str:
        """
        Get valid refresh token, refreshing if necessary.

        Returns:
           Valid refresh token
        """
        if not self.isTokenValid():
            self.update()
        assert self.refresh_token is not None
        return self.refresh_token

    def update(self) -> None:
        """Fetch and update authentication tokens."""
        self._setToken()

    def _setToken(self) -> None:
        """Fetch tokens from API and update internal state."""
        logger.debug("Fetching new authentication token")
        json_response = self._getTokenHttpRequest()

        (
            self.access_token,
            self.refresh_token,
            self.token_time_stamp,
            self.salts,
        ) = self._getValidTokenFromJSON(json_response)

        logger.info("Authentication token refreshed successfully")

    def _getTokenHttpRequest(self) -> dict[str, Any]:
        """
        Make HTTP request to get token.

        Returns:
           Token response dictionary
        """
        response = self.nepse.requestGETAPI(url=self.token_url, include_authorization_headers=False)
        if not isinstance(response, dict):
            raise NepseValidationError(f"Expected dict from token API, got {type(response)}")
        return cast(dict[str, Any], response)


class AsyncTokenManager(_TokenManagerBase):
    """
    Asynchronous token manager.

    Manages authentication tokens for asynchronous NEPSE client,
    with support for concurrent token refresh operations.
    """

    def __init__(self, nepse):
        """Initialize asynchronous token manager."""
        super().__init__(nepse)

        # Synchronization events for concurrent operations
        self.update_started = asyncio.Event()
        self.update_completed = asyncio.Event()

    async def getAccessToken(self) -> str:
        """
        Get valid access token, refreshing if necessary.

        Returns:
           Valid access token
        """
        if not self.isTokenValid():
            await self.update()
        assert self.access_token is not None
        return self.access_token

    async def getRefreshToken(self) -> str:
        """
        Get valid refresh token, refreshing if necessary.

        Returns:
           Valid refresh token
        """
        if not self.isTokenValid():
            await self.update()
        assert self.refresh_token is not None
        return self.refresh_token

    async def update(self) -> None:
        """Fetch and update authentication tokens asynchronously."""
        await self._setToken()

    async def _setToken(self) -> None:
        """
        Fetch tokens from API and update internal state.

        Ensures only one token refresh operation happens at a time,
        even with concurrent requests.
        """
        # Check if another coroutine is already updating
        if not self.update_started.is_set():
            # Mark update as started
            self.update_started.set()
            self.update_completed.clear()

            try:
                logger.debug("Fetching new authentication token")
                json_response = await self._getTokenHttpRequest()

                (
                    self.access_token,
                    self.refresh_token,
                    self.token_time_stamp,
                    self.salts,
                ) = self._getValidTokenFromJSON(json_response)

                logger.info("Authentication token refreshed successfully")

            finally:
                # Mark update as completed
                self.update_completed.set()
                self.update_started.clear()
        else:
            # Wait for ongoing update to complete
            await self.update_completed.wait()

    async def _getTokenHttpRequest(self) -> dict:
        """
        Make async HTTP request to get token.

        Returns:
           Token response dictionary
        """
        return cast(
            dict[Any, Any],
            await self.nepse.requestGETAPI(url=self.token_url, include_authorization_headers=False),
        )


__all__ = [
    "TokenManager",
    "AsyncTokenManager",
    "TokenParser",
]
