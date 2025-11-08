Changelog
=========

All notable changes to nepse-client will be documented in this file.

The format is based on `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_,
and this project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

[Unreleased]
------------

Planned features for future releases:

* WebSocket support for real-time data streaming
* Advanced caching layer with TTL support
* CLI tool for command-line queries
* Data export utilities (CSV, Excel, JSON)
* Django/Flask integration packages
* Interactive Jupyter notebook examples
* Prometheus metrics export
* Request rate limiting with automatic backoff

[1.0.0] - 2024-01-15
--------------------

Initial release of nepse-client with complete NEPSE API coverage.

Added
~~~~~

* **Core Functionality**

  * Synchronous client (NepseClient) for blocking operations
  * Asynchronous client (AsyncNepseClient) for concurrent operations
  * Automatic token management with refresh logic
  * Dummy ID management for POST request payloads

* **API Coverage**

  * Market status and summary endpoints
  * Company information and details
  * Historical price and volume data
  * Floor sheet (trading) data with pagination
  * Market depth data
  * Top performers (gainers, losers, turnover)
  * News and announcements
  * Holiday lists
  * Debenture and bond information
  * NEPSE indices and sub-indices

* **Error Handling**

  * Comprehensive exception hierarchy
  * Automatic retry logic with exponential backoff
  * Network error handling
  * Rate limiting detection
  * TLS verification controls

* **Developer Experience**

  * Full type hints for all public APIs
  * Context manager support (``with`` and ``async with``)
  * Progress bars for long-running operations
  * Configurable logging
  * Custom timeout settings

* **Documentation**

  * Complete Sphinx documentation
  * API reference with examples
  * Quickstart guide
  * Installation instructions
  * Usage examples (basic, async, advanced)

* **Testing**

  * Comprehensive test suite with pytest
  * Unit tests for all modules
  * Integration tests
  * Test coverage >80%

* **CI/CD**

  * GitHub Actions workflows for testing
  * Automated PyPI publishing
  * Documentation auto-deployment
  * Pre-commit hooks configuration

* **Code Quality**

  * Black code formatting
  * isort import sorting
  * flake8 linting
  * mypy type checking
  * bandit security scanning

[0.9.0] - 2024-01-10 [BETA]
----------------------------

Beta release for testing and feedback.

Added
~~~~~

* Basic synchronous client implementation
* Core API endpoints
* Token management
* Basic error handling
* Initial documentation

Changed
~~~~~~~

* Improved API response parsing
* Enhanced error messages
* Better logging

Fixed
~~~~~

* Token refresh issues
* Date parsing errors
* TLS verification bugs

[0.5.0] - 2024-01-05 [ALPHA]
-----------------------------

Alpha release for early adopters.

Added
~~~~~

* Proof of concept implementation
* Basic market data endpoints
* Simple authentication flow

Known Issues
~~~~~~~~~~~~

* Limited error handling
* No async support
* Incomplete documentation

Migration Guides
----------------

Migrating to 1.0.0 from 0.x
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Version 1.0.0 introduces breaking changes. Follow this guide to migrate:

**1. Import Changes**

.. code-block:: python

   # Old (0.x)
   from nepse_client import Nepse

   # New (1.0.0)
   from nepse_client import NepseClient

**2. Client Initialization**

.. code-block:: python

   # Old (0.x)
   client = Nepse()

   # New (1.0.0)
   client = NepseClient()

**3. Exception Handling**

.. code-block:: python

   # Old (0.x)
   from nepse_client.errors import NepseException

   # New (1.0.0)
   from nepse_client import NepseError

**4. Async Support**

.. code-block:: python

   # New in 1.0.0
   from nepse_client import AsyncNepseClient

   async def main():
      async with AsyncNepseClient() as client:
         data = await client.getMarketStatus()

Deprecation Warnings
--------------------

The following features are deprecated and will be removed in future versions:

None currently.

Version History
---------------

.. list-table::
   :header-rows: 1
   :widths: 15 15 15 55

   * - Version
      - Date
      - Status
      - Notes
   * - 1.0.0
      - 2024-01-15
      - Stable
      - Initial stable release
   * - 0.9.0
      - 2024-01-10
      - Beta
      - Beta testing
   * - 0.5.0
      - 2024-01-05
      - Alpha
      - Early preview

Support Policy
--------------

**Stable Releases** (1.x.x)

* Security updates: 2 years
* Bug fixes: 1 year
* Feature updates: 6 months

**Beta Releases** (0.9.x)

* Limited support
* Migration path provided

**Alpha Releases** (0.x.x)

* No support guarantee
* Breaking changes expected

Contributing
------------

We welcome contributions! Please see our `Contributing Guide <https://github.com/4mritgiri/NepseClient/blob/master/CONTRIBUTING.md>`_ for details.

To report bugs or suggest features:

* `GitHub Issues <https://github.com/4mritgiri/NepseClient/issues>`_
* `GitHub Discussions <https://github.com/4mritgiri/NepseClient/discussions>`_

Release Process
---------------

Our release process:

1. **Development** - Features developed in feature branches
2. **Testing** - Comprehensive testing on develop branch
3. **Beta Release** - Released as 0.9.x for testing
4. **Stable Release** - Tagged as 1.x.x after validation
5. **Documentation** - Auto-deployed to Read the Docs
6. **PyPI** - Auto-published via GitHub Actions

Semantic Versioning
~~~~~~~~~~~~~~~~~~~

We follow `Semantic Versioning <https://semver.org/>`_:

* **MAJOR** (1.x.x) - Breaking changes
* **MINOR** (x.1.x) - New features, backwards compatible
* **PATCH** (x.x.1) - Bug fixes, backwards compatible

Links
-----

* `Full Changelog on GitHub <https://github.com/4mritgiri/NepseClient/blob/master/CHANGELOG.md>`_
* `Release Notes <https://github.com/4mritgiri/NepseClient/releases>`_
* `Migration Guides <https://nepse-client.readthedocs.io/en/latest/changelog.html#migration-guides>`_
