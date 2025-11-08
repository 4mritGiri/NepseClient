Contributing Guide
==================

We welcome contributions to nepse-client! This guide will help you get started.

Getting Started
---------------

1. **Fork the Repository**

   Visit `nepse-client on GitHub <https://github.com/4mritgiri/NepseClient>`_ and fork it.

2. **Clone Your Fork**

   .. code-block:: bash

      git clone https://github.com/yourusername/nepse-client.git
      cd nepse-client

3. **Create a Branch**

   .. code-block:: bash

      git checkout -b feature/your-feature-name

4. **Install Development Dependencies**

   .. code-block:: bash

      pip install -e ".[dev]"
      pre-commit install

Development Workflow
--------------------

Making Changes
~~~~~~~~~~~~~~

1. Make your changes
2. Write or update tests
3. Run tests locally
4. Update documentation
5. Commit your changes

.. code-block:: bash

   # Run tests
   pytest

   # Check code quality
   black nepse_client tests
   isort nepse_client tests
   flake8 nepse_client tests
   mypy nepse_client

   # Commit
   git add .
   git commit -m "Add: Your descriptive message"

Code Standards
--------------

Style Guidelines
~~~~~~~~~~~~~~~~

* Follow **PEP 8** style guide
* Use **Black** for formatting (line length: 100)
* Sort imports with **isort**
* Add **type hints** to all functions
* Write **Google-style docstrings**

Example:

.. code-block:: python

   def calculate_total(
      values: List[float],
      multiplier: float = 1.0
   ) -> float:
      """
      Calculate the total of values.

      Args:
         values: List of numeric values
         multiplier: Optional multiplier

      Returns:
         Total sum multiplied by multiplier

      Example:
         >>> calculate_total([1, 2, 3], 2.0)
         12.0
      """
      return sum(values) * multiplier

Testing
~~~~~~~

* Write tests for new features
* Maintain >80% test coverage
* Use pytest for testing
* Add both unit and integration tests

.. code-block:: bash

   # Run tests
   pytest

   # Run with coverage
   pytest --cov=nepse_client

   # Run specific test
   pytest tests/test_sync_client.py::test_get_market_status

Documentation
~~~~~~~~~~~~~

* Update docstrings
* Add examples
* Update README if needed
* Update CHANGELOG.md

Pull Request Process
--------------------

1. **Push Your Changes**

   .. code-block:: bash

      git push origin feature/your-feature-name

2. **Create Pull Request**

   * Go to GitHub
   * Click "New Pull Request"
   * Fill in the template
   * Link related issues

3. **Code Review**

   * Address review comments
   * Update as needed
   * Maintain conversation

4. **Merge**

   Once approved, your PR will be merged!

Reporting Issues
----------------

Bug Reports
~~~~~~~~~~~

Use the `bug report template <https://github.com/4mritgiri/NepseClient/issues/new?template=bug_report.md>`_:

* Describe the bug
* Steps to reproduce
* Expected vs actual behavior
* Environment details
* Error messages

Feature Requests
~~~~~~~~~~~~~~~~

Use the `feature request template <https://github.com/4mritgiri/NepseClient/issues/new?template=feature_request.md>`_:

* Describe the feature
* Explain use cases
* Propose implementation
* Consider alternatives

Code of Conduct
---------------

Please follow our `Code of Conduct <https://github.com/4mritgiri/NepseClient/blob/master/CODE_OF_CONDUCT.md>`_.

Be respectful, inclusive, and professional.

Questions?
----------

* Ask in `Discussions <https://github.com/4mritgiri/NepseClient/discussions>`_
* Check the :doc:`quickstart` guide
* Read the :doc:`api/modules` reference

Thank you for contributing! 🎉
