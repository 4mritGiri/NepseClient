Client Classes
==============

This page documents the client classes in detail.

Base Client
-----------

.. automodule:: nepse_client.client
   :members:
   :undoc-members:
   :show-inheritance:

The base client provides common functionality for both synchronous and asynchronous implementations.

NepseClient (Synchronous)
--------------------------

.. autoclass:: nepse_client.sync_client.NepseClient
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __enter__, __exit__

The synchronous client is ideal for:

* Simple scripts and applications
* Jupyter notebooks
* Sequential data fetching
* Environments without async support

**Initialization:**

.. code-block:: python

   from nepse_client import NepseClient

   # Basic initialization
   client = NepseClient()

   # With custom settings
   client = NepseClient(
      logger=my_logger,
      mask_request_data=True,
      timeout=120.0
   )

**Context Manager:**

.. code-block:: python

   # Automatic resource cleanup
   with NepseClient() as client:
      status = client.getMarketStatus()
      companies = client.getCompanyList()
   # Client automatically closed

Market Data Methods
~~~~~~~~~~~~~~~~~~~

.. automethod:: nepse_client.sync_client.NepseClient.getMarketStatus
.. automethod:: nepse_client.sync_client.NepseClient.getSummary
.. automethod:: nepse_client.sync_client.NepseClient.getNepseIndex
.. automethod:: nepse_client.sync_client.NepseClient.getNepseSubIndices
.. automethod:: nepse_client.sync_client.NepseClient.getLiveMarket
.. automethod:: nepse_client.sync_client.NepseClient.getPriceVolume
.. automethod:: nepse_client.sync_client.NepseClient.getSupplyDemand

Company Information Methods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: nepse_client.sync_client.NepseClient.getCompanyList
.. automethod:: nepse_client.sync_client.NepseClient.getSecurityList
.. automethod:: nepse_client.sync_client.NepseClient.getCompanyDetails
.. automethod:: nepse_client.sync_client.NepseClient.getCompanyPriceVolumeHistory
.. automethod:: nepse_client.sync_client.NepseClient.getDailyScripPriceGraph
.. automethod:: nepse_client.sync_client.NepseClient.getCompanyFinancialDetails
.. automethod:: nepse_client.sync_client.NepseClient.getCompanyAGM
.. automethod:: nepse_client.sync_client.NepseClient.getCompanyDividend

Trading Data Methods
~~~~~~~~~~~~~~~~~~~~~

.. automethod:: nepse_client.sync_client.NepseClient.getFloorSheet
.. automethod:: nepse_client.sync_client.NepseClient.getFloorSheetOf
.. automethod:: nepse_client.sync_client.NepseClient.getSymbolMarketDepth
.. automethod:: nepse_client.sync_client.NepseClient.getTradingAverage

Top Performers Methods
~~~~~~~~~~~~~~~~~~~~~~~

.. automethod:: nepse_client.sync_client.NepseClient.getTopGainers
.. automethod:: nepse_client.sync_client.NepseClient.getTopLosers
.. automethod:: nepse_client.sync_client.NepseClient.getTopTenTradeScrips
.. automethod:: nepse_client.sync_client.NepseClient.getTopTenTransactionScrips
.. automethod:: nepse_client.sync_client.NepseClient.getTopTenTurnoverScrips

Utility Methods
~~~~~~~~~~~~~~~

.. automethod:: nepse_client.sync_client.NepseClient.getCompanyIDKeyMap
.. automethod:: nepse_client.sync_client.NepseClient.getSecurityIDKeyMap
.. automethod:: nepse_client.sync_client.NepseClient.getSectorScrips
.. automethod:: nepse_client.sync_client.NepseClient.setTLSVerification

AsyncNepseClient (Asynchronous)
--------------------------------

.. autoclass:: nepse_client.async_client.AsyncNepseClient
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __aenter__, __aexit__

The asynchronous client is ideal for:

* High-performance applications
* Concurrent data fetching
* Web servers (FastAPI, aiohttp)
* Real-time data processing

**Initialization:**

.. code-block:: python

   from nepse_client import AsyncNepseClient

   # Basic initialization
   client = AsyncNepseClient()

   # With custom settings
   client = AsyncNepseClient(
      logger=my_logger,
      mask_request_data=True,
      timeout=120.0
   )

**Context Manager:**

.. code-block:: python

   import asyncio

   async def main():
      # Automatic resource cleanup
      async with AsyncNepseClient() as client:
         status = await client.getMarketStatus()
         companies = await client.getCompanyList()
      # Client automatically closed

   asyncio.run(main())

**Concurrent Requests:**

