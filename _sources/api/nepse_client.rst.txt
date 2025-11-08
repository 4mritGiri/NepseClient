nepse_client Package
====================

.. automodule:: nepse_client
   :members:
   :undoc-members:
   :show-inheritance:

Main Classes
------------

NepseClient
~~~~~~~~~~~

.. autoclass:: nepse_client.NepseClient
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __enter__, __exit__

   The synchronous client for NEPSE API.

   **Example:**

   .. code-block:: python

      from nepse_client import NepseClient

      client = NepseClient()
      status = client.getMarketStatus()
      print(status)

AsyncNepseClient
~~~~~~~~~~~~~~~~

.. autoclass:: nepse_client.AsyncNepseClient
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __aenter__, __aexit__

   The asynchronous client for NEPSE API.

   **Example:**

   .. code-block:: python

      import asyncio
      from nepse_client import AsyncNepseClient

      async def main():
         client = AsyncNepseClient()
         status = await client.getMarketStatus()
         print(status)

      asyncio.run(main())

Package Metadata
----------------

Version
~~~~~~~

.. autodata:: nepse_client.__version__
   :annotation: = 1.0.0

Author
~~~~~~

.. autodata:: nepse_client.__author__
   :annotation: = Amrit Giri

Submodules
----------

client
~~~~~~

.. automodule:: nepse_client.client
   :members:
   :undoc-members:
   :show-inheritance:

sync_client
~~~~~~~~~~~

.. automodule:: nepse_client.sync_client
   :members:
   :undoc-members:
   :show-inheritance:

async_client
~~~~~~~~~~~~

.. automodule:: nepse_client.async_client
   :members:
   :undoc-members:
   :show-inheritance:

token_manager
~~~~~~~~~~~~~

.. automodule:: nepse_client.token_manager
   :members:
   :undoc-members:
   :show-inheritance:

dummy_id_manager
~~~~~~~~~~~~~~~~

.. automodule:: nepse_client.dummy_id_manager
   :members:
   :undoc-members:
   :show-inheritance:

exceptions
~~~~~~~~~~

.. automodule:: nepse_client.exceptions
   :members:
   :undoc-members:
   :show-inheritance:
