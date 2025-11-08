# tests/test_async_client.py
"""Tests for the AsyncNepse client class."""

from unittest.mock import patch

import pytest


@pytest.fixture
def sync_client_with_mocks(mock_config_files, monkeypatch):
    """Create a sync client with mocked configuration."""
    # Mock the data directory path
    import nepse_client.client
    from nepse_client import NepseClient

    monkeypatch.setattr(
        nepse_client.client, "pathlib.Path(__file__).parent", mock_config_files.parent
    )

    with patch("nepse_client.sync_client.httpx.Client"):
        client = NepseClient()
        return client