.. code-block:: python

   import asyncio
   from nepse_client import AsyncNepseClient

   async def fetch_multiple():
      async with AsyncNepseClient() as client:
         # Fetch multiple data concurrently
         results = await asyncio.gather(
            client.getMarketStatus(),
            client.getSummary(),
            client.getTopGainers(),
            client.getTopLosers()
         )
         status, summary, gainers, losers = results

   asyncio.run(fetch_multiple())

Token Management
----------------

.. automodule:: nepse_client.token_manager
   :members:
   :undoc-members:
   :show-inheritance:

TokenManager (Synchronous)
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: nepse_client.token_manager.TokenManager
   :members:
   :undoc-members:
   :show-inheritance:

Manages authentication tokens for synchronous client:

* Automatic token refresh
* Token validity checking
* Salt management for payload generation

AsyncTokenManager (Asynchronous)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: nepse_client.token_manager.AsyncTokenManager
   :members:
   :undoc-members:
   :show-inheritance:

Manages authentication tokens for asynchronous client:

* Automatic token refresh
* Concurrent request handling
* Event-based synchronization

Dummy ID Management
-------------------

.. automodule:: nepse_client.dummy_id_manager
   :members:
   :undoc-members:
   :show-inheritance:

DummyIDManager (Synchronous)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: nepse_client.dummy_id_manager.DummyIDManager
   :members:
   :undoc-members:
   :show-inheritance:

Manages dummy IDs for POST request payloads:

* Date-aware caching
* Automatic updates on date change
* Market status integration

AsyncDummyIDManager (Asynchronous)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: nepse_client.dummy_id_manager.AsyncDummyIDManager
   :members:
   :undoc-members:
   :show-inheritance:

Manages dummy IDs for asynchronous POST requests:

* Date-aware caching
* Concurrent request support
* Event-based synchronization

Configuration
-------------

All clients support the following configuration options:

**Parameters:**

* ``logger`` (Optional[logging.Logger]): Custom logger instance
* ``mask_request_data`` (bool): Mask sensitive data in logs (default: True)
* ``timeout`` (float): Request timeout in seconds (default: 100.0)

**Example:**

.. code-block:: python

   import logging
   from nepse_client import NepseClient

   # Setup logging
   logger = logging.getLogger('my_app')
   logger.setLevel(logging.DEBUG)

   # Initialize with custom config
   client = NepseClient(
      logger=logger,
      mask_request_data=True,
      timeout=60.0
   )

   # Disable TLS verification (testing only!)
   client.setTLSVerification(False)

Performance Considerations
--------------------------

Synchronous vs Asynchronous
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Use Synchronous Client when:**

* Making sequential requests
* Simple scripts or notebooks
* Straightforward data fetching
* No need for concurrency

**Use Asynchronous Client when:**

* Fetching multiple resources concurrently
* Building web applications
* High-performance requirements
* Processing real-time data

**Performance Comparison:**

.. code-block:: python

   # Synchronous - Sequential (slower)
   client = NepseClient()
   status = client.getMarketStatus()        # ~500ms
   summary = client.getSummary()            # ~500ms
   gainers = client.getTopGainers()         # ~500ms
   # Total: ~1500ms

   # Asynchronous - Concurrent (faster)
   async with AsyncNepseClient() as client:
      status, summary, gainers = await asyncio.gather(
         client.getMarketStatus(),        # \
         client.getSummary(),             # } ~500ms (concurrent)
         client.getTopGainers()           # /
      )
   # Total: ~500ms

Caching
~~~~~~~

The client automatically caches:

* Company ID mappings
* Security ID mappings
* Sector scrips

To force cache refresh:

.. code-block:: python

   # Force refresh cache
   company_map = client.getCompanyIDKeyMap(force_update=True)
   security_map = client.getSecurityIDKeyMap(force_update=True)

Best Practices
--------------

1. **Use Context Managers**

   .. code-block:: python

      # Good
      with NepseClient() as client:
         data = client.getMarketStatus()

      # Avoid
      client = NepseClient()
      data = client.getMarketStatus()
      # Resource not cleaned up!

2. **Handle Errors Properly**

   .. code-block:: python

      from nepse_client import NepseClient, NepseError

      with NepseClient() as client:
         try:
            data = client.getMarketStatus()
         except NepseError as e:
            logger.error(f"Error: {e}")

3. **Use Async for Multiple Requests**

   .. code-block:: python

      # Fetch 10 companies concurrently
      async with AsyncNepseClient() as client:
         symbols = ['NABIL', 'NICA', 'SCB', ...]
         tasks = [client.getCompanyDetails(s) for s in symbols]
         results = await asyncio.gather(*tasks)

4. **Configure Appropriate Timeouts**

   .. code-block:: python

      # For slow connections
      client = NepseClient(timeout=180.0)

5. **Enable Logging for Debugging**

   .. code-block:: python

      import logging
      logging.basicConfig(level=logging.DEBUG)
      client = NepseClient()
