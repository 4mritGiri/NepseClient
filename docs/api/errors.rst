Exception Handling
==================

.. automodule:: nepse_client.exceptions
   :members:
   :undoc-members:
   :show-inheritance:

Exception Hierarchy
-------------------

The nepse-client library uses a comprehensive exception hierarchy::

   NepseError (Base)
   ├── NepseClientError (4xx errors)
   ├── NepseAuthenticationError (401 errors)
   ├── NepseBadGatewayError (502 errors)
   ├── NepseServerError (5xx errors)
   ├── NepseNetworkError (connection errors)
   ├── NepseValidationError (validation errors)
   ├── NepseRateLimitError (429 errors)
   ├── NepseDataNotFoundError (404 errors)
   ├── NepseTimeoutError (timeout errors)
   ├── NepseConnectionError (connection failures)
   └── NepseConfigurationError (config errors)

Base Exception
--------------

NepseError
~~~~~~~~~~

.. autoclass:: nepse_client.NepseError
   :members:
   :undoc-members:
   :show-inheritance:
   :special-members: __init__, __str__, __repr__

   Base exception for all NEPSE-related errors.

   **Attributes:**

   * ``message`` (str): Human-readable error description
   * ``status_code`` (Optional[int]): HTTP status code if applicable
   * ``response_data`` (Optional[Any]): Raw response data from API
   * ``request_data`` (Optional[Dict]): Original request data

   **Example:**

   .. code-block:: python

      from nepse_client import NepseClient, NepseError

      client = NepseClient()

      try:
         data = client.getMarketStatus()
      except NepseError as e:
         print(f"Error: {e}")
         print(f"Status code: {e.status_code}")

Client Errors
-------------

NepseClientError
~~~~~~~~~~~~~~~~

.. autoclass:: nepse_client.NepseClientError
   :members:
   :undoc-members:
   :show-inheritance:

   Raised when client sends an invalid request (4xx errors).

   This typically indicates:

   * Invalid parameters
   * Missing required fields
   * Malformed request data
   * Invalid company symbol

   **Example:**

   .. code-block:: python

      from nepse_client import NepseClient, NepseClientError

      client = NepseClient()

      try:
         # Invalid symbol
         data = client.getCompanyDetails("INVALID")
      except NepseClientError as e:
         print(f"Invalid request: {e}")

NepseValidationError
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: nepse_client.NepseValidationError
   :members:
   :undoc-members:
   :show-inheritance:

   Raised when input validation fails before making API request.

   **Attributes:**

   * ``field`` (Optional[str]): Name of the invalid field
   * ``value`` (Optional[Any]): Invalid value provided

   **Example:**

   .. code-block:: python

      from nepse_client import NepseClient, NepseValidationError

      client = NepseClient()

      try:
         # Invalid date format
         history = client.getCompanyPriceVolumeHistory(
            "NABIL",
            start_date="invalid-date"
         )
      except NepseValidationError as e:
         print(f"Validation error: {e}")
         print(f"Field: {e.field}")

Authentication Errors
---------------------

NepseAuthenticationError
~~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: nepse_client.NepseAuthenticationError
   :members:
   :undoc-members:
   :show-inheritance:

   Raised when access token has expired (401 Unauthorized).

   .. note::
      This exception is typically handled automatically by the client,
      which will refresh the token and retry the request.

   **Example:**

   .. code-block:: python

      from nepse_client import NepseClient, NepseAuthenticationError

      client = NepseClient()

      try:
         data = client.getMarketStatus()
      except NepseAuthenticationError:
         # Token expired - client will auto-refresh
         print("Token expired, retrying...")

Server Errors
-------------

NepseServerError
~~~~~~~~~~~~~~~~

.. autoclass:: nepse_client.NepseServerError
   :members:
   :undoc-members:
   :show-inheritance:

   Generic server error for 5xx status codes.

   Common causes:

   * Internal server error (500)
   * Service unavailable (503)
   * Gateway timeout (504)

   **Recommended action:** Retry with exponential backoff.

   **Example:**

   .. code-block:: python

      from nepse_client import NepseClient, NepseServerError
      import time

      client = NepseClient()

      max_retries = 3
      for attempt in range(max_retries):
         try:
            data = client.getMarketStatus()
            break
         except NepseServerError as e:
            if attempt < max_retries - 1:
               wait_time = 2 ** attempt
               print(f"Server error, retrying in {wait_time}s...")
               time.sleep(wait_time)
            else:
               raise

NepseBadGatewayError
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: nepse_client.NepseBadGatewayError
   :members:
   :undoc-members:
   :show-inheritance:

   Raised when server returns 502 Bad Gateway.

   This typically indicates:

   * Server temporarily unavailable
   * Upstream server issues
   * Network problems between servers

   **Recommended action:** Retry the request after a short delay.

Network Errors
--------------

NepseNetworkError
~~~~~~~~~~~~~~~~~

.. autoclass:: nepse_client.NepseNetworkError
   :members:
   :undoc-members:
   :show-inheritance:

   Raised for general network or unexpected HTTP issues.

   This covers:

   * Connection timeouts
   * DNS resolution failures
   * SSL/TLS errors
   * Unexpected response formats
   * Network interruptions

   **Example:**

   .. code-block:: python

      from nepse_client import NepseClient, NepseNetworkError

      client = NepseClient()

      try:
         data = client.getMarketStatus()
      except NepseNetworkError as e:
         print(f"Network error: {e}")
         print("Check your internet connection")

