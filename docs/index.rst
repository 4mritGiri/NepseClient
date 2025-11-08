NEPSE Client Documentation
==========================

.. image:: https://img.shields.io/pypi/v/nepse-client.svg
   :target: https://pypi.org/project/nepse-client/
   :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/nepse-client.svg
   :target: https://pypi.org/project/nepse-client/
   :alt: Python versions

.. image:: https://img.shields.io/github/license/4mritgiri/NepseClient.svg
   :target: https://github.com/4mritgiri/NepseClient/blob/master/LICENSE
   :alt: License

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: black

Welcome to NEPSE Client's documentation! This is a comprehensive, production-ready **unofficial** Python client library for interacting with the Nepal Stock Exchange (NEPSE) API.

.. warning::
   **DISCLAIMER:** This is an **UNOFFICIAL** library and is **NOT affiliated with, endorsed by,
   or officially connected** to Nepal Stock Exchange Limited (NEPSE) or any of its subsidiaries.

   This library is provided for **educational and informational purposes only**. Always verify
   critical data with official NEPSE sources at https://www.nepalstock.com.np

   **Use at your own risk.** See :doc:`license` for full disclaimers.

Overview
--------

**NEPSE Client** provides both synchronous and asynchronous interfaces to access market data, company information, trading details, and more from the Nepal Stock Exchange.

Key Features
~~~~~~~~~~~~

* ✨ **Dual API Support** - Both synchronous and asynchronous clients
* 🔒 **Smart Token Management** - Automatic authentication with token refresh
* 📊 **Complete API Coverage** - Access all NEPSE endpoints
* 🛡️ **Robust Error Handling** - Comprehensive exception hierarchy
* 📝 **Full Type Hints** - Complete type annotations for IDE support
* 🔄 **Automatic Retry Logic** - Built-in exponential backoff
* 📈 **Progress Tracking** - Optional progress bars
* 🧪 **Well Tested** - Comprehensive test suite with >80% coverage
* 🚀 **Production Ready** - Battle-tested and optimized

Quick Example
~~~~~~~~~~~~~

Synchronous usage:

.. code-block:: python

   from nepse_client import NepseClient

   # Initialize client
   client = NepseClient()

   # Get market status
   status = client.getMarketStatus()
   print(f"Market is: {status['isOpen']}")

   # Get company details
   nabil = client.getCompanyDetails('NABIL')
   print(f"NABIL LTP: {nabil['lastTradedPrice']}")

Asynchronous usage:

.. code-block:: python

   import asyncio
   from nepse_client import AsyncNepseClient

   async def main():
      async with AsyncNepseClient() as client:
         # Concurrent requests
         status, summary = await asyncio.gather(
            client.getMarketStatus(),
            client.getSummary()
         )
         print(f"Market: {status['isOpen']}")
         print(f"Turnover: {summary['totalTurnover']}")

   asyncio.run(main())

Installation
~~~~~~~~~~~~

Install from PyPI:

.. code-block:: bash

   pip install nepse-client

Or install from source:

.. code-block:: bash

   git clone https://github.com/4mritgiri/NepseClient.git
   cd nepse-client
   pip install -e .

Documentation Contents
----------------------

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: Usage Examples

   examples/index
   examples/basic_usage
   examples/async_usage
   examples/advanced_examples

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api/modules
   api/nepse_client
   api/client
   api/errors

.. toctree::
   :maxdepth: 1
   :caption: Additional Information

   disclaimer
   changelog
   contributing
   license

Project Links
-------------

* **GitHub Repository:** https://github.com/4mritgiri/NepseClient
* **PyPI Package:** https://pypi.org/project/nepse-client/
* **Issue Tracker:** https://github.com/4mritgiri/NepseClient/issues
* **Discussions:** https://github.com/4mritgiri/NepseClient/discussions

Support
-------

If you find this library helpful:

* ⭐ Star the repository on GitHub
* 🐛 Report bugs and issues
* 💡 Suggest new features
* 🤝 Contribute code improvements
* 📢 Share with others

Indices and Tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

License
-------

This project is licensed under the MIT License - see the LICENSE file for details.

Authors
-------

* **Amrit Giri** - *Initial work* - `@4mritgiri <https://github.com/4mritgiri>`_

Acknowledgments
---------------

* Nepal Stock Exchange for providing the API
* All contributors who have helped improve this library
* The Python community for excellent tools and libraries
