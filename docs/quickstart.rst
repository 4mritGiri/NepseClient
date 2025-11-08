Quickstart Guide
================

Get started with **nepse-client** in just 5 minutes!

Installation
------------

First, install nepse-client:

.. code-block:: bash

   pip install nepse-client

Basic Usage
-----------

Synchronous Client
~~~~~~~~~~~~~~~~~~

The synchronous client is perfect for simple scripts and applications:

.. code-block:: python

   from nepse_client import NepseClient

   # Initialize the client
   client = NepseClient()

   # Get market status
   status = client.getMarketStatus()
   print(f"Market is: {status['isOpen']}")

   # Get market summary
   summary = client.getSummary()
   print(f"Total Turnover: NPR {summary['totalTurnover']:,.2f}")

   # Get top gainers
   gainers = client.getTopGainers()
   print("\nTop 5 Gainers:")
   for stock in gainers[:5]:
      print(f"  {stock['symbol']}: +{stock['percentageChange']}%")

Asynchronous Client
~~~~~~~~~~~~~~~~~~~

The async client is ideal for concurrent operations:

.. code-block:: python

   import asyncio
   from nepse_client import AsyncNepseClient

   async def main():
      # Initialize async client
      client = AsyncNepseClient()

      # Fetch multiple data concurrently
      status, summary, gainers = await asyncio.gather(
         client.getMarketStatus(),
         client.getSummary(),
         client.getTopGainers()
      )

      print(f"Market: {status['isOpen']}")
      print(f"Turnover: NPR {summary['totalTurnover']:,.2f}")
      print(f"Top Gainer: {gainers[0]['symbol']}")

   # Run the async function
   asyncio.run(main())

Common Operations
-----------------

Market Information
~~~~~~~~~~~~~~~~~~

Get current market status and data:

.. code-block:: python

   from nepse_client import NepseClient

   client = NepseClient()

   # Is market open?
   status = client.getMarketStatus()
   is_open = status['isOpen']

   # Market summary
   summary = client.getSummary()
   print(f"Total Trades: {summary['totalTrades']}")
   print(f"Total Turnover: NPR {summary['totalTurnover']:,.2f}")

   # NEPSE index
   index = client.getNepseIndex()
   print(f"Current Index: {index['index']}")
   print(f"Change: {index['percentageChange']}%")

Company Data
~~~~~~~~~~~~

Fetch information about specific companies:

.. code-block:: python

   # Get company details
   nabil = client.getCompanyDetails('NABIL')
   print(f"Company: {nabil['companyName']}")
   print(f"LTP: NPR {nabil['lastTradedPrice']}")
   print(f"Change: {nabil['percentageChange']}%")

   # Get price history
   from datetime import date, timedelta

   end_date = date.today()
   start_date = end_date - timedelta(days=30)

   history = client.getCompanyPriceVolumeHistory(
      symbol='NABIL',
      start_date=start_date,
      end_date=end_date
   )

   print(f"Historical data points: {len(history['content'])}")

Trading Data
~~~~~~~~~~~~

Access trading information:

.. code-block:: python

   # Get floor sheet (all trades)
   floor_sheet = client.getFloorSheet()
   print(f"Total trades today: {len(floor_sheet)}")

   # Get trades for specific company
   nabil_trades = client.getFloorSheetOf('NABIL')
   print(f"NABIL trades: {len(nabil_trades)}")

   # Get market depth
   depth = client.getSymbolMarketDepth('NABIL')
   print(f"Buy Quantity: {depth['buyQuantity']}")
   print(f"Sell Quantity: {depth['sellQuantity']}")

Top Performers
~~~~~~~~~~~~~~

Find the best and worst performing stocks:

.. code-block:: python

   # Top gainers
   gainers = client.getTopGainers()
   print("Top 3 Gainers:")
   for i, stock in enumerate(gainers[:3], 1):
      print(f"{i}. {stock['symbol']}: +{stock['percentageChange']}%")

   # Top losers
   losers = client.getTopLosers()
   print("\nTop 3 Losers:")
   for i, stock in enumerate(losers[:3], 1):
      print(f"{i}. {stock['symbol']}: {stock['percentageChange']}%")

   # Top by turnover
   top_turnover = client.getTopTenTurnoverScrips()
   print("\nTop by Turnover:")
   for i, stock in enumerate(top_turnover[:3], 1):
      print(f"{i}. {stock['symbol']}: NPR {stock['turnover']:,.2f}")

Error Handling
--------------

Always handle errors gracefully:

.. code-block:: python

   from nepse_client import (
      NepseClient,
      NepseError,
      NepseAuthenticationError,
      NepseServerError
   )

   client = NepseClient()

   try:
      details = client.getCompanyDetails('NABIL')
      print(details)

   except NepseAuthenticationError:
      print("Authentication failed - token will auto-refresh")

   except NepseServerError as e:
      print(f"Server error: {e}")

   except NepseError as e:
      print(f"NEPSE error: {e}")

   except Exception as e:
      print(f"Unexpected error: {e}")

Context Managers
----------------

Use context managers for automatic cleanup:

.. code-block:: python

   from nepse_client import NepseClient

   # Automatic resource cleanup
   with NepseClient() as client:
      status = client.getMarketStatus()
      companies = client.getCompanyList()
      print(f"Found {len(companies)} companies")
   # Client automatically closed

   # Async context manager
   import asyncio
   from nepse_client import AsyncNepseClient

   async def main():
      async with AsyncNepseClient() as client:
         status = await client.getMarketStatus()
         print(status)
      # Client automatically closed

   asyncio.run(main())