NepseConnectionError
~~~~~~~~~~~~~~~~~~~~

.. autoclass:: nepse_client.NepseConnectionError
   :members:
   :undoc-members:
   :show-inheritance:

   Raised when connection to NEPSE server fails.

NepseTimeoutError
~~~~~~~~~~~~~~~~~

.. autoclass:: nepse_client.NepseTimeoutError
   :members:
   :undoc-members:
   :show-inheritance:

   Raised when request times out.

   **Attributes:**

   * ``timeout`` (Optional[float]): Timeout value in seconds

   **Example:**

   .. code-block:: python

      from nepse_client import NepseClient, NepseTimeoutError

      # Set custom timeout
      client = NepseClient(timeout=30.0)

      try:
         data = client.getMarketStatus()
      except NepseTimeoutError as e:
         print(f"Request timed out after {e.timeout}s")

Rate Limiting
-------------

NepseRateLimitError
~~~~~~~~~~~~~~~~~~~

.. autoclass:: nepse_client.NepseRateLimitError
   :members:
   :undoc-members:
   :show-inheritance:

   Raised when API rate limit is exceeded (429 Too Many Requests).

   **Attributes:**

   * ``retry_after`` (Optional[int]): Seconds to wait before retrying

   **Example:**

   .. code-block:: python

      from nepse_client import NepseClient, NepseRateLimitError
      import time

      client = NepseClient()

      try:
         data = client.getMarketStatus()
      except NepseRateLimitError as e:
         if e.retry_after:
            print(f"Rate limited. Retry after {e.retry_after}s")
            time.sleep(e.retry_after)
            # Retry request
         else:
            print("Rate limited. Please try again later")

Data Errors
-----------

NepseDataNotFoundError
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: nepse_client.NepseDataNotFoundError
   :members:
   :undoc-members:
   :show-inheritance:

   Raised when requested data is not found.

   This is used when:

   * Company symbol doesn't exist
   * No data available for requested date
   * Empty result sets

   **Attributes:**

   * ``resource`` (Optional[str]): Resource that was not found

   **Example:**

   .. code-block:: python

      from nepse_client import NepseClient, NepseDataNotFoundError

      client = NepseClient()

      try:
         data = client.getFloorSheetOf("INVALID", "2024-01-01")
      except NepseDataNotFoundError as e:
         print(f"Data not found: {e.resource}")

Configuration Errors
--------------------

NepseConfigurationError
~~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: nepse_client.NepseConfigurationError
   :members:
   :undoc-members:
   :show-inheritance:

   Raised when there's an issue with client configuration.

   This includes:

   * Missing required configuration files
   * Invalid configuration values
   * Corrupted data files

Error Handling Best Practices
------------------------------

Catch Specific Exceptions
~~~~~~~~~~~~~~~~~~~~~~~~~

Always catch specific exceptions before general ones:

.. code-block:: python

   from nepse_client import (
      NepseClient,
      NepseError,
      NepseServerError,
      NepseAuthenticationError,
      NepseRateLimitError
   )

   client = NepseClient()

   try:
      data = client.getMarketStatus()
   except NepseAuthenticationError:
      # Handle authentication errors
      print("Authentication failed")
   except NepseRateLimitError as e:
      # Handle rate limiting
      if e.retry_after:
         time.sleep(e.retry_after)
   except NepseServerError:
      # Handle server errors
      print("Server error - try again later")
   except NepseError as e:
      # Handle any other NEPSE errors
      print(f"NEPSE error: {e}")
   except Exception as e:
      # Handle unexpected errors
      print(f"Unexpected error: {e}")

Retry Logic
~~~~~~~~~~~

Implement retry logic for transient errors:

.. code-block:: python

   import time
   from nepse_client import (
      NepseClient,
      NepseServerError,
      NepseNetworkError
   )

   def fetch_with_retry(func, max_retries=3):
      for attempt in range(max_retries):
         try:
            return func()
         except (NepseServerError, NepseNetworkError) as e:
            if attempt < max_retries - 1:
                  wait_time = 2 ** attempt
                  print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                  time.sleep(wait_time)
            else:
                  raise

   client = NepseClient()
   data = fetch_with_retry(client.getMarketStatus)

Logging Errors
~~~~~~~~~~~~~~

Log errors for debugging:

.. code-block:: python

   import logging
   from nepse_client import NepseClient, NepseError

   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   client = NepseClient()

   try:
       data = client.getMarketStatus()
   except NepseError as e:
       logger.error(f"NEPSE error: {e}", exc_info=True)
       # exc_info=True includes full traceback

Graceful Degradation
~~~~~~~~~~~~~~~~~~~~

Provide fallback behavior:

.. code-block:: python

   from nepse_client import NepseClient, NepseError

   client = NepseClient()

   try:
      companies = client.getCompanyList()
   except NepseError:
      # Use cached data or default value
      companies = []
      print("Using cached data due to API error")

   # Continue with application logic
   print(f"Found {len(companies)} companies")
