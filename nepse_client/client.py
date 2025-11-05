# client.py
# Defines the base class _Nepse common to both sync and async clients

import json
import pathlib
from datetime import datetime
from .exceptions import (
   NepseClientError,
   NepseBadGatewayError,
   NepseNetworkError,
   NepseServerError,
   NepseAuthenticationError,
)
from functools import singledispatch
import logging

# Optional: Mask sensitive fields like auth tokens
def mask_sensitive_data(data: dict, keys=("token", "password")) -> dict:
   masked = data.copy()
   for key in keys:
      if key in masked:
         masked[key] = "***MASKED***"
   return masked

# Convert object to JSON-safe string
@singledispatch
def safe_serialize(o):
   try:
      return str(o)
   except Exception:
      return "<unserializable>"

@safe_serialize.register(dict)
def _(o):
   return json.dumps(o, default=safe_serialize)

@safe_serialize.register(list)
def _(o):
   return [safe_serialize(i) for i in o]

class _Nepse:
   def __init__(self, token_manager, dummy_id_manager, logger=None, mask_request_data=True):
      self.logger = logger or logging.getLogger(__name__)
      self.token_manager = token_manager(self)
      self.mask_request_data = mask_request_data


      self.dummy_id_manager = dummy_id_manager(
         market_status_function=self.getMarketStatus,
         date_function=datetime.now,
      )
      # explicitly set value to True, can be disabled by user using setTLSVerification method
      self._tls_verify = True
      # list of all company that were listed in nepse (including delisted but doesn't include promoter shares)
      self.company_symbol_id_keymap = None
      # list of all valid company that are not delisted (includes promoter share)
      self.security_symbol_id_keymap = None

      self.company_list = None
      self.holiday_list = None
      self.security_list = None

      self.sector_scrips = None

      self.floor_sheet_size = 500

      self.base_url = "https://nepalstock.com.np"
      
      self.load_json_api_end_points()
      self.load_json_dummy_data()
      self.load_json_header()

   ############################################### PRIVATE METHODS###############################################
   def getDummyID(self):
      return self.dummy_id_manager.getDummyID()

   def load_json_header(self):
      json_file_path = f"{pathlib.Path(__file__).parent}/data/HEADERS.json"
      with open(json_file_path, "r") as json_file:
         self.headers = json.load(json_file)
         self.headers["Host"] = self.base_url.replace("https://", "")
         self.headers["Referer"] = self.base_url.replace("https://", "")

   def load_json_api_end_points(self):
      json_file_path = f"{pathlib.Path(__file__).parent}/data/API_ENDPOINTS.json"
      with open(json_file_path, "r") as json_file:
         self.api_end_points = json.load(json_file)

   def get_full_url(self, api_url):
      return f"{self.base_url}{api_url}"

   def load_json_dummy_data(self):
      json_file_path = f"{pathlib.Path(__file__).parent}/data/DUMMY_DATA.json"
      with open(json_file_path, "r") as json_file:
         self.dummy_data = json.load(json_file)

   def getDummyData(self):
      return self.dummy_data

   def init_client(self, tls_verify):
      pass

   def requestGETAPI(self, url):
      pass

   def requestPOSTAPI(self, url, payload_generator):
      pass

   # These 3 functions maybe both sync/async which needs to be implemented by the the child class
   def getPOSTPayloadIDForScrips(self):
      pass

   def getPOSTPayloadID(self):
      pass

   def getPOSTPayloadIDForFloorSheet(self):
      pass


   def handle_response(self, response, request_data=None):
      self.logger.debug(f"HTTP {response.request.method} {response.url}")
      self.logger.debug(f"STATUS CODE: {response.status_code}")

      # Try to parse response data
      try:
         data = response.json()
      except ValueError:
         data = response.text.strip()

      # Log request/response details
      log_context = {
         "url": response.url,
         "method": response.request.method,
         "status_code": response.status_code,
         "request_headers": dict(response.request.headers),
         "request_body": request_data or getattr(response.request, "body", None),
         "response_body": data,
      }

      if self.mask_request_data and isinstance(log_context["request_body"], dict):
         log_context["request_body"] = mask_sensitive_data(log_context["request_body"])

      self.logger.debug("Response received", extra=log_context)

      match response.status_code:
         case status if 200 <= status < 300:
               return data

         case 400:
               msg = f"Client Error 400: {safe_serialize(data)}"
               self.logger.warning(msg, extra=log_context)
               raise NepseClientError(msg) from None

         case 401:
               msg = f"Unauthorized (401): {safe_serialize(data)}"
               self.logger.warning(msg, extra=log_context)
               raise NepseAuthenticationError(msg) from None

         case 502:
               msg = f"Bad Gateway (502): {safe_serialize(data)}"
               self.logger.error(msg, exc_info=True, extra=log_context)
               raise NepseBadGatewayError(msg) from None

         case status if 500 <= status < 600:
               msg = f"Server Error {status}: {safe_serialize(data)}"
               self.logger.error(msg, exc_info=True, extra=log_context)
               raise NepseServerError(msg) from None

         case _:
               msg = f"Unexpected HTTP status code {response.status_code}: {safe_serialize(data)}"
               self.logger.critical(msg, exc_info=True, extra=log_context)
               raise NepseNetworkError(msg) from None


   ############################################### PUBLIC METHODS###############################################
   def setTLSVerification(self, flag):
      self._tls_verify = flag
      self.init_client(tls_verify=flag)

   # api requiring get method
   def getMarketStatus(self):
      return self.requestGETAPI(url=self.api_end_points["nepse_open_url"])

   def getPriceVolume(self):
      return self.requestGETAPI(url=self.api_end_points["price_volume_url"])

   def getSummary(self):
      return self.requestGETAPI(url=self.api_end_points["summary_url"])

   def getTopTenTradeScrips(self):
      return self.requestGETAPI(url=self.api_end_points["top_ten_trade_url"])

   def getTopTenTransactionScrips(self):
      return self.requestGETAPI(url=self.api_end_points["top_ten_transaction_url"])

   def getTopTenTurnoverScrips(self):
      return self.requestGETAPI(url=self.api_end_points["top_ten_turnover_url"])

   def getSupplyDemand(self):
      return self.requestGETAPI(url=self.api_end_points["supply_demand_url"])

   def getTopGainers(self):
      return self.requestGETAPI(url=self.api_end_points["top_gainers_url"])

   def getTopLosers(self):
      return self.requestGETAPI(url=self.api_end_points["top_losers_url"])

   def isNepseOpen(self):
      return self.requestGETAPI(url=self.api_end_points["nepse_open_url"])

   def getNepseIndex(self):
      return self.requestGETAPI(url=self.api_end_points["nepse_index_url"])

   def getNepseSubIndices(self):
      return self.requestGETAPI(url=self.api_end_points["nepse_subindices_url"])

   def getLiveMarket(self):
      return self.requestGETAPI(url=self.api_end_points["live-market"])

   def getTradingAverage(self, business_date=None, nDays=180):
      business_date = f"&businessDate={business_date}" if business_date else None
      nDays = f"&nDays={nDays}" if nDays else None
      # url=f"{self.api_end_points['trading-average']}?{business_date}{nDays}"
      return self.requestGETAPI(url=f"{self.api_end_points['trading-average']}?{business_date}{nDays}")

   # ================= api requiring POST method =================
   def getPriceVolumeHistory(self, business_date=None):
      business_date = f"&businessDate={business_date}" if business_date else ''
      url = f"{self.api_end_points['todays_price']}?&size=500{business_date}"
      return self.requestPOSTAPI(
         url=url, payload_generator=self.getPOSTPayloadIDForFloorSheet
      )

   def getDailyNepseIndexGraph(self):
      return self.requestPOSTAPI(
         url=self.api_end_points["nepse_index_daily_graph"],
         payload_generator=self.getPOSTPayloadID,
      )

   def getDailySensitiveIndexGraph(self):
      return self.requestPOSTAPI(
         url=self.api_end_points["sensitive_index_daily_graph"],
         payload_generator=self.getPOSTPayloadID,
      )

   def getDailyFloatIndexGraph(self):
      return self.requestPOSTAPI(
         url=self.api_end_points["float_index_daily_graph"],
         payload_generator=self.getPOSTPayloadID,
      )

   def getDailySensitiveFloatIndexGraph(self):
      return self.requestPOSTAPI(
         url=self.api_end_points["sensitive_float_index_daily_graph"],
         payload_generator=self.getPOSTPayloadID,
      )

   def getDailyBankSubindexGraph(self):
      return self.requestPOSTAPI(
         url=self.api_end_points["banking_sub_index_graph"],
         payload_generator=self.getPOSTPayloadID,
      )

   def getDailyDevelopmentBankSubindexGraph(self):
      return self.requestPOSTAPI(
         url=self.api_end_points["development_bank_sub_index_graph"],
         payload_generator=self.getPOSTPayloadID,
      )

   def getDailyFinanceSubindexGraph(self):
      return self.requestPOSTAPI(
         url=self.api_end_points["finance_sub_index_graph"],
         payload_generator=self.getPOSTPayloadID,
      )

   def getDailyHotelTourismSubindexGraph(self):
      return self.requestPOSTAPI(
         url=self.api_end_points["hotel_tourism_sub_index_graph"],
         payload_generator=self.getPOSTPayloadID,
      )

   def getDailyHydroSubindexGraph(self):
      return self.requestPOSTAPI(
         url=self.api_end_points["hydro_sub_index_graph"],
         payload_generator=self.getPOSTPayloadID,
      )

   def getDailyInvestmentSubindexGraph(self):
      return self.requestPOSTAPI(
         url=self.api_end_points["investment_sub_index_graph"],
         payload_generator=self.getPOSTPayloadID,
      )

   def getDailyLifeInsuranceSubindexGraph(self):
      return self.requestPOSTAPI(
         url=self.api_end_points["life_insurance_sub_index_graph"],
         payload_generator=self.getPOSTPayloadID,
      )

   def getDailyManufacturingSubindexGraph(self):
      return self.requestPOSTAPI(
         url=self.api_end_points["manufacturing_sub_index_graph"],
         payload_generator=self.getPOSTPayloadID,
      )

   def getDailyMicrofinanceSubindexGraph(self):
      return self.requestPOSTAPI(
         url=self.api_end_points["microfinance_sub_index_graph"],
         payload_generator=self.getPOSTPayloadID,
      )

   def getDailyMutualfundSubindexGraph(self):
      return self.requestPOSTAPI(
         url=self.api_end_points["mutual_fund_sub_index_graph"],
         payload_generator=self.getPOSTPayloadID,
      )

   def getDailyNonLifeInsuranceSubindexGraph(self):
      return self.requestPOSTAPI(
         url=self.api_end_points["non_life_insurance_sub_index_graph"],
         payload_generator=self.getPOSTPayloadID,
      )

   def getDailyOthersSubindexGraph(self):
      return self.requestPOSTAPI(
         url=self.api_end_points["others_sub_index_graph"],
         payload_generator=self.getPOSTPayloadID,
      )

   def getDailyTradingSubindexGraph(self):
      return self.requestPOSTAPI(
         url=self.api_end_points["trading_sub_index_graph"],
         payload_generator=self.getPOSTPayloadID,
      )

__all__ = [
   "_Nepse"
]
