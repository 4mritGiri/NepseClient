# tests/test_dummy_id_manager.py
"""Tests for the Dummy id manager class."""

from unittest.mock import Mock


def create_mock_dummy_id_manager(dummy_id=80):
    """Create a mock dummy ID manager."""
    mock_manager = Mock()
    mock_manager.getDummyID.return_value = dummy_id
    mock_manager.populateData = Mock()

    return mock_manager
