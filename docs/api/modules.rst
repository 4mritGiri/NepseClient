API Reference
=============

This section contains the complete API reference for nepse-client.

Overview
--------

The nepse-client library is organized into several modules:

.. toctree::
   :maxdepth: 2

   nepse_client
   client
   errors
   utils

Main Modules
------------

nepse_client
~~~~~~~~~~~~

The main module containing the public API:

.. autosummary::
   :toctree: generated
   :recursive:

   nepse_client.NepseClient
   nepse_client.AsyncNepseClient

Client Modules
~~~~~~~~~~~~~~

Base and implementation classes:

.. autosummary::
   :toctree: generated

   nepse_client.client
   nepse_client.sync_client
   nepse_client.async_client

Support Modules
~~~~~~~~~~~~~~~

Token and ID management:

.. autosummary::
   :toctree: generated

   nepse_client.token_manager
   nepse_client.dummy_id_manager

Exception Handling
~~~~~~~~~~~~~~~~~~

Custom exceptions for error handling:

.. autosummary::
   :toctree: generated

   nepse_client.exceptions

Package Information
-------------------

Version Information
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from nepse_client import __version__, __author__

   print(__version__)  # e.g., '1.0.0'
   print(__author__)   # e.g., 'Amrit Giri'

Available Exports
~~~~~~~~~~~~~~~~~

The following are available from the main package:

**Client Classes:**

* :class:`nepse_client.NepseClient` - Synchronous client
* :class:`nepse_client.AsyncNepseClient` - Asynchronous client

**Exception Classes:**

* :class:`nepse_client.NepseError` - Base exception
* :class:`nepse_client.NepseClientError` - Client errors (4xx)
* :class:`nepse_client.NepseServerError` - Server errors (5xx)
* :class:`nepse_client.NepseAuthenticationError` - Authentication errors
* :class:`nepse_client.NepseNetworkError` - Network errors
* :class:`nepse_client.NepseValidationError` - Validation errors
* :class:`nepse_client.NepseBadGatewayError` - Bad gateway errors
* :class:`nepse_client.NepseRateLimitError` - Rate limit errors
* :class:`nepse_client.NepseDataNotFoundError` - Data not found errors
* :class:`nepse_client.NepseTimeoutError` - Timeout errors
* :class:`nepse_client.NepseConnectionError` - Connection errors
* :class:`nepse_client.NepseConfigurationError` - Configuration errors

Usage Examples
--------------

Basic Import
~~~~~~~~~~~~

.. code-block:: python

   from nepse_client import NepseClient, AsyncNepseClient

   # Synchronous client
   client = NepseClient()

   # Asynchronous client
   async_client = AsyncNepseClient()

Exception Handling
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from nepse_client import (
      NepseClient,
      NepseError,
      NepseServerError,
      NepseAuthenticationError
   )

   client = NepseClient()

   try:
      data = client.getMarketStatus()
   except NepseAuthenticationError:
      print("Authentication failed")
   except NepseServerError:
      print("Server error")
   except NepseError as e:
      print(f"General error: {e}")

Type Hints
~~~~~~~~~~

All public APIs include type hints:

.. code-block:: python

   from nepse_client import NepseClient
   from typing import Dict, List, Any

   client: NepseClient = NepseClient()

   # Return types are properly annotated
   status: Dict[str, Any] = client.getMarketStatus()
   companies: List[Dict[str, Any]] = client.getCompanyList()

Module Index
------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
