# examples/advance_usage.py
"""
Advanced usage examples for nepse-client library.

This script demonstrates advanced patterns, best practices, and
real-world use cases for the NEPSE client library.
"""

import asyncio
import logging
from datetime import date, timedelta
from typing import Dict, List

from nepse_client import AsyncNepseClient, NepseClient
from nepse_client.exceptions import (
    NepseDataNotFoundError,
    NepseError,
    NepseRateLimitError,
    NepseServerError,
)


# ============== Setup Logging ==============


def setup_logging(level=logging.INFO):
    """Configure comprehensive logging."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("nepse_client.log"), logging.StreamHandler()],
    )
    return logging.getLogger(__name__)


logger = setup_logging()


# ============== Advanced Patterns ==============


class NepsePortfolioAnalyzer:
    """
    Advanced portfolio analysis using NEPSE client.

    Example usage:
       >>> analyzer = NepsePortfolioAnalyzer()
       >>> portfolio = {
       ...     'NABIL': 100,
       ...     'NICA': 50,
       ...     'SCB': 75
       ... }
       >>> value = analyzer.calculate_portfolio_value(portfolio)
    """

    def __init__(self, use_async: bool = False):
        """Initialize analyzer with sync or async client."""
        self.client = AsyncNepseClient() if use_async else NepseClient()
        self.use_async = use_async

    def calculate_portfolio_value(self, portfolio: Dict[str, int]) -> float:
        """
        Calculate total portfolio value.

        Args:
           portfolio: Dict of {symbol: quantity}

        Returns:
           Total portfolio value
        """
        if self.use_async:
            return asyncio.run(self._calculate_async(portfolio))
        return self._calculate_sync(portfolio)

    def _calculate_sync(self, portfolio: Dict[str, int]) -> float:
        """Configure comprehensive logging."""
        total_value = 0.0

        for symbol, quantity in portfolio.items():
            try:
                details = self.client.getCompanyDetails(symbol)
                ltp = float(details.get("lastTradedPrice", 0))
                total_value += ltp * quantity

                logger.info(f"{symbol}: {quantity} shares @ {ltp} = {ltp * quantity}")

            except NepseDataNotFoundError:
                logger.warning(f"Symbol {symbol} not found")
            except NepseError as e:
                logger.error(f"Error fetching {symbol}: {e}")

        return total_value

    async def _calculate_async(self, portfolio: Dict[str, int]) -> float:
        """Asynchronous calculation with concurrent requests.

        Args:
            portfolio (Dict[str, int]): _description_

        Returns:
            float: _description_
        """
        total_value = 0.0

        # Fetch all company details concurrently
        symbols = list(portfolio.keys())
        tasks = [self.client.getCompanyDetails(symbol) for symbol in symbols]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for symbol, result in zip(symbols, results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching {symbol}: {result}")
                continue

            quantity = portfolio[symbol]
            ltp = float(result.get("lastTradedPrice", 0))
            total_value += ltp * quantity

            logger.info(f"{symbol}: {quantity} shares @ {ltp} = {ltp * quantity}")

        return total_value


class NepsePriceAlertSystem:
    """
    Price monitoring and alert system.

    Example:
       >>> alerts = NepsePriceAlertSystem()
       >>> alerts.add_alert('NABIL', target_price=1300, above=True)
       >>> alerts.check_alerts()
    """

    def __init__(self):
        """Initialize alert system."""
        self.client = NepseClient()
        self.alerts: List[Dict] = []

    def add_alert(self, symbol: str, target_price: float, above: bool = True, callback=None):
        """
        Add price alert.

        Args:
           symbol: Stock symbol
           target_price: Target price to trigger alert
           above: If True, alert when price goes above target
           callback: Optional callback function
        """
        self.alerts.append(
            {
                "symbol": symbol,
                "target_price": target_price,
                "above": above,
                "callback": callback,
                "triggered": False,
            }
        )

        logger.info(f"Alert added: {symbol} " f"{'above' if above else 'below'} {target_price}")

    def check_alerts(self):
        """Check all alerts and trigger if conditions met."""
        for alert in self.alerts:
            if alert["triggered"]:
                continue

            try:
                details = self.client.getCompanyDetails(alert["symbol"])
                current_price = float(details.get("lastTradedPrice", 0))

                condition_met = (alert["above"] and current_price >= alert["target_price"]) or (
                    not alert["above"] and current_price <= alert["target_price"]
                )

                if condition_met:
                    alert["triggered"] = True
                    self._trigger_alert(alert, current_price)

            except NepseError as e:
                logger.error(f"Error checking alert for {alert['symbol']}: {e}")

    def _trigger_alert(self, alert: Dict, current_price: float):
        """Trigger an alert."""
        direction = "above" if alert["above"] else "below"
        message = (
            f"ALERT: {alert['symbol']} is {direction} "
            f"{alert['target_price']} (current: {current_price})"
        )

        logger.warning(message)
        print(f"🔔 {message}")

        if alert["callback"]:
            alert["callback"](alert, current_price)


class NepseHistoricalAnalyzer:
    """
    Analyze historical data and calculate metrics.

    Example:
       >>> analyzer = NepseHistoricalAnalyzer()
       >>> metrics = analyzer.calculate_returns('NABIL', days=30)
    """

    def __init__(self):
        """Initialize the historical analyzer."""
        self.client = NepseClient()

    def calculate_returns(self, symbol: str, days: int = 30) -> Dict[str, float]:
        """
        Calculate returns over specified period.

        Args:
           symbol: Stock symbol
           days: Number of days to analyze

        Returns:
           Dictionary with return metrics
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        try:
            history = self.client.getCompanyPriceVolumeHistory(
                symbol=symbol, start_date=start_date, end_date=end_date
            )

            if isinstance(history, dict) and "content" in history:
                data = history["content"]
            else:
                data = history

            if not data or len(data) < 2:
                logger.warning(f"Insufficient data for {symbol}")
                return {}

            # Calculate metrics
            prices = [float(d.get("closePrice", 0)) for d in data if d.get("closePrice")]

            if not prices:
                return {}

            start_price = prices[0]
            end_price = prices[-1]

            total_return = ((end_price - start_price) / start_price) * 100
            max_price = max(prices)
            min_price = min(prices)
            avg_price = sum(prices) / len(prices)
            volatility = self._calculate_volatility(prices)

            return {
                "symbol": symbol,
                "start_price": start_price,
                "end_price": end_price,
                "total_return_pct": round(total_return, 2),
                "max_price": max_price,
                "min_price": min_price,
                "avg_price": round(avg_price, 2),
                "volatility": round(volatility, 2),
                "days_analyzed": len(prices),
            }

        except NepseError as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {}

    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calculate price volatility (standard deviation)."""
        if len(prices) < 2:
            return 0.0

        avg = sum(prices) / len(prices)
        variance = sum((p - avg) ** 2 for p in prices) / (len(prices) - 1)
        return variance**0.5


# ============== Retry and Error Handling Patterns ==============


class RobustNepseClient:
    """
    Wrapper with advanced retry and error handling.

    Example:
       >>> client = RobustNepseClient(max_retries=5, retry_delay=2)
       >>> data = client.safe_get_market_status()
    """

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """Initialize robust client."""
        self.client = NepseClient()
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def safe_request(self, func, *args, **kwargs):
        """
        Execute request with retry logic.

        Args:
           func: Function to call
           *args, **kwargs: Arguments for the function

        Returns:
           Result or None if all retries fail
        """
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)

            except NepseRateLimitError as e:
                if e.retry_after:
                    wait_time = e.retry_after
                else:
                    wait_time = self.retry_delay * (2**attempt)

                logger.warning(f"Rate limited, waiting {wait_time}s...")
                asyncio.sleep(wait_time)

            except NepseServerError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2**attempt)
                    logger.warning(
                        f"Server error, retrying in {wait_time}s... "
                        f"(attempt {attempt + 1}/{self.max_retries})"
                    )
                    asyncio.sleep(wait_time)
                else:
                    logger.error(f"Max retries exceeded: {e}")
                    return None

            except NepseError as e:
                logger.error(f"NEPSE error: {e}")
                return None

        return None

    def safe_get_market_status(self):
        """Get market status with retry logic."""
        return self.safe_request(self.client.getMarketStatus)

    def safe_get_company_details(self, symbol: str):
        """Get company details with retry logic."""
        return self.safe_request(self.client.getCompanyDetails, symbol)


# ============== Async Batch Operations ==============


async def fetch_multiple_companies(symbols: List[str]) -> Dict[str, Dict]:
    """
    Fetch details for multiple companies concurrently.

    Args:
       symbols: List of stock symbols

    Returns:
       Dictionary of {symbol: details}
    """
    client = AsyncNepseClient()
    results = {}

    tasks = [client.getCompanyDetails(symbol) for symbol in symbols]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    for symbol, response in zip(symbols, responses):
        if isinstance(response, Exception):
            logger.error(f"Error fetching {symbol}: {response}")
            results[symbol] = None
        else:
            results[symbol] = response

    return results


async def monitor_market_continuously(interval_seconds: int = 60):
    """
    Continuously monitor market status.

    Args:
       interval_seconds: Monitoring interval
    """
    client = AsyncNepseClient()

    while True:
        try:
            status = await client.getMarketStatus()
            summary = await client.getSummary()

            logger.info(
                f"Market: {status.get('isOpen')} | " f"Turnover: {summary.get('totalTurnover')}"
            )

            await asyncio.sleep(interval_seconds)

        except KeyboardInterrupt:
            logger.info("Monitoring stopped")
            break
        except NepseError as e:
            logger.error(f"Monitoring error: {e}")
            await asyncio.sleep(interval_seconds)


# ============== Example Usage ==============
def example_portfolio_analysis():
    """Demonstrate the Portfolio analysis system example."""
    print("\n" + "=" * 60)
    print("PORTFOLIO ANALYSIS EXAMPLE")
    print("=" * 60)

    analyzer = NepsePortfolioAnalyzer(use_async=False)

    portfolio = {
        "NABIL": 100,
        "NICA": 50,
        "SCB": 75,
    }

    print(f"\nPortfolio: {portfolio}")
    total_value = analyzer.calculate_portfolio_value(portfolio)
    print(f"\nTotal Portfolio Value: NPR {total_value:,.2f}")


def example_price_alerts():
    """Demonstrate the price alert system example."""
    print("\n" + "=" * 60)
    print("PRICE ALERT SYSTEM EXAMPLE")
    print("=" * 60)

    alerts = NepsePriceAlertSystem()

    # Add alerts
    alerts.add_alert("NABIL", target_price=1300, above=True)
    alerts.add_alert("NICA", target_price=800, above=False)

    # Check alerts
    print("\nChecking alerts...")
    alerts.check_alerts()


def example_historical_analysis():
    """Demonstrate the Historical analysis system example."""
    print("\n" + "=" * 60)
    print("HISTORICAL ANALYSIS EXAMPLE")
    print("=" * 60)

    analyzer = NepseHistoricalAnalyzer()

    symbols = ["NABIL", "NICA", "SCB"]

    for symbol in symbols:
        print(f"\n{symbol}:")
        metrics = analyzer.calculate_returns(symbol, days=30)

        if metrics:
            print(f"  Return: {metrics['total_return_pct']}%")
            print(f"  Range: {metrics['min_price']} - {metrics['max_price']}")
            print(f"  Volatility: {metrics['volatility']}")


async def example_async_batch():
    """Demonstrate the Async batch operations system example."""
    print("\n" + "=" * 60)
    print("ASYNC BATCH OPERATIONS EXAMPLE")
    print("=" * 60)

    symbols = ["NABIL", "NICA", "SCB", "EBL", "ADBL"]

    print(f"\nFetching {len(symbols)} companies concurrently...")
    results = await fetch_multiple_companies(symbols)

    print("\nResults:")
    for symbol, details in results.items():
        if details:
            ltp = details.get("lastTradedPrice", "N/A")
            print(f"  {symbol}: NPR {ltp}")
        else:
            print(f"  {symbol}: Error")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("NEPSE CLIENT - ADVANCED USAGE EXAMPLES")
    print("=" * 60)

    # Synchronous examples
    try:
        example_portfolio_analysis()
    except Exception as e:
        logger.error(f"Portfolio analysis error: {e}")

    try:
        example_historical_analysis()
    except Exception as e:
        logger.error(f"Historical analysis error: {e}")

    try:
        example_price_alerts()
    except Exception as e:
        logger.error(f"Price alerts error: {e}")

    # Asynchronous examples
    try:
        asyncio.run(example_async_batch())
    except Exception as e:
        logger.error(f"Async batch error: {e}")

    print("\n" + "=" * 60)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
