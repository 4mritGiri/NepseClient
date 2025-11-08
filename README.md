# NEPSE Client

[![Tests](https://github.com/4mritgiri/NepseClient/workflows/Tests/badge.svg)](https://github.com/4mritgiri/NepseClient/actions/workflows/tests.yml)
[![Publish](https://github.com/4mritgiri/NepseClient/workflows/Publish%20to%20PyPI/badge.svg)](https://github.com/4mritgiri/NepseClient/actions/workflows/publish.yml)
[![Documentation](https://github.com/4mritgiri/NepseClient/workflows/Documentation/badge.svg)](https://github.com/4mritgiri/NepseClient/actions/workflows/docs.yml)
[![PyPI version](https://badge.fury.io/py/nepse-client.svg)](https://badge.fury.io/py/nepse-client)
[![Python versions](https://img.shields.io/pypi/pyversions/nepse-client.svg)](https://pypi.org/project/nepse-client/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A comprehensive, production-ready Python client library for interacting with the Nepal Stock Exchange (NEPSE) API. Built with
modern Python best practices, full type hints, and both synchronous and asynchronous support.

## 🌟 Features

- ✨ **Dual API Support** - Both synchronous and asynchronous clients for flexible integration
- 🔒 **Smart Token Management** - Automatic authentication with token refresh and caching
- 📊 **Complete API Coverage** - Access all NEPSE endpoints: market data, company info, floor sheets, news, and more
- 🛡️ **Robust Error Handling** - Comprehensive exception hierarchy with automatic retries
- 📝 **Full Type Hints** - Complete type annotations for excellent IDE support and type safety
- 🔄 **Automatic Retry Logic** - Built-in exponential backoff for network failures
- 📈 **Progress Tracking** - Optional progress bars for long-running operations
- 🧪 **Well Tested** - Comprehensive test suite with >80% coverage
- 🚀 **Production Ready** - Battle-tested, secure, and optimized for performance
- 📚 **Excellent Documentation** - Detailed docs, examples, and API reference

## 📦 Installation

### From PyPI (Recommended)

```bash
pip install nepse-client
```

### Using uv (Fast)

```bash
uv pip install nepse-client
```

### From Source

```bash
git clone https://github.com/4mritgiri/NepseClient.git
cd nepse-client
pip install -e .
```

### Development Installation

```bash
# Clone and install with dev dependencies
git clone https://github.com/4mritgiri/NepseClient.git
cd nepse-client
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## 🚀 Quick Start

### Synchronous Usage

```python
from nepse_client import NepseClient

# Initialize client
client = NepseClient()

# Optional: Disable TLS verification (for testing only)
client.setTLSVerification(False)

# Get market status
market_status = client.getMarketStatus()
print(f"Market is: {market_status['isOpen']}")

# Get company details
nabil = client.getCompanyDetails('NABIL')
print(f"NABIL LTP: {nabil['lastTradedPrice']}")

# Get today's top gainers
gainers = client.getTopGainers()
for stock in gainers[:5]:
    print(f"{stock['symbol']}: +{stock['percentageChange']}%")
```

### Asynchronous Usage

```python
import asyncio
from nepse_client import AsyncNepseClient

async def main():
    # Initialize async client
    async with AsyncNepseClient() as client:
        # Optional: Disable TLS verification (for testing only)
        client.setTLSVerification(False)

        # Concurrent requests for better performance
        market_status, summary, gainers = await asyncio.gather(
            client.getMarketStatus(),
            client.getSummary(),
            client.getTopGainers()
        )

        print(f"Market: {market_status['isOpen']}")
        print(f"Turnover: {summary['totalTurnover']}")
        print(f"Top Gainer: {gainers[0]['symbol']}")

# Run async function
asyncio.run(main())
```

### Context Manager Support

```python
# Automatic resource cleanup with context manager
with NepseClient() as client:
    status = client.getMarketStatus()
    companies = client.getCompanyList()
# Client automatically closed
```

## 📖 API Documentation

### Market Information

```python
# Get market status (open/closed)
status = client.getMarketStatus()

# Get market summary (turnover, trades, etc.)
summary = client.getSummary()

# Get NEPSE index
index = client.getNepseIndex()

# Get sub-indices (sector indices)
sub_indices = client.getNepseSubIndices()

# Get live market data
live_market = client.getLiveMarket()

# Get price volume data
price_volume = client.getPriceVolume()

# Get supply and demand data
supply_demand = client.getSupplyDemand()
```

### Company Information

```python
# Get list of all companies
companies = client.getCompanyList()

# Get security list (non-delisted securities)
securities = client.getSecurityList()

# Get company details by symbol
details = client.getCompanyDetails('NABIL')

# Get company price history
from datetime import date, timedelta
end_date = date.today()
start_date = end_date - timedelta(days=365)

history = client.getCompanyPriceVolumeHistory(
    symbol='NABIL',
    start_date=start_date,
    end_date=end_date
)

# Get daily price graph data
graph = client.getDailyScripPriceGraph('NABIL')

# Get company financial details
financials = client.getCompanyFinancialDetails(company_id='123')

# Get company AGM information
agm = client.getCompanyAGM(company_id='123')

# Get company dividend information
dividend = client.getCompanyDividend(company_id='123')

# Get company market depth
market_depth = client.getCompanyMarketDepth(company_id='123')
```

### Trading Data

```python
# Get complete floor sheet (all trades)
floor_sheet = client.getFloorSheet()

# Get floor sheet with progress bar
floor_sheet = client.getFloorSheet(show_progress=True)

# Get floor sheet for specific company
company_trades = client.getFloorSheetOf(
    symbol='NABIL',
    business_date='2024-01-15'
)

# Get trading average
trading_avg = client.getTradingAverage(
    business_date='2024-01-15',
    nDays=180
)

# Get market depth for symbol
depth = client.getSymbolMarketDepth('NABIL')
```

### Top Performers

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

### News and Announcements

```python
# Get company news with pagination
news = client.getCompanyNewsList(
    page=1,
    page_size=100,
    is_strip_tags=True  # Remove HTML tags
)

# Get news and alerts
alerts = client.getNewsAndAlertList(
    page=1,
    page_size=100,
    is_strip_tags=True
)

# Get press releases
press_releases = client.getPressRelease()

# Get NEPSE notices
notices = client.getNepseNotice(page=0)
```

### Other Data

```python
# Get holiday list for specific year
holidays = client.getHolidayList(year=2025)

# Get debenture and bond list
debentures = client.getDebentureAndBondList(type='debenture')
bonds = client.getDebentureAndBondList(type='bond')

# Get price volume history for specific date
price_history = client.getPriceVolumeHistory(business_date='2024-01-15')
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
# Returns: {'Commercial Banks': ['NABIL', 'SCB', ...], ...}
```

#### Custom Configuration

```python
import logging

# Custom logger
logger = logging.getLogger('my_nepse_app')
logger.setLevel(logging.DEBUG)

# Initialize with custom settings
client = NepseClient(
    logger=logger,
    mask_request_data=True,  # Mask sensitive data in logs
    timeout=120.0            # Request timeout in seconds
)

# Disable TLS verification (not recommended for production)
client.setTLSVerification(False)

# Re-enable TLS verification
client.setTLSVerification(True)
```

## 🔥 Advanced Usage Examples

### Portfolio Value Calculator

```python
def calculate_portfolio_value(portfolio):
    """
    Calculate total portfolio value.

    Args:
        portfolio: Dict of {symbol: quantity}

    Returns:
        Total value in NPR
    """
    client = NepseClient()
    total = 0

    for symbol, quantity in portfolio.items():
        details = client.getCompanyDetails(symbol)
        price = float(details['lastTradedPrice'])
        value = price * quantity
        total += value
        print(f"{symbol}: {quantity} @ NPR {price} = NPR {value:,.2f}")

    return total

# Example
portfolio = {'NABIL': 100, 'NICA': 50, 'SCB': 75}
total_value = calculate_portfolio_value(portfolio)
print(f"\nTotal Portfolio Value: NPR {total_value:,.2f}")
```

### Async Batch Operations

```python
import asyncio
from nepse_client import AsyncNepseClient

async def fetch_multiple_companies(symbols):
    """Fetch details for multiple companies concurrently."""
    async with AsyncNepseClient() as client:
        # Create tasks for all symbols
        tasks = [client.getCompanyDetails(symbol) for symbol in symbols]

        # Fetch all concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                print(f"{symbol}: Error - {result}")
            else:
                ltp = result['lastTradedPrice']
                print(f"{symbol}: NPR {ltp}")

# Run
symbols = ['NABIL', 'NICA', 'SCB', 'EBL', 'ADBL']
asyncio.run(fetch_multiple_companies(symbols))
```

### Real-time Market Monitoring

```python
import asyncio
from nepse_client import AsyncNepseClient

async def monitor_market(interval=60):
    """Monitor market status continuously."""
    async with AsyncNepseClient() as client:
        while True:
            try:
                status = await client.getMarketStatus()
                summary = await client.getSummary()

                print(f"[{status['asOf']}] Market: {status['isOpen']}")
                print(f"Turnover: NPR {summary['totalTurnover']:,.2f}")

                await asyncio.sleep(interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(interval)

asyncio.run(monitor_market())
```

## 🐛 Error Handling

The library provides a comprehensive exception hierarchy:

```python
from nepse_client import (
    NepseError,                  # Base exception
    NepseClientError,            # 400 errors
    NepseAuthenticationError,    # 401 errors
    NepseBadGatewayError,        # 502 errors
    NepseServerError,            # 5xx errors
    NepseNetworkError,           # Network/connection errors
    NepseValidationError,        # Input validation errors
    NepseRateLimitError,         # Rate limit exceeded
    NepseDataNotFoundError,      # Data not found
    NepseTimeoutError,           # Request timeout
)

# Example error handling
try:
    data = client.getCompanyDetails('INVALID')
except NepseAuthenticationError:
    print("Authentication failed - token will auto-refresh")
except NepseDataNotFoundError:
    print("Company symbol not found")
except NepseRateLimitError as e:
    print(f"Rate limited - retry after {e.retry_after}s")
except NepseServerError as e:
    print(f"Server error: {e}")
except NepseError as e:
    print(f"NEPSE error: {e}")
```

## 🧪 Testing

```bash
# Install test dependencies
pip install -e ".[dev]"

# Run all tests
pytest

# Run with coverage
pytest --cov=nepse_client --cov-report=html

# Run specific test file
pytest tests/test_sync_client.py -v

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

## 📊 Code Quality

This project maintains high code quality standards:

```bash
# Format code
black nepse_client tests examples
isort nepse_client tests examples

# Lint code
flake8 nepse_client tests --max-line-length=100

# Type check
mypy nepse_client --ignore-missing-imports

# Security check
bandit -r nepse_client

# Run all pre-commit hooks
pre-commit run --all-files
```

## 🏗️ Project Structure

```sh
nepse-client/
├── nepse_client/            # Main package
│   ├── __init__.py          # Package exports
│   ├── client.py            # Base client
│   ├── sync_client.py       # Sync implementation
│   ├── async_client.py      # Async implementation
│   ├── token_manager.py     # Token management
│   ├── dummy_id_manager.py  # Dummy ID management
│   ├── exceptions.py        # Custom exceptions
│   ├── py.typed             # Type hint marker
│   └── data/                # Configuration files
├── tests/                   # Test suite
├── examples/                # Usage examples
├── docs/                    # Documentation
├── .github/                 # GitHub Actions
│   ├── workflows/           # CI/CD pipelines
│   └── ISSUE_TEMPLATE/      # Issue templates
├── pyproject.toml           # Project config
└── README.md                # This file
```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

### Getting Started

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/yourusername/nepse-client.git`
3. **Create** a branch: `git checkout -b feature/amazing-feature`
4. **Install** dev dependencies: `pip install -e ".[dev]"`
5. **Install** pre-commit: `pre-commit install`

### Making Changes

1. Make your changes
2. Add tests for new functionality
3. Run tests: `pytest`
4. Run code quality checks: `pre-commit run --all-files`
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. **Create** a Pull Request

### Code Standards

- Follow **PEP 8** style guide
- Use **Black** for formatting (line length: 100)
- Add **type hints** to all functions
- Write **docstrings** (Google style)
- Maintain **test coverage** above 80%
- Update **documentation** for new features

### Pull Request Checklist

- [ ] Tests pass locally
- [ ] Code formatted with Black and isort
- [ ] Type hints added
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] No linting errors
- [ ] Test coverage maintained

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📝 Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/4mritgiri/NepseClient.git
cd nepse-client

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Verify installation
pytest --version
black --version
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=nepse_client --cov-report=term-missing

# Run specific test
pytest tests/test_sync_client.py::test_get_market_status

# Run in watch mode (requires pytest-watch)
ptw
```

### Building Documentation

```bash
# Install documentation dependencies
pip install sphinx sphinx-rtd-theme

# Build HTML docs
cd docs
make html

# Open in browser
open _build/html/index.html  # macOS
xdg-open _build/html/index.html  # Linux
```

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Nepal Stock Exchange** for providing the API
- All **contributors** who have helped improve this library
- The **Python community** for excellent tools and libraries

## 👨‍💻 Author

 > **Amrit Giri**

- GitHub: [@4mritgiri](https://github.com/4mritgiri)
- Email: <amritgiri.dev@gmail.com>

## 🔗 Links

- 📦 [PyPI Package](https://pypi.org/project/nepse-client/)
- 📖 [Documentation](https://nepse-client.readthedocs.io)
- 🐛 [Issue Tracker](https://github.com/4mritgiri/NepseClient/issues)
- 💬 [Discussions](https://github.com/4mritgiri/NepseClient/discussions)
- 📋 [Changelog](CHANGELOG.md)
- 🤝 [Contributing Guide](CONTRIBUTING.md)

## 📈 Project Stats

![GitHub stars](https://img.shields.io/github/stars/4mritgiri/NepseClient?style=social)
![GitHub forks](https://img.shields.io/github/forks/4mritgiri/NepseClient?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/4mritgiri/NepseClient?style=social)
![GitHub issues](https://img.shields.io/github/issues/4mritgiri/NepseClient)
![GitHub pull requests](https://img.shields.io/github/issues-pr/4mritgiri/NepseClient)

## 💖 Support

If you find this library helpful, please consider:

- ⭐ **Starring** the repository
- 🐛 **Reporting** bugs and issues
- 💡 **Suggesting** new features
- 🤝 **Contributing** code improvements
- 📢 **Sharing** with others

## 🗺️ Roadmap

- [ ] WebSocket support for real-time data
- [ ] Data export utilities (CSV, Excel, JSON)
- [ ] Advanced filtering and sorting
- [ ] Rate limiting with automatic backoff
- [ ] Caching layer for repeated requests
- [ ] CLI tool for quick queries
- [ ] Django/Flask integration examples
- [ ] Interactive Jupyter notebook examples

## ❓ FAQ

**Q: Is this library official?**  
A: No, this is an unofficial client library for the NEPSE API.

**Q: Do I need an API key?**  
A: No, the NEPSE API doesn't require authentication keys. The client handles token management automatically.

**Q: Can I use this in production?**  
A: Yes! The library is production-ready with comprehensive error handling, retries, and logging.

**Q: Which Python versions are supported?**  
A: Python 3.8 and above are supported.

**Q: How do I report a bug?**  
A: Please open an issue on [GitHub Issues](https://github.com/4mritgiri/NepseClient/issues) with details and a minimal reproduction example.

**Q: Can I contribute?**  
A: Absolutely! Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

---

> **Made with ❤️ for the Nepali Tech Community**
>
> If this project helps you, please consider giving it a ⭐!
