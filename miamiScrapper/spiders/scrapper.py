import scrapy
from scrapy.utils.response import open_in_browser
from scrapy import FormRequest
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import json

class MiamiSpider(scrapy.Spider):
    name = 'miami'
    start_urls = [
        'https://www2.miami-dadeclerk.com/PremierServices/login.aspx']

    def parse(self, response):
        loginPayload = {
            'ctl00$cphPage$txtUserName': 'hirolex',
            'ctl00$cphPage$txtPassword': 'hirolex231',
            'ctl00$cphPage$btnLogin': 'Login',
            'ctl00$cphPage$registrationEmail': ''
        }
        yield FormRequest.from_response(response, formdata=loginPayload, callback=self.step2)

    def step2(self, response):
        # open_in_browser(response)
        official_records_url = 'https://onlineservices.miami-dadeclerk.com/officialrecords/StandardSearch.aspx'
        return scrapy.Request(official_records_url, method='GET', callback=self.step3)

    def step3(self, response):
        official_record_payload = {
            '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$btnNameSearch',
            'ctl00$ContentPlaceHolder1$hfTab': '',
            'ctl00$ContentPlaceHolder1$pfirst_party': '',
            'ctl00$ContentPlaceHolder1$prec_date_from': '11/01/2022',
            'ctl00$ContentPlaceHolder1$prec_date_to': '11/03/2022',
            'ctl00$ContentPlaceHolder1$pdoc_type': 'LIS',
            'ctl00$ContentPlaceHolder1$pcfn_year': '',
            'ctl00$ContentPlaceHolder1$pcfn_seq': '',
            'ctl00$ContentPlaceHolder1$prec_book': '',
            'ctl00$ContentPlaceHolder1$prec_page': '',
            'ctl00$ContentPlaceHolder1$prec_booktype': 'O',
            'ctl00$ContentPlaceHolder1$pplat_book': '',
            'ctl00$ContentPlaceHolder1$pplat_page': '',
            'ctl00$ContentPlaceHolder1$pblock_no': '',
            'ctl00$ContentPlaceHolder1$party_name': ''
        }

        yield FormRequest.from_response(response, formdata=official_record_payload, callback=self.step4)

    def step4(self, response):
        # open_in_browser(response)
        dfs = pd.read_html(response.text)
        # self.logger.info(dfs[0])
        for x, df in enumerate(dfs):
            # y = df.to_dict('tight')
            y = df.T.to_dict().values()

        my_data = list(y)

        for i in my_data:
            i['Blk'] = str(i['Blk'])
            
        
        trial= {"name":"bonface","School":"Moringa school"}

        print(my_data)

        yield requests.post('http://127.0.0.1:8000/available-cases',json=trial)


    # def django_auth(self,response):
    #     open_in_browser(response)

    #     yield FormRequest(response,'http://127.0.0.1:8000/available-cases',)
        
        # tbody = response.xpath('')
        
        

        # final_data_payload = {
        #     '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$exportResultSearch'
        # }
        # yield FormRequest.from_response(response, formdata=final_data_payload, callback=self.step5)

    # def step5(self, response):
        # open_in_browser(response)
        # open_in_browser(response)
    # table = response.css('#tableSearchResults"')
    # self.logger.info(response.body)

    # table = response.xpath('/html/body/div/form/main/div[1]/div[9]/div/div/div[2]/table').get()

    # path_1=response.url
    # path = response.url.split('/')
    # self.logger.info('Saving CSV %s',path)
    # self.logger.info(path_1)
    # with open(path,'wb') as f:
    #     f.write
