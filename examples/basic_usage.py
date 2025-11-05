"""
Basic usage examples for nepse-client library.

This script demonstrates common use cases and best practices.
"""

import asyncio
from datetime import date, timedelta

from nepse_client import AsyncNepse, Nepse
from nepse_client.errors import NepseError, NepseServerError, NepseTokenExpired


def example_sync_basic():
   """Basic synchronous usage example."""
   print("=" * 60)
   print("SYNCHRONOUS CLIENT - BASIC USAGE")
   print("=" * 60)

   # Initialize client
   client = Nepse()

   # Get market status
   print("\n1. Market Status:")
   try:
      status = client.getMarketStatus()
      print(f"   Market is: {status.get('isOpen', 'Unknown')}")
      print(f"   As of: {status.get('asOf', 'Unknown')}")
   except NepseError as e:
      print(f"   Error: {e}")

   # Get market summary
   print("\n2. Market Summary:")
   try:
      summary = client.getSummary()
      print(f"   Total Turnover: {summary.get('totalTurnover', 'N/A')}")
      print(f"   Total Traded Shares: {summary.get('totalTradedShares', 'N/A')}")
   except NepseError as e:
      print(f"   Error: {e}")

   # Get top gainers
   print("\n3. Top Gainers:")
   try:
      gainers = client.getTopGainers()
      for i, stock in enumerate(gainers[:5], 1):
         print(f"   {i}. {stock.get('symbol', 'N/A')}: {stock.get('percentageChange', 'N/A')}%")
   except NepseError as e:
      print(f"   Error: {e}")


def example_sync_company_data():
   """Example of fetching company-specific data."""
   print("\n" + "=" * 60)
   print("SYNCHRONOUS CLIENT - COMPANY DATA")
   print("=" * 60)

   client = Nepse()
   symbol = "NABIL"  # Example: NABIL Bank

   # Get company details
   print(f"\n1. Company Details for {symbol}:")
   try:
      details = client.getCompanyDetails(symbol)
      print(f"   Name: {details.get('companyName', 'N/A')}")
      print(f"   Sector: {details.get('sectorName', 'N/A')}")
      print(f"   LTP: {details.get('lastTradedPrice', 'N/A')}")
   except NepseError as e:
      print(f"   Error: {e}")

   # Get price history
   print(f"\n2. Price History for {symbol} (Last 30 days):")
   try:
      end_date = date.today()
      start_date = end_date - timedelta(days=30)
      history = client.getCompanyPriceVolumeHistory(
         symbol=symbol, start_date=start_date, end_date=end_date
      )
      
      if isinstance(history, dict) and 'content' in history:
         content = history['content'][:5]  # Show first 5 records
      else:
         content = history[:5] if isinstance(history, list) else []
         
      for record in content:
         print(
               f"   {record.get('businessDate', 'N/A')}: "
               f"Close: {record.get('closePrice', 'N/A')}, "
               f"Volume: {record.get('totalTradedQuantity', 'N/A')}"
         )
   except NepseError as e:
      print(f"   Error: {e}")

   # Get market depth
   print(f"\n3. Market Depth for {symbol}:")
   try:
      depth = client.getSymbolMarketDepth(symbol)
      print(f"   Buy Quantity: {depth.get('buyQuantity', 'N/A')}")
      print(f"   Sell Quantity: {depth.get('sellQuantity', 'N/A')}")
   except NepseError as e:
      print(f"   Error: {e}")


def example_sync_error_handling():
   """Example of proper error handling."""
   print("\n" + "=" * 60)
   print("SYNCHRONOUS CLIENT - ERROR HANDLING")
   print("=" * 60)

   client = Nepse()

   print("\n1. Handling different exception types:")
   try:
      # This might fail if symbol doesn't exist
      details = client.getCompanyDetails("INVALID_SYMBOL")
      print(f"   Details: {details}")
   except NepseTokenExpired:
      print("   Token expired - client will auto-refresh")
   except NepseServerError as e:
      print(f"   Server error occurred: {e}")
   except NepseError as e:
      print(f"   NEPSE error: {e}")
   except Exception as e:
      print(f"   Unexpected error: {e}")


