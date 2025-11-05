"""
Pytest configuration and fixtures for NEPSE client tests.

This module provides shared fixtures and configuration for all test modules.
"""

import json
from datetime import date, datetime
from unittest.mock import MagicMock, Mock, patch

import pytest
import httpx


@pytest.fixture
def mock_response():
   """Create a mock HTTP response."""
   def _create_response(
      status_code=200,
      json_data=None,
      text="",
      headers=None
   ):
      response = Mock(spec=httpx.Response)
      response.status_code = status_code
      response.json.return_value = json_data or {}
      response.text = text
      response.headers = headers or {}
      response.url = "https://nepalstock.com.np/api/test"
      
      # Mock request object
      response.request = Mock()
      response.request.method = "GET"
      response.request.headers = {}
      response.request.body = None
      
      return response
   
   return _create_response


@pytest.fixture
def mock_market_status():
   """Mock market status response."""
   return {
      "id": 80,
      "isOpen": "OPEN",
      "asOf": "2024-01-15T10:45:00",
   }


@pytest.fixture
def mock_company_list():
   """Mock company list response."""
   return [
      {
         "id": 1,
         "symbol": "NABIL",
         "companyName": "Nabil Bank Limited",
         "sectorName": "Commercial Banks",
         "lastTradedPrice": 1200.0,
      },
      {
         "id": 2,
         "symbol": "NICA",
         "companyName": "NIC Asia Bank Limited",
         "sectorName": "Commercial Banks",
         "lastTradedPrice": 850.0,
      },
      {
         "id": 3,
         "symbol": "SCB",
         "companyName": "Standard Chartered Bank Nepal Limited",
         "sectorName": "Commercial Banks",
         "lastTradedPrice": 550.0,
      },
   ]


@pytest.fixture
def mock_security_list():
   """Mock security list response."""
   return [
      {
         "id": 1,
         "symbol": "NABIL",
         "securityName": "Nabil Bank Limited",
         "activeStatus": "A",
      },
      {
         "id": 2,
         "symbol": "NICA",
         "securityName": "NIC Asia Bank Limited",
         "activeStatus": "A",
      },
      {
         "id": 100,
         "symbol": "PROMO1",
         "securityName": "Promoter Share 1",
         "activeStatus": "A",
      },
   ]


@pytest.fixture
def mock_summary():
   """Mock market summary response."""
   return {
      "totalTurnover": 5000000000.0,
      "totalTradedShares": 1000000,
      "totalTrades": 5000,
      "totalScripsTraded": 200,
   }


@pytest.fixture
def mock_top_gainers():
   """Mock top gainers response."""
   return [
      {
         "symbol": "NABIL",
         "ltp": 1250.0,
         "pointChange": 50.0,
         "percentageChange": 4.17,
      },
      {
         "symbol": "NICA",
         "ltp": 870.0,
         "pointChange": 20.0,
         "percentageChange": 2.35,
      },
   ]


@pytest.fixture
def mock_floor_sheet_page():
   """Mock floor sheet page response."""
   return {
      "floorsheets": {
         "content": [
               {
                  "contractId": 1001,
                  "stockSymbol": "NABIL",
                  "buyerMemberId": 10,
                  "sellerMemberId": 20,
                  "contractQuantity": 100,
                  "contractRate": 1200.0,
                  "contractAmount": 120000.0,
                  "businessDate": "2024-01-15",
               },
               {
                  "contractId": 1002,
                  "stockSymbol": "NICA",
                  "buyerMemberId": 15,
                  "sellerMemberId": 25,
                  "contractQuantity": 50,
                  "contractRate": 850.0,
                  "contractAmount": 42500.0,
                  "businessDate": "2024-01-15",
               },
         ],
         "totalPages": 3,
         "totalElements": 100,
         "size": 500,
         "number": 0,
      }
   }


@pytest.fixture
def mock_token_response():
   """Mock token authentication response."""
   return {
      "accessToken": "abc123def456ghi789jkl012mno345pqr678stu901vwx234yz",
      "refreshToken": "xyz987wvu654tsr321pon098mlk765jih432gfe210dcb",
      "salt1": 100,
      "salt2": 200,
      "salt3": 300,
      "salt4": 400,
      "salt5": 500,
      "serverTime": int(datetime.now().timestamp() * 1000),
   }


