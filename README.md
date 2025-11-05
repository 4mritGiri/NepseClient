# NEPSE Client

[![PyPI version](https://badge.fury.io/py/nepse-client.svg)](https://badge.fury.io/py/nepse-client)
[![Python](https://img.shields.io/pypi/pyversions/nepse-client.svg)](https://pypi.org/project/nepse-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive, professional-grade Python client library for interacting with the Nepal Stock Exchange (NEPSE) API. Built with modern Python best practices, type hints, and both synchronous and asynchronous support.

## 🌟 Features

- ✨ **Both Sync and Async Support** - Choose the programming paradigm that fits your needs
- 🔒 **Automatic Token Management** - Handles authentication and token refresh automatically
- 📊 **Complete API Coverage** - Access all NEPSE endpoints including market data, company info, floor sheets, and more
- 🛡️ **Robust Error Handling** - Comprehensive exception hierarchy for better error management
- 📝 **Type Hints** - Full type annotations for better IDE support and code quality
- 🔄 **Retry Logic** - Built-in retry mechanisms for network failures
- 📈 **Progress Tracking** - Optional progress bars for long-running operations
- 🧪 **Well Tested** - Comprehensive test suite with high coverage
- 📚 **Excellent Documentation** - Detailed docs with examples

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install nepse-client
```

### From Source

```bash
git clone https://github.com/yourusername/nepse-client.git
cd nepse-client
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## 🚀 Quick Start

### Synchronous Usage

```python
from nepse_client import Nepse

# Initialize client
client = Nepse()

# Get market status
market_status = client.getMarketStatus()
print(f"Market is: {market_status['isOpen']}")

# Get today's prices
prices = client.getPriceVolume()

# Get company list
companies = client.getCompanyList()

# Get floor sheet
floor_sheet = client.getFloorSheet()
```

### Asynchronous Usage

```python
import asyncio
from nepse_client import AsyncNepse

async def main():
    # Initialize client
    client = AsyncNepse()
    
    # Get market status
    market_status = await client.getMarketStatus()
    print(f"Market is: {market_status['isOpen']}")
    
    # Get today's prices
    prices = await client.getPriceVolume()
    
    # Get company list
    companies = await client.getCompanyList()
    
    # Get floor sheet with progress bar
    floor_sheet = await client.getFloorSheet(show_progress=True)

# Run async function
asyncio.run(main())
```

## 📖 Documentation

### Core Methods

#### Market Information

```python
# Get market status (open/closed)
status = client.getMarketStatus()

# Get market summary
summary = client.getSummary()

# Get NEPSE index
index = client.getNepseIndex()

# Get sub-indices
sub_indices = client.getNepseSubIndices()

# Get live market data
live_market = client.getLiveMarket()
```

#### Company Information

```python
# Get list of all companies
companies = client.getCompanyList()

# Get security list
securities = client.getSecurityList()

# Get company details by symbol
details = client.getCompanyDetails('NABIL')

# Get company price history
history = client.getCompanyPriceVolumeHistory(
    symbol='NABIL',
    start_date='2024-01-01',
    end_date='2024-12-31'
)

# Get company financial details
financials = client.getCompanyFinancialDetails(company_id='123')

# Get company AGM information
agm = client.getCompanyAGM(company_id='123')

# Get company dividend information
dividend = client.getCompanyDividend(company_id='123')
```

#### Trading Data

```python
# Get floor sheet
floor_sheet = client.getFloorSheet()

# Get floor sheet for specific company
company_floor_sheet = client.getFloorSheetOf('NABIL', business_date='2024-01-15')

# Get trading average
trading_avg = client.getTradingAverage(business_date='2024-01-15', nDays=180)

# Get market depth
depth = client.getSymbolMarketDepth('NABIL')
```

#### Top Performers

```python
# Get top gainers
gainers = client.getTopGainers()

# Get top losers
losers = client.getTopLosers()

# Get top 10 by trade volume
top_trade = client.getTopTenTradeScrips()

# Get top 10 by transaction count
top_transaction = client.getTopTenTransactionScrips()

# Get top 10 by turnover
top_turnover = client.getTopTenTurnoverScrips()
```

#### News and Announcements

```python
# Get company news
news = client.getCompanyNewsList(page=1, page_size=100, is_strip_tags=True)

# Get news and alerts
alerts = client.getNewsAndAlertList(page=1, page_size=100, is_strip_tags=True)

# Get press releases
press_releases = client.getPressRelease()

# Get NEPSE notices
notices = client.getNepseNotice(page=0)
```

#### Other Data

```python
# Get holiday list
holidays = client.getHolidayList(year=2025)

# Get debenture and bond list
debentures = client.getDebentureAndBondList(type='debenture')

# Get supply and demand
supply_demand = client.getSupplyDemand()
```

### Advanced Features

#### Caching and ID Mappings

```python
# Get company ID to symbol mapping (cached)
company_map = client.getCompanyIDKeyMap()

# Get security ID to symbol mapping (cached)
security_map = client.getSecurityIDKeyMap()

# Force update cache
company_map = client.getCompanyIDKeyMap(force_update=True)

# Get sector-wise scrips
sector_scrips = client.getSectorScrips()
```

#### TLS Verification

```python
# Disable TLS verification (not recommended for production)
client.setTLSVerification(False)

# Re-enable TLS verification
client.setTLSVerification(True)
```

#### Custom Logging

```python
import logging

# Create custom logger
logger = logging.getLogger('my_nepse_app')
logger.setLevel(logging.DEBUG)

# Initialize client with custom logger
client = Nepse()
client.logger = logger
```

## 🏗️ Project Structure

```
nepse-client/
├── nepse_client/
│   ├── __init__.py          # Package entry point
│   ├── client.py            # Base client class
│   ├── sync_client.py       # Synchronous implementation
│   ├── async_client.py      # Asynchronous implementation
│   ├── token_manager.py     # Token management
│   ├── dummy_id_manager.py  # Dummy ID management
│   ├── errors.py            # Custom exceptions
│   └── data/
│       ├── API_ENDPOINTS.json
│       ├── DUMMY_DATA.json
│       ├── HEADERS.json
│       └── css.wasm
├── tests/
│   ├── __init__.py
│   ├── test_sync_client.py
│   ├── test_async_client.py
│   └── test_token_manager.py
├── examples/
│   ├── basic_usage.py
│   ├── async_usage.py
│   └── advanced_examples.py
├── docs/
│   └── ... (Sphinx documentation)
├── setup.py
├── pyproject.toml
├── README.md
├── LICENSE
├── CHANGELOG.md
├── MANIFEST.in
├── .gitignore
├── .pre-commit-config.yaml
└── requirements.txt
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=nepse_client --cov-report=html

# Run specific test file
pytest tests/test_sync_client.py

# Run with verbose output
pytest -v
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and ensure they pass
5. Run code formatters: `black .` and `isort .`
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/nepse-client.git
cd nepse-client

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

## 📝 Code Style

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run all formatters:

```bash
black .
isort .
flake8 .
mypy nepse_client
```

## 🐛 Error Handling

The library provides a comprehensive exception hierarchy:

```python
from nepse_client import (
    NepseError,                  # Base exception
    NepseInvalidClientRequest,   # 400 errors
    NepseTokenExpired,           # 401 errors
    NepseBadGatewayError,        # 502 errors
    NepseServerError,            # Other 5xx errors
    NepseNetworkError            # Network/unexpected errors
)

try:
    data = client.getMarketStatus()
except NepseTokenExpired:
    print("Token expired, will auto-refresh")
except NepseServerError as e:
    print(f"Server error: {e}")
except NepseError as e:
    print(f"NEPSE error: {e}")
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Nepal Stock Exchange for providing the API
- All contributors who have helped improve this library

## 📧 Contact

- **Author**: Your Name
- **Email**: your.email@example.com
- **GitHub**: [@yourusername](https://github.com/yourusername)

## 🔗 Links

- [PyPI Package](https://pypi.org/project/nepse-client/)
- [Documentation](https://nepse-client.readthedocs.io)
- [Issue Tracker](https://github.com/yourusername/nepse-client/issues)
- [Changelog](CHANGELOG.md)

## ⭐ Star History

If you find this library useful, please consider giving it a star on GitHub!