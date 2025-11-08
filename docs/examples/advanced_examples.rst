Advanced Examples
=================

Real-world scenarios and advanced patterns.

Portfolio Calculator
--------------------

.. code-block:: python

   from nepse_client import NepseClient

   def calculate_portfolio_value(portfolio):
      client = NepseClient()
      total = 0

      for symbol, quantity in portfolio.items():
         details = client.getCompanyDetails(symbol)
         price = float(details['lastTradedPrice'])
         total += price * quantity

      return total

See :download:`advanced_usage.py <../../examples/advance_usage.py>`.
