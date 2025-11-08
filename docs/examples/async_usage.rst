Asynchronous Usage
==================

Examples using the async client for concurrent operations.

Basic Async Example
-------------------

.. code-block:: python

   import asyncio
   from nepse_client import AsyncNepseClient

   async def main():
      async with AsyncNepseClient() as client:
         status = await client.getMarketStatus()
         print(status)

   asyncio.run(main())

See :download:`async_usage.py <../../examples/basic_usage.py>` for more.
