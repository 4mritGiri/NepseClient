Utilities
=========

This page documents utility functions and helper classes.

Helper Functions
----------------

mask_sensitive_data
~~~~~~~~~~~~~~~~~~~

.. autofunction:: nepse_client.client.mask_sensitive_data

Masks sensitive fields in data dictionaries for safe logging.

**Example:**

.. code-block:: python

   from nepse_client.client import mask_sensitive_data

   data = {
      'token': 'secret_token_12345',
      'password': 'my_password',
      'username': 'user123'
   }

   masked = mask_sensitive_data(data)
   # {'token': '***MASKED***', 'password': '***MASKED***', 'username': 'user123'}

safe_serialize
~~~~~~~~~~~~~~

.. autofunction:: nepse_client.client.safe_serialize

Safely serializes objects for logging, handling complex types.

**Example:**

.. code-block:: python

   from nepse_client.client import safe_serialize
   from datetime import datetime

   obj = {
      'date': datetime.now(),
      'data': [1, 2, 3],
      'nested': {'key': 'value'}
   }

   serialized = safe_serialize(obj)
   print(serialized)  # JSON string

get_client_info
~~~~~~~~~~~~~~~

.. autofunction:: nepse_client.get_client_info

Returns information about the nepse-client package.

**Example:**

.. code-block:: python

   from nepse_client import get_client_info

   info = get_client_info()
   print(info)
   # {
   #     'name': 'nepse-client',
   #     'version': '1.0.0',
   #     'author': 'Amrit Giri',
   #     'features': [...],
   #     ...
   # }

Token Parser
------------

TokenParser
~~~~~~~~~~~

.. autoclass:: nepse_client.token_manager.TokenParser
   :members:
   :undoc-members:
   :show-inheritance:

Parses authentication tokens using WebAssembly module.

**Example:**

.. code-block:: python

   from nepse_client.token_manager import TokenParser

   parser = TokenParser()
   token_response = {
      'accessToken': '...',
      'refreshToken': '...',
      'salt1': 100,
      'salt2': 200,
      'salt3': 300,
      'salt4': 400,
      'salt5': 500,
      'serverTime': 1234567890
   }

   access_token, refresh_token = parser.parse_token_response(token_response)

Data Type Conversions
---------------------

Date/Time Handling
~~~~~~~~~~~~~~~~~~

The library handles various date and time formats:

**String to Date:**

.. code-block:: python

   from datetime import date

   # ISO format strings
   date_obj = date.fromisoformat('2024-01-15')

   # In client methods
   history = client.getCompanyPriceVolumeHistory(
      symbol='NABIL',
      start_date='2024-01-01',  # String
      end_date=date.today()      # date object
   )

**DateTime Parsing:**

The ``DummyIDManager`` includes robust datetime parsing:

.. code-block:: python

   from nepse_client.dummy_id_manager import DummyIDManager

   manager = DummyIDManager()

   # Handles various formats
   dt1 = manager.convertToDateTime('2024-01-15T10:45:00')
   dt2 = manager.convertToDateTime('2024-01-15T10:45:00.123456')
   dt3 = manager.convertToDateTime('2024-01-15T10:45:00.123456789')  # Truncates

Type Annotations
----------------

The library provides comprehensive type hints:

**Client Types:**

.. code-block:: python

   from typing import Dict, List, Any, Optional
   from nepse_client import NepseClient

   client: NepseClient = NepseClient()

   # All methods have return type annotations
   status: Dict[str, Any] = client.getMarketStatus()
   companies: List[Dict[str, Any]] = client.getCompanyList()
   company: Dict[str, Any] = client.getCompanyDetails('NABIL')

**Optional Parameters:**

.. code-block:: python

   from datetime import date
   from typing import Optional, Union

   history = client.getCompanyPriceVolumeHistory(
      symbol: str,
      start_date: Optional[Union[str, date]] = None,
      end_date: Optional[Union[str, date]] = None
   )

Configuration Loading
---------------------

The client loads configuration from JSON files:

**API Endpoints:**

Located at ``nepse_client/data/API_ENDPOINTS.json``

::

   {
      "market_status_url": "/api/nots/nepse-data/market-open",
      "summary_url": "/api/nots/market-summary/",
      ...
   }

**Headers:**

Located at ``nepse_client/data/HEADERS.json``

::

   {
      "User-Agent": "Mozilla/5.0 ...",
      "Accept": "application/json",
      ...
   }

**Dummy Data:**

Located at ``nepse_client/data/DUMMY_DATA.json``

::

   [147, 117, 239, 143, ...]

**WASM Module:**

Located at ``nepse_client/data/css.wasm`` - Used for token parsing

Logging Utilities
-----------------

