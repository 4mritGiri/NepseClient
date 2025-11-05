# nepse-client/nepse_client/sync_client.py
# Synchronous implementation of the NEPSE client

import json
from datetime import date, datetime
import httpx
import tqdm
from .client import _Nepse
from .token_manager import TokenManager
from .dummy_id_manager import DummyIDManager


class NepseClient(_Nepse):
   def __init__(self, logger=None, mask_request_data=True):
      super().__init__(TokenManager, DummyIDManager, logger, mask_request_data)
      # internal flag to set tls verification true or false during http request
      self.init_client(tls_verify=self._tls_verify)

   ############################################### PRIVATE METHODS###############################################
   def getPOSTPayloadIDForScrips(self):
      dummy_id = self.getDummyID()
      e = self.getDummyData()[dummy_id] + dummy_id + 2 * (date.today().day)
      return e

   def getPOSTPayloadID(self):
      e = self.getPOSTPayloadIDForScrips()
      post_payload_id = (
         e
         + self.token_manager.salts[3 if e % 10 < 5 else 1] * date.today().day
         - self.token_manager.salts[(3 if e % 10 < 5 else 1) - 1]
      )
      return post_payload_id

   def getPOSTPayloadIDForFloorSheet(self, business_date=None):
      e = self.getPOSTPayloadIDForScrips()
      # Parse business_date properly
      if business_date is None:
         day = date.today().day
      else:
         if isinstance(business_date, (date, datetime)):
               day = business_date.day
         else:
               try:
                  parsed_date = datetime.strptime(business_date, "%Y-%m-%d")
                  day = parsed_date.day
               except ValueError as ex:
                  raise ValueError(f"Invalid date format: {business_date}. Expected YYYY-MM-DD.") from ex
      salt_index = 1 if e % 10 < 4 else 3
      post_payload_id = (
         e
         + self.token_manager.salts[salt_index] * day
         - self.token_manager.salts[salt_index - 1]
      )
      return post_payload_id

   def getAuthorizationHeaders(self):
      headers = self.headers
      access_token = self.token_manager.getAccessToken()
      headers = {
         "Authorization": f"Salter {access_token}",
         "Content-Type": "application/json",
         **self.headers,
      }
      return headers

   def init_client(self, tls_verify):
      self.client = httpx.Client(verify=tls_verify, http2=True, timeout=100)

   def requestGETAPI(self, url, include_authorization_headers=True):
      try:
         response = self.client.get(
               self.get_full_url(api_url=url),
               headers=(
                  self.getAuthorizationHeaders()
                  if include_authorization_headers
                  else self.headers
               ),
         )
         return self.handle_response(response)
      except (httpx.RemoteProtocolError, httpx.ReadError, httpx.ConnectError):
         return self.requestGETAPI(url, include_authorization_headers)
      except Exception as e:
         if "NepseTokenExpired" in str(type(e)): # Handle specific exception if needed
               self.token_manager.update()
               return self.requestGETAPI(url, include_authorization_headers)
         raise e # Re-raise if not a token expired error

   def requestPOSTAPI(self, url, payload_generator):
      try:
         response = self.client.post(
               self.get_full_url(api_url=url),
               headers=self.getAuthorizationHeaders(),
               data=json.dumps({"id": payload_generator()}),
         )
         return self.handle_response(response)
      except (httpx.RemoteProtocolError, httpx.ReadError, httpx.ConnectError):
         return self.requestPOSTAPI(url, payload_generator)
      except Exception as e:
         if "NepseTokenExpired" in str(type(e)): # Handle specific exception if needed
               self.token_manager.update()
               return self.requestPOSTAPI(url, payload_generator)
         raise e # Re-raise if not a token expired error

   ############################################### PUBLIC METHODS###############################################
   # api requiring get method
   def getCompanyList(self):
      self.company_list = self.requestGETAPI(
         url=self.api_end_points["company_list_url"]
      )
      # return a copy of self.company_list so than changes after return are not perisistent
      return list(self.company_list)

   def getHolidayList(self, year=2025):
      url=f"{self.api_end_points['holiday-list']}?year={year}"
      print(url)
      self.holiday_list = self.requestGETAPI(
         url=url
      )
      # return a copy of self.holiday_list so than changes after return are not perisistent
      return list(self.holiday_list)

   def getDebentureAndBondList(self, type='debenture'):
      url=f"{self.api_end_points['debenture-and-bond']}?type={type}"
      # print(url)
      return list(self.requestGETAPI(url=url))

   def getCompanyNewsList(self, page: int = 1, page_size: int = 100, is_strip_tags: bool = True):
      from django.utils.html import strip_tags
      url = self.api_end_points['company-news']
      raw_data = self.requestGETAPI(url=url) or []
      if not isinstance(raw_data, list):
         print(f"Warning: API response is not a list. Type: {type(raw_data)}. Attempting to convert.")
         try:
               raw_data = list(raw_data)
         except (TypeError, ValueError):
               print("Error: Could not convert API response to list. Returning empty results.")
               raw_data = []
      base_file_url = self.get_full_url(self.api_end_points['fetch-security-files'])
      processed_data = []
      for item in raw_data:
         if isinstance(item, dict):
               processed_item = item.copy()
               file_path = processed_item.get('filePath')
               if is_strip_tags in [1, True, 'true', '1', 'True']:
                  news_body = processed_item.get('newsBody', None)
                  if news_body:
                     processed_item['newsBody'] = strip_tags(news_body)
               if file_path:
                  processed_item['fullFilePath'] = f"{base_file_url}{file_path}"
               processed_data.append(processed_item)
         else:
               print(f"Warning: Skipping non-dictionary item in raw  {item}")
      total_count = len(processed_data)
      if total_count == 0:
         return {
               'results': [],
               'count': 0,
               'page': page,
               'page_size': page_size,
               'total_pages': 0,
               'next_page': None,
               'previous_page': None
         }
      try:
         page = int(page)
         page_size = int(page_size)
      except (ValueError, TypeError):
         print("Invalid page or page_size provided, defaulting to page 1, size 100.")
         page = 1
         page_size = 100
      if page < 1:
         page = 1
      if page_size < 1:
         page_size = 100 # Or raise an error
      total_pages = (total_count + page_size - 1) // page_size # Ceiling division
      if page > total_pages:
         page = total_pages if total_pages > 0 else 1
      start_index = (page - 1) * page_size
      end_index = start_index + page_size
      if start_index >= total_count:
         paginated_results = []
      else:
         paginated_results = processed_data[start_index:end_index]
      next_page = page + 1 if page < total_pages else None
      previous_page = page - 1 if page > 1 else None
      return {
         'results': paginated_results,
         'count': total_count, # Total items available
         'page': page,
         'page_size': page_size,
         'total_pages': total_pages,
         'next_page': next_page,
         'previous_page': previous_page,
         'params': [
               'page: number',
               'pageSize: number',
               'isStripTags: bool'
         ]
      }

   def getNewsAndAlertList(self, page: int = 1, page_size: int = 100, is_strip_tags: bool = True):
      from django.utils.html import strip_tags
      url = self.api_end_points['news-alerts']
      raw_data = self.requestGETAPI(url=url) or []
      if not isinstance(raw_data, list):
         print(f"Warning: API response is not a list. Type: {type(raw_data)}. Attempting to convert.")
         try:
               raw_data = list(raw_data)
         except (TypeError, ValueError):
               print("Error: Could not convert API response to list. Returning empty results.")
               raw_data = []
      base_file_url = self.get_full_url(self.api_end_points['fetch-security-files'])
      processed_data = []
      for item in raw_data:
         if isinstance(item, dict):
               processed_item = item.copy()
               file_path = processed_item.get('filePath')
               if is_strip_tags in [1, True, 'true', '1', 'True']:
                  news_body = processed_item.get('messageBody', None)
                  if news_body:
                     processed_item['messageBody'] = strip_tags(news_body)
               if file_path:
                  processed_item['fullFilePath'] = f"{base_file_url}{file_path}"
               processed_data.append(processed_item)
         else:
               print(f"Warning: Skipping non-dictionary item in raw  {item}")
      total_count = len(processed_data)
      if total_count == 0:
         return {
               'results': [],
               'count': 0,
               'page': page,
               'page_size': page_size,
               'total_pages': 0,
               'next': None,
               'previous': None
         }
      try:
         page = int(page)
         page_size = int(page_size)
      except (ValueError, TypeError):
         print("Invalid page or page_size provided, defaulting to page 1, size 100.")
         page = 1
         page_size = 100
      if page < 1:
         page = 1
      if page_size < 1:
         page_size = 100 # Or raise an error
      total_pages = (total_count + page_size - 1) // page_size # Ceiling division
      if page > total_pages:
         page = total_pages if total_pages > 0 else 1
      start_index = (page - 1) * page_size
      end_index = start_index + page_size
      if start_index >= total_count:
         paginated_results = []
      else:
         paginated_results = processed_data[start_index:end_index]
      next_page = page + 1 if page < total_pages else None
      previous_page = page - 1 if page > 1 else None
      return {
         'results': paginated_results,
         'count': total_count,
         'page': page,
         'page_size': page_size,
         'total_pages': total_pages,
         'next': next_page,
         'previous': previous_page,
         'params': [
               'page: number',
               'pageSize: number',
               'isStripTags: bool'
         ]
      }

   def getPressRelease(self):
      url = self.api_end_points['press-release']
      data = self.requestGETAPI(url=url)
      # base_file_url = self.get_full_url(self.api_end_points['fetch-security-files'])
      # for item in data:
      #    file_path = item.get('filePath')
      #    if file_path:
      #          item['fullFilePath'] = f"{base_file_url}{file_path}"
      return data

   def getNepseNotice(self, page=None):
      url = f"{self.api_end_points['nepse-notice']}?page={page}"
      data = self.requestGETAPI(url=url) or []
      base_file_url = self.get_full_url(self.api_end_points['fetch-files'])
      for item in data:
         try:
               content = item.get('content', {})
               file_path = content.get('noticeFilePath')
               if file_path:
                  item.setdefault('content', {})['fullNoticeFilePath'] = f"{base_file_url}{file_path}"
         except (AttributeError, TypeError):
               continue
      return data

   # def getTradingAverage(self, business_date=None, nDays=180):
   #    url=self.requestGETAPI(url=f"{self.api_end_points['trading-average']}?&nDays={nDays}&businessDate={business_date}")
   #    trading_average = self.requestGETAPI(
   #       url=url
   #    )
   #    # return a copy of self.holiday_list so than changes after return are not perisistent
   #    return list(trading_average)

   def getSecurityList(self):
      self.security_list = self.requestGETAPI(
         url=self.api_end_points["security_list_url"]
      )
      # return a copy of self.company_list so than changes after return are not perisistent
      return list(self.security_list)

   def getSectorScrips(self):
      if self.sector_scrips is None:
         company_info_dict = {
               company_info["symbol"]: company_info
               for company_info in self.getCompanyList()
         }
         sector_scrips = defaultdict(list)
         for security_info in self.getSecurityList():
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

   def getCompanyIDKeyMap(self, force_update=False):
      if self.company_symbol_id_keymap is None or force_update:
         company_list = self.getCompanyList()
         self.company_symbol_id_keymap = {
               company["symbol"]: company["id"] for company in company_list
         }
      return self.company_symbol_id_keymap

   def getSecurityIDKeyMap(self, force_update=False):
      if self.security_symbol_id_keymap is None or force_update:
         security_list = self.getSecurityList()
         self.security_symbol_id_keymap = {
               security["symbol"]: security["id"] for security in security_list
         }
      return self.security_symbol_id_keymap

   def getCompanyPriceVolumeHistory(self, symbol, start_date=None, end_date=None):
      from datetime import timedelta
      end_date = end_date if end_date else date.today()
      start_date = start_date if start_date else (end_date - timedelta(days=365))
      symbol = symbol.upper()
      company_id = self.getSecurityIDKeyMap()[symbol]
      url = f"{self.api_end_points['company_price_volume_history']}{company_id}?&size=500&startDate={start_date}&endDate={end_date}"
      return self.requestGETAPI(url=url)

   # api requiring post method
   def getDailyScripPriceGraph(self, symbol):
      symbol = symbol.upper()
      company_id = self.getSecurityIDKeyMap()[symbol]
      return self.requestPOSTAPI(
         url=f"{self.api_end_points['company_daily_graph']}{company_id}",
         payload_generator=self.getPOSTPayloadIDForScrips,
      )

   def getCompanyDetails(self, symbol):
      symbol = symbol.upper()
      company_id = self.getSecurityIDKeyMap()[symbol]
      return self.requestPOSTAPI(
         url=f"{self.api_end_points['company_details']}{company_id}",
         payload_generator=self.getPOSTPayloadIDForScrips,
      )

   def getCompanyFinancialDetails(self, company_id: str = None):
      url = f"{self.api_end_points['company-financial']}/{company_id}"
      data = list(self.requestGETAPI(url=url) or [])
      base_file_url = self.get_full_url(self.api_end_points['application-fetch-files'])
      base_sec_file_url = self.get_full_url(self.api_end_points['fetch-security-files'])
      for item in data:
         try:
               application_doc_list = item.get('applicationDocumentDetailsList', [])
               if not isinstance(application_doc_list, list):
                  continue
               for doc in application_doc_list:
                  encrypted_id = doc.get('encryptedId')
                  file_path = doc.get('filePath')
                  if file_path:
                     doc['fullFilePath'] = f"{base_sec_file_url}{file_path}"
                  if encrypted_id:
                     doc['fullEncryptedPath'] = f"{base_file_url}{encrypted_id}"
         except (AttributeError, TypeError, KeyError):
               continue
      return data

   def getCompanyAGM(self, company_id: str = None):
      url = f"{self.api_end_points['company-agm']}/{company_id}"
      data = list(self.requestGETAPI(url=url) or [])
      base_file_url = self.get_full_url(self.api_end_points['application-fetch-files'])
      for item in data:
         try:
               application_doc_list = item.get('applicationDocumentDetailsList', [])
               if not isinstance(application_doc_list, list):
                  continue
               for doc in application_doc_list:
                  encrypted_id = doc.get('encryptedId')
                  if encrypted_id:
                     doc['fullFilePath'] = f"{base_file_url}{encrypted_id}"
         except (AttributeError, TypeError, KeyError):
               continue
      return data

   def getCompanyDividend(self, company_id: str = None):
      url = f"{self.api_end_points['company-dividend']}/{company_id}"
      data = list(self.requestGETAPI(url=url) or [])
      base_file_url = self.get_full_url(self.api_end_points['application-fetch-files'])
      for item in data:
         try:
               application_doc_list = item.get('applicationDocumentDetailsList', [])
               if not isinstance(application_doc_list, list):
                  continue
               for doc in application_doc_list:
                  encrypted_id = doc.get('encryptedId')
                  if encrypted_id:
                     doc['fullFilePath'] = f"{base_file_url}{encrypted_id}"
         except (AttributeError, TypeError, KeyError):
               continue
      return data

   def getCompanyMarketDepth(self, company_id: str = None):
      url = f"{self.api_end_points['company-market-depth']}/{company_id}"
      data = self.requestGETAPI(url=url) or []
      return data

   def getFloorSheet(self, show_progress=False, paginated=False, page=None):
      url = f"{self.api_end_points['floor_sheet']}?&size={self.floor_sheet_size}&sort=contractId,desc"
      if page is not None:
         # Fetch only the specified page
         page_url = f"{url}&page={page}"
         sheet = self.requestPOSTAPI(
               url=page_url, payload_generator=self.getPOSTPayloadIDForFloorSheet
         )
         floor_sheets = sheet["floorsheets"]
         return floor_sheets
      # Fetch all pages
      sheet = self.requestPOSTAPI(
         url=url, payload_generator=self.getPOSTPayloadIDForFloorSheet
      )
      floor_sheets = sheet["floorsheets"]["content"]
      max_page = sheet["floorsheets"]["totalPages"]
      page_range = (
         tqdm.tqdm(range(1, max_page)) if show_progress else range(1, max_page)
      )
      all_pages = [floor_sheets]
      for page_number in page_range:
         current_sheet = self.requestPOSTAPI(
               url=f"{url}&page={page_number}",
               payload_generator=self.getPOSTPayloadIDForFloorSheet,
         )
         current_sheet_content = current_sheet["floorsheets"]["content"]
         all_pages.append(current_sheet_content)
      if paginated:
         return all_pages
      # Flatten all pages into a single list
      return [row for page in all_pages for row in page]

   def getFloorSheetOf(self, symbol, business_date=None):
      # business date can be YYYY-mm-dd string or date object
      symbol = symbol.upper()
      company_id = self.getSecurityIDKeyMap()[symbol]
      business_date = (
         date.fromisoformat(f"{business_date}") if business_date else date.today()
      )
      url = f"{self.api_end_points['company_floorsheet']}{company_id}?&businessDate={business_date}&size={self.floor_sheet_size}&sort=contractid,desc"
      sheet = self.requestPOSTAPI(
         url=url, payload_generator=self.getPOSTPayloadIDForFloorSheet
      )
      if sheet:  # sheet might be empty
         floor_sheets = sheet["floorsheets"]["content"]
         for page in range(1, sheet["floorsheets"]["totalPages"]):
               next_sheet = self.requestPOSTAPI(
                  url=f"{url}&page={page}",
                  payload_generator=self.getPOSTPayloadIDForFloorSheet,
               )
               next_floor_sheet = next_sheet["floorsheets"]["content"]
               floor_sheets.extend(next_floor_sheet)
      else:
         floor_sheets = []
      return floor_sheets

   def getSymbolMarketDepth(self, symbol):
      symbol = symbol.upper()
      company_id = self.getSecurityIDKeyMap()[symbol]
      url = f"{self.api_end_points['market-depth']}{company_id}/"
      return self.requestGETAPI(url=url)
