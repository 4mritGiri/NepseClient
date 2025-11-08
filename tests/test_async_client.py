# tests/test_async_client.py
"""Tests for the AsyncNepse client class."""

from unittest.mock import MagicMock, patch

import httpx
import pytest


@pytest.fixture
def async_client_with_mocks(mock_config_files, monkeypatch):
    """Create an async client with mocked configuration."""
    # Mock the data directory path
    import nepse_client.client
    from nepse_client import AsyncNepseClient

    monkeypatch.setattr(
        nepse_client.client, "pathlib.Path(__file__).parent", mock_config_files.parent
    )

    with patch("nepse_client.async_client.httpx.AsyncClient"):
        client = AsyncNepseClient()
        return client


@pytest.fixture
def mock_httpx_async_client():
    """Create a mock httpx.AsyncClient."""
    mock_client = MagicMock(spec=httpx.AsyncClient)
    return mock_client
