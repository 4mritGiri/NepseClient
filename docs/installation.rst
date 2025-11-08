Installation
============

This guide will help you install **nepse-client** on your system.

Requirements
------------

Before installing nepse-client, ensure you have:

* Python 3.8 or higher
* pip (Python package installer)
* Internet connection

Supported Platforms
~~~~~~~~~~~~~~~~~~~

nepse-client works on:

* **Linux** (Ubuntu, Debian, CentOS, Fedora, etc.)
* **macOS** (10.14 Mojave and later)
* **Windows** (Windows 10 and later)

Installation Methods
--------------------

From PyPI (Recommended)
~~~~~~~~~~~~~~~~~~~~~~~

The easiest way to install nepse-client is from PyPI using pip:

.. code-block:: bash

   pip install nepse-client

This will install the latest stable version along with all required dependencies.

Verify the installation:

.. code-block:: bash

   python -c "from nepse_client import NepseClient; print('Installation successful!')"

Using uv (Fast)
~~~~~~~~~~~~~~~

If you use `uv <https://github.com/astral-sh/uv>`_ for faster Python package management:

.. code-block:: bash

   uv pip install nepse-client

Using poetry
~~~~~~~~~~~~

If you use `Poetry <https://python-poetry.org/>`_ for dependency management:

.. code-block:: bash

   poetry add nepse-client

Using pipenv
~~~~~~~~~~~~

If you use `Pipenv <https://pipenv.pypa.io/>`_:

.. code-block:: bash

   pipenv install nepse-client

From Source
~~~~~~~~~~~

To install from the latest source code:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/4mritgiri/NepseClient.git
   cd nepse-client

   # Install in editable mode
   pip install -e .

Development Installation
~~~~~~~~~~~~~~~~~~~~~~~~

For contributing or development work:

.. code-block:: bash

   # Clone the repository
   git clone https://github.com/4mritgiri/NepseClient.git
   cd nepse-client

   # Install with development dependencies
   pip install -e ".[dev]"

   # Install pre-commit hooks
   pre-commit install

This will install:

* All runtime dependencies
* Testing tools (pytest, pytest-cov)
* Code formatters (black, isort)
* Linters (flake8, mypy)
* Documentation tools (sphinx, sphinx-rtd-theme)

Dependencies
------------

Core Dependencies
~~~~~~~~~~~~~~~~~

nepse-client requires the following packages:

* **httpx** (>=0.28.1) - HTTP client with HTTP/2 support
* **pywasm** (>=2.2.1) - WebAssembly runtime for token parsing
* **tqdm** (>=4.67.1) - Progress bar for long-running operations

These are automatically installed when you install nepse-client.

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~

For development and testing:

* **pytest** - Testing framework
* **pytest-asyncio** - Async test support
* **pytest-cov** - Coverage reporting
* **black** - Code formatter
* **isort** - Import sorter
* **flake8** - Linter
* **mypy** - Type checker
* **sphinx** - Documentation generator

Install all optional dependencies:

.. code-block:: bash

   pip install nepse-client[dev]

Upgrading
---------

To upgrade to the latest version:

.. code-block:: bash

   pip install --upgrade nepse-client

To upgrade to a specific version:

.. code-block:: bash

   pip install nepse-client==1.2.0

Uninstallation
--------------

To remove nepse-client:

.. code-block:: bash

   pip uninstall nepse-client

Virtual Environments
--------------------

We strongly recommend using virtual environments to isolate your project dependencies.

Using venv
~~~~~~~~~~

.. code-block:: bash

   # Create virtual environment
   python -m venv venv

   # Activate (Linux/macOS)
   source venv/bin/activate

   # Activate (Windows)
   venv\Scripts\activate

   # Install nepse-client
   pip install nepse-client

Using conda
~~~~~~~~~~~

.. code-block:: bash

   # Create conda environment
   conda create -n nepse python=3.11

   # Activate environment
   conda activate nepse

   # Install nepse-client
   pip install nepse-client

Troubleshooting
---------------

Import Error
~~~~~~~~~~~~

If you encounter an import error:

.. code-block:: python

   ImportError: No module named 'nepse_client'

**Solution:** Ensure nepse-client is installed in your current Python environment:

.. code-block:: bash

   pip list | grep nepse-client

   # If not found, install it
   pip install nepse-client

SSL Certificate Error
~~~~~~~~~~~~~~~~~~~~~

If you encounter SSL certificate verification errors:

.. code-block:: python

   # Temporarily disable TLS verification (for testing only)
   client = NepseClient()
   client.setTLSVerification(False)

**Note:** Only disable TLS verification for testing. Never use this in production.

Permission Denied
~~~~~~~~~~~~~~~~~

If you get permission errors during installation on Linux/macOS:

.. code-block:: bash

   # Use user installation
   pip install --user nepse-client

   # Or use sudo (not recommended)
   sudo pip install nepse-client

Version Conflicts
~~~~~~~~~~~~~~~~~

If you have dependency conflicts:

.. code-block:: bash

   # Upgrade pip first
   pip install --upgrade pip

   # Try installing with --force-reinstall
   pip install --force-reinstall nepse-client

Verifying Installation
----------------------

After installation, verify everything works:

.. code-block:: python

   from nepse_client import NepseClient, AsyncNepseClient
   from nepse_client import __version__

   print(f"nepse-client version: {__version__}")

   # Test synchronous client
   client = NepseClient()
   print("Synchronous client initialized successfully!")

   # Test asynchronous client
   async_client = AsyncNepseClient()
   print("Asynchronous client initialized successfully!")

Check installed version:

.. code-block:: bash

   pip show nepse-client

Next Steps
----------

Now that you have nepse-client installed:

1. Read the :doc:`quickstart` guide
2. Explore :doc:`examples/basic_usage`
3. Check out the :doc:`api/modules` reference
4. Join the community on `GitHub <https://github.com/4mritgiri/NepseClient>`_

Support
-------

If you encounter any installation issues:

* Check the `GitHub Issues <https://github.com/4mritgiri/NepseClient/issues>`_
* Ask in `GitHub Discussions <https://github.com/4mritgiri/NepseClient/discussions>`_
* Email: amritgiri.dev@gmail.com
