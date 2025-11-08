Basic Usage Examples
====================

This page provides basic examples for common use cases.

Getting Started
---------------

Simple Market Data
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from nepse_client import NepseClient

   # Initialize client
   client = NepseClient()

   # Get market status
   status = client.getMarketStatus()
   print(f"Market: {status['isOpen']}")

   # Get market summary
   summary = client.getSummary()
   print(f"Turnover: NPR {summary['totalTurnover']:,.2f}")

For complete examples, see the :download:`basic_usage.py <../../examples/basic_usage.py>` file.
