import scrapy
from scrapy.utils.response import open_in_browser
from scrapy import FormRequest
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import json
from datetime import date
from math import isnan,nan


class MiamiSpider(scrapy.Spider):
    #  This is the spider name
    name = 'miami'

    # This is the start url ->
    start_urls = [
        'https://www2.miami-dadeclerk.com/PremierServices/login.aspx']

    def parse(self, response):
        '''
        providing login credentials and using the previous request to store sessions
        '''
        loginPayload = {
            'ctl00$cphPage$txtUserName': 'hirolex',
            'ctl00$cphPage$txtPassword': 'hirolex231',
            'ctl00$cphPage$btnLogin': 'Login',
            'ctl00$cphPage$registrationEmail': ''
        }
        yield FormRequest.from_response(response, formdata=loginPayload, callback=self.step2)

    def step2(self, response):
        '''
        After getting a response the response can be opened in a browser or  since
        we are logged in we can continue with the scrapping
        '''
        # open_in_browser(response)
        official_records_url = 'https://onlineservices.miami-dadeclerk.com/officialrecords/StandardSearch.aspx'
        return scrapy.Request(official_records_url, method='GET', callback=self.step3)

    def step3(self, response):
        '''
        Here in the official payload its where we can pass dynamic data like how someone
        navigates the miami-dade website inputs the date to and from
        I'm just getting todays date and subtracting a day before to get the date for that day.....
        so that is actually a day search

        'ctl00$ContentPlaceHolder1$prec_date_from': f'{date.today().month}/{(date.today().day)-2}/{date.today().year}',
        'ctl00$ContentPlaceHolder1$prec_date_to': f'{date.today().month}/{date.today().day}/{date.today().year}',
        '''
        official_record_payload = {
            '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$btnNameSearch',
            'ctl00$ContentPlaceHolder1$hfTab': '',
            'ctl00$ContentPlaceHolder1$pfirst_party': '',
            'ctl00$ContentPlaceHolder1$prec_date_from': '11/1/2022',
            'ctl00$ContentPlaceHolder1$prec_date_to': '11/2/2022',
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

        '''
        Providing the final form data payload
        '''

        yield FormRequest.from_response(response, formdata=official_record_payload, callback=self.step4)

        # official_record_payload_pagination={
        #     '__EVENTTARGET':f'ctl00$ContentPlaceHolder1$rptPaging$ctl0{}$ctl00',
        # }

    def step4(self, response):
        # open_in_browser(response)
        '''
        Reading the response using pandas to extract the table

        '''
        yield scrapy.FormRequest(url='https://onlineservices.miami-dadeclerk.com/officialrecords/PrinterFriendly.aspx', callback=self.printer_friendly)
    
    def printer_friendly(self,response):
        # open_in_browser(response)

        try:
            dfs = pd.read_html(response.text)

        except ValueError:
            return

        # self.logger.info(dfs[0])
        for x, df in enumerate(dfs):
            # y = df.to_dict('tight')
            y = df.T.to_dict().values()

        if list(y):
            my_data = list(y)

        for case in my_data:
            if type(case['Rec Book/Page']) is not str:
                case['Rec Book/Page']=''
            if type(case['Blk']) is not str:
                case['Blk']=''
            if type(case['Misc Ref']) is not str:
                case['Misc Ref'] = ''
            if type(case['Plat Book/Page']) is not str:
                case['Plat Book/Page'] = ''

        
            

            
        for case in my_data:
            if len(case['Misc Ref'])>0:
                case['Misc Ref'] = case['Misc Ref'].split(' ')[0]

        for data in my_data:
            yield requests.post('http://127.0.0.1:8000/available-cases',data=data)

        
            # print(data)

        # next_btns_length = len(response.xpath(
        #     '//*[@id="content"]/div[1]/div[9]/div/div/div[4]/div/div[2]/ul/li').getall())
        

        # print(next_btns_length)

        # if next_btns_length > 0:

        #     for i in range(1, next_btns_length):
        #         yield FormRequest(
        #             'https://onlineservices.miami-dadeclerk.com/officialrecords/StandardSearch.aspx',formdata={})
                


        # try:
        #     dfs = pd.read_html(response.text)

        # except ValueError:
        #     return

        # # self.logger.info(dfs[0])
        # for x, df in enumerate(dfs):
        #     # y = df.to_dict('tight')
        #     y = df.T.to_dict().values()

        # if list(y):
        #     my_data = list(y)

        # #     '''
        # #     Changing this specific key value to a string so that it is easier to send vie http
        # #     '''

        #     for i in my_data:
        #         if i['Blk']:
        #             i['Blk'] = str(i['Blk'])
        #         else:
        #             i['Blk'] = ''

        #     # This is just a sample data we expect from the response
        #     # sample_data = {
        #     #     "Clerk's File No": "2022 R 831976",
        #     #     "Doc Type": "LIS",
        #     #     "Rec Date": "11/1/2022",
        #     #     "Rec Book/Page": "33447 / 92",
        #     #     "Plat Book/Page": "149/220",
        #     #     'Blk': '5.0',
        #     #     'Legal': "LOT 2A",
        #     #     "Misc Ref": "2022-020673-CA-01 LISPCV",
        #     #     "First Party (Code)  Second Party (Code)":
        #     #     "HSBC BANK USA NA (D)  LARGAESPADA SILVIA",
        #     # }


        #     # '''
        #     # Making a request to the django backend url providing the data as the form data
        #     # '''

        #     for data in my_data:
        #         yield scrapy.FormRequest('http://127.0.0.1:8000/available-cases', formdata=data)
        #         # yield scrapy.request('http://127.0.0.1:8000/available-cases', data=data ,callback=self.step5, meta={'data':response})
        #         # print(data)

    # def step5(self, data):
    #     response = data
    #     try:
    #         dfs = pd.read_html(response.text)
        
    #     except ValueError:
    #         return

    #     # self.logger.info(dfs[0])
    #     for x, df in enumerate(dfs):
    #         # y = df.to_dict('tight')
    #         y = df.T.to_dict().values()

    #     if list(y):
    #         my_data = list(y)

    #     #     '''
    #     #     Changing this specific key value to a string so that it is easier to send vie http
    #     #     '''
    #         for i in my_data:
    #             if i['Blk']:
    #                 i['Blk'] = str(i['Blk'])
    #             else:
    #                 i['Blk'] = ''

            
    #         for data in my_data:
    #             yield scrapy.FormRequest('http://127.0.0.1:8000/available-cases',formdata=data, callback=self.step5)
    #             # yield scrapy.request('http://127.0.0.1:8000/available-cases', data=data ,callback=self.step5, meta={'data':response})
    #             # print(data)
    



    '''

    use this code to run this script................
    ---------scrapy crawl miami to run it

    '''


