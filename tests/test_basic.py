"""Basic tests for nepse-client to ensure CI passes."""

import pytest

from nepse_client import AsyncNepseClient, NepseClient, __version__


def test_version():
    """Test that version is defined."""
    assert __version__ is not None
    assert isinstance(__version__, str)


def test_sync_client_initialization():
    """Test synchronous client can be initialized."""
    client = NepseClient()
    client.setTLSVerification(False)
    assert client is not None
    assert hasattr(client, "getMarketStatus")
    assert hasattr(client, "getCompanyList")


def test_async_client_initialization():
    """Test asynchronous client can be initialized."""
    client = AsyncNepseClient()
    assert client is not None
    assert hasattr(client, "getMarketStatus")
    assert hasattr(client, "getCompanyList")


def test_client_base_url():
    """Test client has correct base URL."""
    client = NepseClient()
    assert client.base_url == "https://nepalstock.com.np"


def test_client_floor_sheet_size():
    """Test client has default floor sheet size."""
    client = NepseClient()
    assert client.floor_sheet_size == 500


def test_tls_verification():
    """Test TLS verification can be toggled."""
    client = NepseClient()
    client.setTLSVerification(False)
    assert client._tls_verify is False

    client.setTLSVerification(True)
    assert client._tls_verify is True


def test_context_manager():
    """Test client works as context manager."""
    with NepseClient() as client:
        assert client is not None


@pytest.mark.asyncio
async def test_async_context_manager():
    """Test async client works as async context manager."""
    async with AsyncNepseClient() as client:
        assert client is not None


def test_imports():
    """Test all main imports work."""
    from nepse_client import (
        AsyncNepseClient,
        NepseClient,
        NepseClientError,
        NepseError,
        NepseServerError,
    )

    assert NepseClient is not None
    assert AsyncNepseClient is not None
    assert NepseError is not None
    assert NepseClientError is not None
    assert NepseServerError is not None
