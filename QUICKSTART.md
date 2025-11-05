# NEPSE Client - Quick Start Guide

Get up and running with nepse-client in 5 minutes!

## 📦 Installation

```bash
# Install from PyPI (when published)
pip install nepse-client

# Or install from source
git clone https://github.com/yourusername/nepse-client.git
cd nepse-client
pip install -e .
```

## 🚀 Basic Usage

### Synchronous (Blocking)

```python
from nepse_client import Nepse

# Create client
client = Nepse()

# Get market status
status = client.getMarketStatus()
print(f"Market: {status['isOpen']}")

# Get today's top gainers
gainers = client.getTopGainers()
for stock in gainers[:5]:
    print(f"{stock['symbol']}: +{stock['percentageChange']}%")

# Get company details
details = client.getCompanyDetails("NABIL")
print(f"LTP: {details['lastTradedPrice']}")
```

### Asynchronous (Non-blocking)

```python
import asyncio
from nepse_client import AsyncNepse

async def main():
    # Create async client
    client = AsyncNepse()
    
    # Get multiple data concurrently
    status, gainers, summary = await asyncio.gather(
        client.getMarketStatus(),
        client.getTopGainers(),
        client.getSummary()
    )
    
    print(f"Market: {status['isOpen']}")
    print(f"Top Gainer: {gainers[0]['symbol']}")
    print(f"Turnover: {summary['totalTurnover']}")

# Run async function
asyncio.run(main())
```

## 📊 Common Operations

### Market Information

```python
client = Nepse()

# Market status
status = client.getMarketStatus()
is_open = status['isOpen']

# Market summary
summary = client.getSummary()
turnover = summary['totalTurnover']

# NEPSE index
index = client.getNepseIndex()
current_index = index['index']

# Live market data
live_data = client.getLiveMarket()
```

### Company Data

```python
# List all companies
companies = client.getCompanyList()

# Get specific company
details = client.getCompanyDetails("NABIL")

# Price history
from datetime import date, timedelta
end_date = date.today()
start_date = end_date - timedelta(days=30)

history = client.getCompanyPriceVolumeHistory(
    symbol="NABIL",
    start_date=start_date,
    end_date=end_date
)
```

### Trading Data

```python
# Floor sheet (all trades)
floor_sheet = client.getFloorSheet()

# Floor sheet for specific company
nabil_trades = client.getFloorSheetOf("NABIL", business_date="2024-01-15")

# Market depth
depth = client.getSymbolMarketDepth("NABIL")
```

### Top Performers

```python
# Top gainers
gainers = client.getTopGainers()

# Top losers
losers = client.getTopLosers()

# Top by turnover
top_turnover = client.getTopTenTurnoverScrips()
```

## 🛡️ Error Handling

```python
from nepse_client import Nepse, NepseError, NepseTokenExpired

client = Nepse()

try:
    details = client.getCompanyDetails("NABIL")
    print(details)
    
except NepseTokenExpired:
    # Token expired - client will auto-refresh
    print("Token expired, retrying...")
    
except NepseError as e:
    # Handle any NEPSE error
    print(f"Error: {e}")
```

## 🔧 Configuration

### Custom Timeout

```python
client = Nepse(timeout=60.0)  # 60 seconds timeout
```

### Disable TLS Verification (Not Recommended)

```python
client = Nepse()
client.setTLSVerification(False)
```

### Custom Logging

```python
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Client will use the configured logger
client = Nepse()
```

## 📈 Advanced Examples

### Portfolio Value Calculator

```python
def calculate_portfolio(portfolio):
    """
    Calculate portfolio value.
    
    Args:
        portfolio: Dict of {symbol: quantity}
    
    Returns:
        Total value in NPR
    """
    client = Nepse()
    total = 0
    
    for symbol, quantity in portfolio.items():
        details = client.getCompanyDetails(symbol)
        price = float(details['lastTradedPrice'])
        total += price * quantity
        print(f"{symbol}: {quantity} @ {price} = {price * quantity}")
    
    return total

# Example usage
my_portfolio = {
    'NABIL': 100,
    'NICA': 50,
    'SCB': 75
}

total_value = calculate_portfolio(my_portfolio)
print(f"\nTotal Portfolio Value: NPR {total_value:,.2f}")
```

### Async Batch Processing

```python
import asyncio
from nepse_client import AsyncNepse

async def fetch_multiple_symbols(symbols):
    """Fetch details for multiple symbols concurrently."""
    client = AsyncNepse()
    
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
asyncio.run(fetch_multiple_symbols(symbols))
```

### Context Manager Usage

```python
# Automatic cleanup
with Nepse() as client:
    status = client.getMarketStatus()
    print(status)
# Client automatically closed
```

## 🧪 Testing Your Code

```python
# Create a simple test
def test_market_status():
    client = Nepse()
    status = client.getMarketStatus()
    
    assert 'isOpen' in status
    assert 'asOf' in status
    print("✓ Test passed!")

test_market_status()
```

## 📚 Next Steps

1. **Read the full documentation**: [README.md](README.md)
2. **Explore examples**: Check the `examples/` directory
3. **Run tests**: `pytest tests/`
4. **Check API reference**: See docstrings in the code

## 🐛 Troubleshooting

### Import Error

```bash
# Make sure package is installed
pip install -e .

# Or check your Python path
python -c "import nepse_client; print(nepse_client.__file__)"
```

### Connection Errors

```python
# Increase timeout
client = Nepse(timeout=120.0)

# Or increase retries
client = Nepse(max_retries=5)
```

### Rate Limiting

```python
from nepse_client import NepseRateLimitError
import time

try:
    data = client.getMarketStatus()
except NepseRateLimitError as e:
    if e.retry_after:
        print(f"Rate limited, waiting {e.retry_after}s...")
        time.sleep(e.retry_after)
```

## 💡 Tips

1. **Use async for multiple requests** - Much faster than sequential
2. **Cache company lists** - They don't change often
3. **Handle errors gracefully** - Network issues happen
4. **Use context managers** - Ensures proper cleanup
5. **Enable logging** - Helps debug issues

## 📞 Getting Help

- **Issues**: https://github.com/yourusername/nepse-client/issues
- **Discussions**: https://github.com/yourusername/nepse-client/discussions
- **Email**: your.email@example.com

## ⭐ Show Your Support

If you find this library helpful, please give it a star on GitHub!

---

**Ready to build something awesome? Start coding! 🚀**