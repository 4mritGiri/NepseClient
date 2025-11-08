Usage Examples
==============

This section provides practical examples for using nepse-client in various scenarios.

.. toctree::
   :maxdepth: 2

   basic_usage
   async_usage
   advanced_examples

Example Categories
------------------

Basic Usage
~~~~~~~~~~~

Learn the fundamentals:

* :doc:`basic_usage` - Simple synchronous examples
* Market data fetching
* Company information
* Error handling basics

Asynchronous Usage
~~~~~~~~~~~~~~~~~~

Master async patterns:

* :doc:`async_usage` - Concurrent operations
* Multiple requests
* Performance optimization
* Context managers

Advanced Examples
~~~~~~~~~~~~~~~~~

Complex scenarios:

* :doc:`advanced_examples` - Real-world applications
* Portfolio management
* Data analysis
* Custom integrations

Quick Examples
--------------

Get Market Status
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from nepse_client import NepseClient

   client = NepseClient()
   status = client.getMarketStatus()

   print(f"Market is: {status['isOpen']}")
   print(f"As of: {status['asOf']}")

Get Top Gainers
~~~~~~~~~~~~~~~

.. code-block:: python

   from nepse_client import NepseClient

   client = NepseClient()
   gainers = client.getTopGainers()

   print("Top 5 Gainers:")
   for i, stock in enumerate(gainers[:5], 1):
      print(f"{i}. {stock['symbol']}: +{stock['percentageChange']}%")

Async Concurrent Requests
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import asyncio
   from nepse_client import AsyncNepseClient

   async def main():
      async with AsyncNepseClient() as client:
         # Fetch multiple data concurrently
         status, summary, gainers = await asyncio.gather(
            client.getMarketStatus(),
            client.getSummary(),
            client.getTopGainers()
         )

         print(f"Market: {status['isOpen']}")
         print(f"Turnover: NPR {summary['totalTurnover']:,.2f}")
         print(f"Top Gainer: {gainers[0]['symbol']}")

   asyncio.run(main())

Example Projects
----------------

GitHub Repository
~~~~~~~~~~~~~~~~~

Find complete example projects in the `examples/ directory <https://github.com/4mritgiri/NepseClient/tree/master/examples>`_:

* ``basic_usage.py`` - Fundamental examples
* ``async_usage.py`` - Async patterns
* ``advanced_usage.py`` - Complex scenarios
* ``error_handling.py`` - Error management
* ``django_integration.py`` - Django integration

Running Examples
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # Clone repository
   git clone https://github.com/4mritgiri/NepseClient.git
   cd nepse-client

   # Install
   pip install -e .

   # Run examples
   python examples/basic_usage.py
   python examples/async_usage.py

Community Examples
------------------

Check out community-contributed examples:

* `GitHub Discussions <https://github.com/4mritgiri/NepseClient/discussions>`_
* User-submitted examples
* Integration patterns
* Use case studies

Contributing Examples
---------------------

Have an interesting use case? Share it!

1. Create your example
2. Test thoroughly
3. Add documentation
4. Submit a pull request

See :doc:`../contributing` for guidelines.

Need Help?
----------

* Check the :doc:`../quickstart` guide
* Read the :doc:`../api/modules` reference
* Ask in `GitHub Discussions <https://github.com/4mritgiri/NepseClient/discussions>`_
* Open an `Issue <https://github.com/4mritgiri/NepseClient/issues>`_
