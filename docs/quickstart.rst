Quick Start
===========

Here's a simple example of how to use the ``nepse-client`` library.

Synchronous Usage
-----------------

.. code-block:: python

   from nepse_client import Nepse

   # Initialize client
   client = Nepse()

   # Get market status
   market_status = client.getMarketStatus()
   print(f"Market is: {market_status['isOpen']}")

   # Get today's prices
   prices = client.getPriceVolume()

   # Get company list
   companies = client.getCompanyList()

Asynchronous Usage
------------------

.. code-block:: python

   import asyncio
   from nepse_client import AsyncNepse

   async def main():
       # Initialize client
       client = AsyncNepse()

       # Get market status
       market_status = await client.getMarketStatus()
       print(f"Market is: {market_status['isOpen']}")

       # Get today's prices
       prices = await client.getPriceVolume()

       # Get company list
       companies = await client.getCompanyList()

   # Run async function
   asyncio.run(main())