Configuration
-------------

Custom Timeout
~~~~~~~~~~~~~~

Set custom timeout for requests:

.. code-block:: python

   # 60 second timeout
   client = NepseClient(timeout=60.0)

TLS Verification
~~~~~~~~~~~~~~~~

Control TLS certificate verification:

.. code-block:: python

   client = NepseClient()

   # Disable TLS verification (testing only!)
   client.setTLSVerification(False)

   # Re-enable TLS verification
   client.setTLSVerification(True)

.. warning::
   Never disable TLS verification in production environments!

Custom Logging
~~~~~~~~~~~~~~

Configure custom logging:

.. code-block:: python

   import logging

   # Setup logging
   logging.basicConfig(
      level=logging.INFO,
      format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )

   logger = logging.getLogger('my_app')

   # Initialize client
   client = NepseClient(logger=logger)

Complete Example
----------------

Here's a complete example that demonstrates multiple features:

.. code-block:: python

   from nepse_client import NepseClient
   from datetime import date, timedelta

   def main():
      """Complete example of using nepse-client."""

      # Initialize client
      with NepseClient() as client:
         # Get market status
         print("=" * 50)
         print("MARKET STATUS")
         print("=" * 50)

         status = client.getMarketStatus()
         print(f"Status: {status['isOpen']}")
         print(f"As of: {status['asOf']}")

         # Get market summary
         print("\n" + "=" * 50)
         print("MARKET SUMMARY")
         print("=" * 50)

         summary = client.getSummary()
         print(f"Total Turnover: NPR {summary['totalTurnover']:,.2f}")
         print(f"Total Trades: {summary['totalTrades']:,}")
         print(f"Total Scrips Traded: {summary['totalScripsTraded']}")

         # Get NEPSE index
         print("\n" + "=" * 50)
         print("NEPSE INDEX")
         print("=" * 50)

         index = client.getNepseIndex()
         print(f"Index: {index['index']}")
         print(f"Change: {index['percentageChange']}%")

         # Get top performers
         print("\n" + "=" * 50)
         print("TOP PERFORMERS")
         print("=" * 50)

         gainers = client.getTopGainers()
         print("\nTop 5 Gainers:")
         for i, stock in enumerate(gainers[:5], 1):
            print(f"  {i}. {stock['symbol']}: +{stock['percentageChange']}%")

         losers = client.getTopLosers()
         print("\nTop 5 Losers:")
         for i, stock in enumerate(losers[:5], 1):
            print(f"  {i}. {stock['symbol']}: {stock['percentageChange']}%")

         # Get company details
         print("\n" + "=" * 50)
         print("COMPANY DETAILS (NABIL)")
         print("=" * 50)

         nabil = client.getCompanyDetails('NABIL')
         print(f"Company: {nabil['companyName']}")
         print(f"Sector: {nabil['sectorName']}")
         print(f"LTP: NPR {nabil['lastTradedPrice']}")
         print(f"Change: {nabil['percentageChange']}%")
         print(f"Volume: {nabil['totalTradeQuantity']:,}")

   if __name__ == '__main__':
      main()

Next Steps
----------

Now that you understand the basics:

1. **Explore Examples**

   * :doc:`examples/basic_usage` - More basic examples
   * :doc:`examples/async_usage` - Async patterns
   * :doc:`examples/advanced_examples` - Advanced techniques

2. **Read API Documentation**

   * :doc:`api/nepse_client` - Full API reference
   * :doc:`api/client` - Client classes
   * :doc:`api/errors` - Exception handling

3. **Join the Community**

   * `GitHub Repository <https://github.com/4mritgiri/NepseClient>`_
   * `Issue Tracker <https://github.com/4mritgiri/NepseClient/issues>`_
   * `Discussions <https://github.com/4mritgiri/NepseClient/discussions>`_

Tips and Best Practices
------------------------

1. **Use async for multiple requests** - Much faster than sequential
2. **Cache company lists** - They don't change frequently
3. **Handle errors gracefully** - Network issues happen
4. **Use context managers** - Ensures proper cleanup
5. **Enable logging** - Helps debug issues
6. **Don't disable TLS in production** - Security first!

Troubleshooting
---------------

Import Error
~~~~~~~~~~~~

.. code-block:: bash

   # Make sure package is installed
   pip install nepse-client

   # Verify installation
   python -c "import nepse_client; print(nepse_client.__version__)"

Connection Errors
~~~~~~~~~~~~~~~~~

.. code-block:: python

   # Increase timeout
   client = NepseClient(timeout=120.0)

Rate Limiting
~~~~~~~~~~~~~

.. code-block:: python

   from nepse_client import NepseRateLimitError
   import time

   try:
      data = client.getMarketStatus()
   except NepseRateLimitError as e:
      if e.retry_after:
         time.sleep(e.retry_after)
         # Retry request

Getting Help
------------

If you need help:

* Read the full :doc:`api/modules` documentation
* Check `GitHub Issues <https://github.com/4mritgiri/NepseClient/issues>`_
* Ask in `Discussions <https://github.com/4mritgiri/NepseClient/discussions>`_
* Email: amritgiri.dev@gmail.com

**Ready to build something awesome? Start coding! 🚀**