The library uses Python's standard logging:

**Basic Setup:**

.. code-block:: python

   import logging

   # Configure root logger
   logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )

   # Client will use configured logger
   client = NepseClient()

**Custom Logger:**

.. code-block:: python

   import logging

   # Create custom logger
   logger = logging.getLogger('my_nepse_app')
   logger.setLevel(logging.DEBUG)

   # Add handler
   handler = logging.FileHandler('nepse.log')
   handler.setFormatter(
      logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
   )
   logger.addHandler(handler)

   # Use with client
   client = NepseClient(logger=logger)

**Log Levels:**

* ``DEBUG``: Detailed information (HTTP requests, responses)
* ``INFO``: General information (token refresh, cache updates)
* ``WARNING``: Warning messages (retry attempts)
* ``ERROR``: Error messages (API failures)
* ``CRITICAL``: Critical errors (configuration failures)

Response Processing
-------------------

The client automatically processes responses:

**JSON Parsing:**

.. code-block:: python

   # Automatic JSON parsing
   response = client.getMarketStatus()
   # Returns: Dict[str, Any]

**Error Handling:**

.. code-block:: python

   # Automatic error handling based on status code
   # 200-299: Success - returns data
   # 400: NepseClientError
   # 401: NepseAuthenticationError (auto-retry)
   # 502: NepseBadGatewayError
   # 5xx: NepseServerError

**Data Extraction:**

.. code-block:: python

   # Some responses have nested content
   history = client.getCompanyPriceVolumeHistory('NABIL')

   # Automatically extracts 'content' field if present
   if isinstance(history, dict) and 'content' in history:
      data = history['content']
   else:
      data = history

Caching Mechanisms
------------------

The client implements smart caching:

**Company ID Cache:**

.. code-block:: python

   # First call - fetches from API
   company_map = client.getCompanyIDKeyMap()
   # {'NABIL': 1, 'NICA': 2, ...}

   # Subsequent calls - returns cached data
   company_map = client.getCompanyIDKeyMap()

   # Force refresh
   company_map = client.getCompanyIDKeyMap(force_update=True)

**Security ID Cache:**

.. code-block:: python

   security_map = client.getSecurityIDKeyMap()
   # Cached automatically

**Sector Scrips Cache:**

.. code-block:: python

   sector_scrips = client.getSectorScrips()
   # {'Commercial Banks': ['NABIL', ...], ...}
   # Cached after first call

Progress Tracking
-----------------

For long-running operations:

**Floor Sheet with Progress:**

.. code-block:: python

   from nepse_client import NepseClient

   client = NepseClient()

   # Shows progress bar
   floor_sheet = client.getFloorSheet(show_progress=True)
   # Downloading floor sheet: 100%|████████| 150/150 [00:30<00:00]

**Async Progress:**

.. code-block:: python

   import asyncio
   from nepse_client import AsyncNepseClient

   async def main():
      client = AsyncNepseClient()
      floor_sheet = await client.getFloorSheet(show_progress=True)

   asyncio.run(main())

Pagination Helpers
------------------

Some endpoints return paginated data:

**Manual Pagination:**

.. code-block:: python

   # Get specific page
   page_0 = client.getFloorSheet(page=0)
   page_1 = client.getFloorSheet(page=1)

**Automatic Pagination:**

.. code-block:: python

   # Get all pages automatically
   all_data = client.getFloorSheet()  # Fetches all pages

**Paginated Format:**

.. code-block:: python

   # Returns list of pages
   pages = client.getFloorSheet(paginated=True)
   # [[page_0_data], [page_1_data], ...]

Testing Utilities
-----------------

For testing your application:

**Mock Client:**

.. code-block:: python

   from unittest.mock import Mock
   from nepse_client import NepseClient

   # Create mock client
   mock_client = Mock(spec=NepseClient)
   mock_client.getMarketStatus.return_value = {
      'isOpen': 'OPEN',
      'asOf': '2024-01-15T10:00:00'
   }

   # Use in tests
   status = mock_client.getMarketStatus()

**Disable TLS for Testing:**

.. code-block:: python

   # Only for testing!
   client = NepseClient()
   client.setTLSVerification(False)

   # Run tests
   # ...

   # Re-enable
   client.setTLSVerification(True)

Constants
---------

**Package Constants:**

.. code-block:: python

   from nepse_client import __version__, __author__

   print(__version__)  # '1.0.0'
   print(__author__)   # 'Amrit Giri'

**Client Constants:**

.. code-block:: python

   client = NepseClient()

   print(client.base_url)           # 'https://nepalstock.com.np'
   print(client.floor_sheet_size)   # 500
   print(client.timeout)            # 100.0
