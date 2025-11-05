# nepse-client/nepse_client/async_client.py
# Asynchronous implementation of the NEPSE client

import asyncio
import json
from datetime import date, datetime, timedelta
from collections import defaultdict

import httpx
import tqdm.asyncio
from .client import _Nepse
from .token_manager import AsyncTokenManager
from .dummy_id_manager import AsyncDummyIDManager
from .exceptions import NepseAuthenticationError


class AsyncNepseClient(_Nepse):
   def __init__(self):
      super().__init__(AsyncTokenManager, AsyncDummyIDManager)
      # internal flag to set tls verification true or false during http request
      self.init_client(tls_verify=self._tls_verify)

   ############################################### PRIVATE METHODS###############################################
   async def getPOSTPayloadIDForScrips(self):
      dummy_id = await self.getDummyID()
      e = self.getDummyData()[dummy_id] + dummy_id + 2 * (date.today().day)
      return e

   async def getPOSTPayloadID(self):
      e = await self.getPOSTPayloadIDForScrips()
      # we need to await before update is completed
      await self.token_manager.update_completed.wait()
      post_payload_id = (
         e
         + self.token_manager.salts[3 if e % 10 < 5 else 1] * date.today().day
         - self.token_manager.salts[(3 if e % 10 < 5 else 1) - 1]
      )
      return post_payload_id

   async def getPOSTPayloadIDForFloorSheet(self):
      e = await self.getPOSTPayloadIDForScrips()

      # we need to await before update is completed
      await self.token_manager.update_completed.wait()

      post_payload_id = (
         e
         + self.token_manager.salts[1 if e % 10 < 4 else 3] * date.today().day
         - self.token_manager.salts[(1 if e % 10 < 4 else 3) - 1]
      )
      return post_payload_id

   async def getAuthorizationHeaders(self):
      headers = self.headers
      access_token = await self.token_manager.getAccessToken()

      headers = {
         "Authorization": f"Salter {access_token}",
         "Content-Type": "application/json",
         **self.headers,
      }

      return headers

   def init_client(self, tls_verify):
      self.client = httpx.AsyncClient(verify=tls_verify, http2=False, timeout=100)

   async def requestGETAPI(self, url, include_authorization_headers=True):
      try:
         response = await self.client.get(
               self.get_full_url(api_url=url),
               headers=(
                  await self.getAuthorizationHeaders()
                  if include_authorization_headers
                  else self.headers
               ),
         )
         return self.handle_response(response)
      except (httpx.RemoteProtocolError, httpx.ReadError, httpx.ConnectError):
         return await self.requestGETAPI(url, include_authorization_headers)
      except NepseAuthenticationError:
         await self.token_manager.update()
         return await self.requestGETAPI(url, include_authorization_headers)

   async def requestPOSTAPI(self, url, payload_generator):
      try:
         response = await self.client.post(
               self.get_full_url(api_url=url),
               headers=await self.getAuthorizationHeaders(),
               data=json.dumps({"id": await payload_generator()}),
         )
         return self.handle_response(response)
      except (httpx.RemoteProtocolError, httpx.ReadError, httpx.ConnectError):
         return await self.requestPOSTAPI(url, payload_generator)
      except NepseAuthenticationError:
         await self.token_manager.update()
         return await self.requestPOSTAPI(url, payload_generator)

   ############################################### PUBLIC METHODS###############################################
   # api requiring get method
   async def getCompanyList(self):
      self.company_list = await self.requestGETAPI(
         url=self.api_end_points["company_list_url"]
      )
      # return a copy of self.company_list so than changes after return are not perisistent
      return list(self.company_list)

   async def getSecurityList(self):
      self.security_list = await self.requestGETAPI(
         url=self.api_end_points["security_list_url"]
      )
      # return a copy of self.company_list so than changes after return are not perisistent
      return list(self.security_list)

   async def getSectorScrips(self):
      if self.sector_scrips is None:
         company_info_dict = {
               company_info["symbol"]: company_info
               for company_info in (await self.getCompanyList())
         }
         sector_scrips = defaultdict(list)

         for security_info in await self.getSecurityList():
               symbol = security_info["symbol"]
               if company_info_dict.get(symbol):
                  company_info = company_info_dict[symbol]
                  sector_name = company_info["sectorName"]
                  sector_scrips[sector_name].append(symbol)
               else:
                  sector_scrips["Promoter Share"].append(symbol)

         self.sector_scrips = dict(sector_scrips)
      # return a copy of self.sector_scrips so than changes after return are not perisistent
      return dict(self.sector_scrips)

   async def getCompanyIDKeyMap(self, force_update=False):
      if self.company_symbol_id_keymap is None or force_update:
         company_list = await self.getCompanyList()
         self.company_symbol_id_keymap = {
               company["symbol"]: company["id"] for company in company_list
         }
      return self.company_symbol_id_keymap

   async def getSecurityIDKeyMap(self, force_update=False):
      if self.security_symbol_id_keymap is None or force_update:
         security_list = await self.getSecurityList()
         self.security_symbol_id_keymap = {
               security["symbol"]: security["id"] for security in security_list
         }
      return self.security_symbol_id_keymap

   async def getCompanyPriceVolumeHistory(
      self, symbol, start_date=None, end_date=None
   ):
      end_date = end_date if end_date else date.today()
      start_date = start_date if start_date else (end_date - timedelta(days=365))
      symbol = symbol.upper()
      company_id = (await self.getSecurityIDKeyMap())[symbol]
      url = f"{self.api_end_points['company_price_volume_history']}{company_id}?&size=500&startDate={start_date}&endDate={end_date}"
      return (await self.requestGETAPI(url=url))["content"]

   # api requiring post method
   async def getDailyScripPriceGraph(self, symbol):
      symbol = symbol.upper()
      company_id = (await self.getSecurityIDKeyMap())[symbol]
      return await self.requestPOSTAPI(
         url=f"{self.api_end_points['company_daily_graph']}{company_id}",
         payload_generator=self.getPOSTPayloadIDForScrips,
      )

   async def getCompanyDetails(self, symbol):
      symbol = symbol.upper()
      company_id = (await self.getSecurityIDKeyMap())[symbol]
      return await self.requestPOSTAPI(
         url=f"{self.api_end_points['company_details']}{company_id}",
         payload_generator=self.getPOSTPayloadIDForScrips,
      )

   async def getFloorSheet(self, show_progress=False):
      size = f"&size={self.floor_sheet_size}"
      url = f"{self.api_end_points['floor_sheet']}?{size}&sort=contractId,desc"
      sheet = await self.requestPOSTAPI(
         url=url, payload_generator=self.getPOSTPayloadIDForFloorSheet
      )
      floor_sheets = sheet["floorsheets"]["content"]
      max_page = sheet["floorsheets"]["totalPages"]

      # page 0 is already downloaded so starting from 1
      page_range = range(1, max_page)
      awaitables = map(
         lambda page_number: self._getFloorSheetPageNumber(
               url,
               page_number,
         ),
         page_range,
      )
      if show_progress:
         remaining_floor_sheets = await tqdm.asyncio.tqdm.gather(*awaitables)
      else:
         remaining_floor_sheets = await asyncio.gather(*awaitables)

      floor_sheets = [floor_sheets] + remaining_floor_sheets
      return [row for array in floor_sheets for row in array]

   async def _getFloorSheetPageNumber(self, url, page_number):
      current_sheet = await self.requestPOSTAPI(
         url=f"{url}&page={page_number}",
         payload_generator=self.getPOSTPayloadIDForFloorSheet,
      )
      current_sheet_content = (
         current_sheet["floorsheets"]["content"] if current_sheet else []
      )
      return current_sheet_content

   async def getFloorSheetOf(self, symbol, business_date=None):
      # business date can be YYYY-mm-dd string or date object
      symbol = symbol.upper()
      company_id = (await self.getSecurityIDKeyMap())[symbol]
      business_date = (
         date.fromisoformat(f"{business_date}") if business_date else date.today()
      )
      url = f"{self.api_end_points['company_floorsheet']}{company_id}?&businessDate={business_date}&size={self.floor_sheet_size}&sort=contractid,desc"
      sheet = await self.requestPOSTAPI(
         url=url, payload_generator=self.getPOSTPayloadIDForFloorSheet
      )
      if sheet:  # sheet might be empty
         floor_sheets = sheet["floorsheets"]["content"]
         for page in range(1, sheet["floorsheets"]["totalPages"]):
               next_sheet = await self.requestPOSTAPI(
                  url=f"{url}&page={page}",
                  payload_generator=self.getPOSTPayloadIDForFloorSheet,
               )
               next_floor_sheet = next_sheet["floorsheets"]["content"]
               floor_sheets.extend(next_floor_sheet)
      else:
         floor_sheets = []
      return floor_sheets

   async def getSymbolMarketDepth(self, symbol):
      symbol = symbol.upper()
      company_id = await self.getSecurityIDKeyMap()
      url = f"{self.api_end_points['market-depth']}{company_id[symbol]}/"
      result = await self.requestGETAPI(url=url)
      return result