async def example_async_basic():
   """Basic asynchronous usage example."""
   print("\n" + "=" * 60)
   print("ASYNCHRONOUS CLIENT - BASIC USAGE")
   print("=" * 60)

   # Initialize async client
   client = AsyncNepse()

   # Get market status
   print("\n1. Market Status:")
   try:
      status = await client.getMarketStatus()
      print(f"   Market is: {status.get('isOpen', 'Unknown')}")
   except NepseError as e:
      print(f"   Error: {e}")

   # Get multiple data concurrently
   print("\n2. Fetching Multiple Data Concurrently:")
   try:
      results = await asyncio.gather(
         client.getSummary(),
         client.getTopGainers(),
         client.getTopLosers(),
         return_exceptions=True,
      )

      summary, gainers, losers = results

      if isinstance(summary, dict):
         print(f"   Summary - Turnover: {summary.get('totalTurnover', 'N/A')}")

      if isinstance(gainers, list) and len(gainers) > 0:
         print(f"   Top Gainer: {gainers[0].get('symbol', 'N/A')}")

      if isinstance(losers, list) and len(losers) > 0:
         print(f"   Top Loser: {losers[0].get('symbol', 'N/A')}")

   except NepseError as e:
      print(f"   Error: {e}")


async def example_async_floor_sheet():
   """Example of fetching floor sheet data with progress."""
   print("\n" + "=" * 60)
   print("ASYNCHRONOUS CLIENT - FLOOR SHEET")
   print("=" * 60)

   client = AsyncNepse()

   print("\n1. Fetching Floor Sheet (with progress bar):")
   try:
      floor_sheet = await client.getFloorSheet(show_progress=True)
      print(f"   Total records: {len(floor_sheet)}")
      if floor_sheet:
         print(f"   Sample record: {floor_sheet[0]}")
   except NepseError as e:
      print(f"   Error: {e}")


async def example_async_company_batch():
   """Example of fetching data for multiple companies."""
   print("\n" + "=" * 60)
   print("ASYNCHRONOUS CLIENT - BATCH COMPANY DATA")
   print("=" * 60)

   client = AsyncNepse()
   symbols = ["NABIL", "NICA", "SCB", "EBL", "ADBL"]

   print(f"\n1. Fetching details for {len(symbols)} companies:")
   try:
      # Fetch all company details concurrently
      tasks = [client.getCompanyDetails(symbol) for symbol in symbols]
      results = await asyncio.gather(*tasks, return_exceptions=True)

      for symbol, result in zip(symbols, results):
         if isinstance(result, dict):
               print(f"   {symbol}: LTP = {result.get('lastTradedPrice', 'N/A')}")
         else:
               print(f"   {symbol}: Error - {result}")

   except NepseError as e:
      print(f"   Error: {e}")


def example_caching():
   """Example of using cached data."""
   print("\n" + "=" * 60)
   print("CACHING EXAMPLE")
   print("=" * 60)

   client = Nepse()

   print("\n1. Getting Company ID Mappings (cached):")
   try:
      # First call - fetches from API
      company_map = client.getCompanyIDKeyMap()
      print(f"   Total companies: {len(company_map)}")

      # Second call - uses cached data
      company_map_cached = client.getCompanyIDKeyMap()
      print(f"   Using cached data: {company_map is company_map_cached}")

      # Force refresh cache
      company_map_fresh = client.getCompanyIDKeyMap(force_update=True)
      print(f"   Force refreshed: {company_map is not company_map_fresh}")

   except NepseError as e:
      print(f"   Error: {e}")

   print("\n2. Getting Sector-wise Scrips:")
   try:
      sector_scrips = client.getSectorScrips()
      for sector, scrips in list(sector_scrips.items())[:3]:
         print(f"   {sector}: {len(scrips)} companies")
   except NepseError as e:
      print(f"   Error: {e}")


def main():
   """Run all examples."""
   print("\n" + "=" * 60)
   print("NEPSE CLIENT LIBRARY - EXAMPLES")
   print("=" * 60)

   # Synchronous examples
   example_sync_basic()
   example_sync_company_data()
   example_sync_error_handling()
   example_caching()

   # Asynchronous examples
   print("\n\nRunning Async Examples...\n")
   asyncio.run(example_async_basic())
   asyncio.run(example_async_floor_sheet())
   asyncio.run(example_async_company_batch())

   print("\n" + "=" * 60)
   print("ALL EXAMPLES COMPLETED")
   print("=" * 60)


if __name__ == "__main__":
   main()
