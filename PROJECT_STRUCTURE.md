# Project structure tree view

```sh
nepse-client/
│
├── nepse_client/                      # Main package directory
│   ├── __init__.py                    # Package entry point, exports
│   ├── client.py                      # Base client class
│   ├── sync_client.py                 # Synchronous client implementation
│   ├── async_client.py                # Asynchronous client implementation
│   ├── token_manager.py               # Token management (sync & async)
│   ├── dummy_id_manager.py            # Dummy ID management (sync & async)
│   ├── errors.py                      # Custom exception classes
│   ├── py.typed                       # PEP 561 marker for type hints
│   │
│   └── data/                          # Data files
│       ├── API_ENDPOINTS.json         # API endpoint configurations
│       ├── DUMMY_DATA.json            # Dummy data for calculations
│       ├── HEADERS.json               # HTTP headers template
│       └── css.wasm                   # WebAssembly for token parsing
│
├── tests/                             # Test suite
│   ├── __init__.py
│   ├── conftest.py                    # Pytest configuration & fixtures
│   ├── test_sync_client.py            # Synchronous client tests
│   ├── test_async_client.py           # Asynchronous client tests
│   ├── test_token_manager.py          # Token manager tests
│   ├── test_dummy_id_manager.py       # Dummy ID manager tests
│   ├── test_errors.py                 # Exception tests
│   └── test_integration.py            # Integration tests
│
├── examples/                          # Usage examples
│   ├── __init__.py
│   ├── basic_usage.py                 # Basic examples (sync & async)
│   ├── advanced_usage.py              # Advanced usage patterns
│   ├── error_handling.py              # Error handling examples
│   ├── batch_operations.py            # Batch data fetching
│   └── django_integration.py          # Django integration example
│
├── docs/                              # Documentation
│   ├── conf.py                        # Sphinx configuration
│   ├── index.rst                      # Documentation index
│   ├── installation.rst               # Installation guide
│   ├── quickstart.rst                 # Quick start guide
│   ├── api/                           # API documentation
│   │   ├── client.rst
│   │   ├── errors.rst
│   │   └── utils.rst
│   ├── examples/                      # Example documentation
│   └── changelog.rst                  # Changelog
│
├── .github/                           # GitHub specific files
│   ├── workflows/                     # GitHub Actions
│   │   ├── tests.yml                  # Run tests on PR/push
│   │   ├── publish.yml                # Publish to PyPI
│   │   └── docs.yml                   # Build documentation
│   ├── ISSUE_TEMPLATE/               # Issue templates
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── pull_request_template.md       # PR template
│
├── pyproject.toml                     # Modern build configuration
├── MANIFEST.in                        # Package data inclusion
├── requirements.txt                   # Runtime dependencies
├── requirements-dev.txt               # Development dependencies
├── .gitignore                         # Git ignore rules
├── .pre-commit-config.yaml            # Pre-commit hooks
├── README.md                          # Main readme
├── CHANGELOG.md                       # Version history
├── LICENSE                            # MIT License
├── CONTRIBUTING.md                    # Contribution guidelines
├── CODE_OF_CONDUCT.md                 # Code of conduct
├── DEPLOYMENT.md                      # Deployment guide
└── PROJECT_STRUCTURE.md               # This file
```