@pytest.fixture
def mock_dummy_data():
   """Mock dummy data."""
   return [147, 117, 239, 143, 157, 312] + [100] * 94  # 100 elements total


@pytest.fixture
def mock_api_endpoints():
   """Mock API endpoints."""
   return {
      "nepse_open_url": "/api/nots/nepse-data/market-open",
      "summary_url": "/api/nots/market-summary/",
      "company_list_url": "/api/nots/company/list",
      "security_list_url": "/api/nots/security?nonDelisted=true",
      "top_gainers_url": "/api/nots/top-ten/top-gainer",
      "floor_sheet": "/api/nots/nepse-data/floorsheet",
      "company_details": "/api/nots/security/",
      "company_price_volume_history": "/api/nots/market/history/security/",
   }


@pytest.fixture
def mock_headers():
   """Mock HTTP headers."""
   return {
      "Host": "nepalstock.com.np",
      "User-Agent": "Mozilla/5.0",
      "Accept": "application/json",
      "Referer": "nepalstock.com.np",
   }


@pytest.fixture
def mock_config_files(tmp_path, mock_api_endpoints, mock_dummy_data, mock_headers):
   """Create mock configuration files."""
   data_dir = tmp_path / "data"
   data_dir.mkdir()
   
   # API endpoints
   with open(data_dir / "API_ENDPOINTS.json", "w") as f:
      json.dump(mock_api_endpoints, f)
   
   # Dummy data
   with open(data_dir / "DUMMY_DATA.json", "w") as f:
      json.dump(mock_dummy_data, f)
   
   # Headers
   with open(data_dir / "HEADERS.json", "w") as f:
      json.dump(mock_headers, f)
   
   # Create empty WASM file
   (data_dir / "css.wasm").touch()
   
   return data_dir


@pytest.fixture
def sync_client_with_mocks(mock_config_files, monkeypatch):
   """Create a sync client with mocked configuration."""
   from nepse_client import Nepse
   
   # Mock the data directory path
   import nepse_client.client
   monkeypatch.setattr(
      nepse_client.client,
      "pathlib.Path(__file__).parent",
      mock_config_files.parent
   )
   
   with patch("nepse_client.sync_client.httpx.Client"):
      client = Nepse()
      return client


@pytest.fixture
def async_client_with_mocks(mock_config_files, monkeypatch):
   """Create an async client with mocked configuration."""
   from nepse_client import AsyncNepse
   
   # Mock the data directory path
   import nepse_client.client
   monkeypatch.setattr(
      nepse_client.client,
      "pathlib.Path(__file__).parent",
      mock_config_files.parent
   )
   
   with patch("nepse_client.async_client.httpx.AsyncClient"):
      client = AsyncNepse()
      return client


@pytest.fixture
def mock_httpx_client():
   """Create a mock httpx.Client."""
   mock_client = MagicMock(spec=httpx.Client)
   return mock_client


@pytest.fixture
def mock_httpx_async_client():
   """Create a mock httpx.AsyncClient."""
   mock_client = MagicMock(spec=httpx.AsyncClient)
   return mock_client


# Pytest configuration
def pytest_configure(config):
   """Configure pytest."""
   config.addinivalue_line(
      "markers", "integration: mark test as integration test"
   )
   config.addinivalue_line(
      "markers", "unit: mark test as unit test"
   )
   config.addinivalue_line(
      "markers", "slow: mark test as slow running"
   )


@pytest.fixture(autouse=True)
def reset_cache():
   """Reset client cache before each test."""
   yield
   # Cleanup code here if needed


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


def create_mock_dummy_id_manager(dummy_id=80):
   """Create a mock dummy ID manager."""
   mock_manager = Mock()
   mock_manager.getDummyID.return_value = dummy_id
   mock_manager.populateData = Mock()
   
   return mock_manager


# Export helper functions
__all__ = [
   "create_mock_token_manager",
   "create_mock_dummy_id_manager",
]