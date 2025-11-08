# tests/test_token_manager.py
"""Tests for the AsyncNepse client class."""

from unittest.mock import Mock


# Helper functions
def create_mock_token_manager(salts=None):
    """Create a mock token manager."""
    if salts is None:
        salts = [100, 200, 300, 400, 500]

    mock_manager = Mock()
    mock_manager.salts = salts
    mock_manager.getAccessToken.return_value = "mock_access_token"
    mock_manager.getRefreshToken.return_value = "mock_refresh_token"
    mock_manager.isTokenValid.return_value = True
    mock_manager.update = Mock()

    return mock_manager
