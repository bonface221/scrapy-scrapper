import scrapy
from scrapy.utils.response import open_in_browser
from scrapy import FormRequest
from bs4 import BeautifulSoup as bs
import pandas as pd
import requests
import json
from datetime import date


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
        '''
        official_record_payload = {
            '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$btnNameSearch',
            'ctl00$ContentPlaceHolder1$hfTab': '',
            'ctl00$ContentPlaceHolder1$pfirst_party': '',
            'ctl00$ContentPlaceHolder1$prec_date_from': f'{date.today().month}/{(date.today().day)-2}/{date.today().year}',
            'ctl00$ContentPlaceHolder1$prec_date_to': f'{date.today().month}/{date.today().day}/{date.today().year}',
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

    def step4(self, response):
        # open_in_browser(response)
        '''
        Reading the response using pandas to extract the table
        '''
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

            '''
            Changing this specific key value to a string so that it is easier to send vie http
            '''
            for i in my_data:
                if i['Blk']:
                    i['Blk'] = str(i['Blk'])
                else:
                    i['Blk'] = ''
            # This is just a sample data we expect from the response
            # sample_data = {
            #     "Clerk's File No": "2022 R 831976",
            #     "Doc Type": "LIS",
            #     "Rec Date": "11/1/2022",
            #     "Rec Book/Page": "33447 / 92",
            #     "Plat Book/Page": "149/220",
            #     'Blk': '5.0',
            #     'Legal': "LOT 2A",
            #     "Misc Ref": "2022-020673-CA-01 LISPCV",
            #     "First Party (Code)  Second Party (Code)":
            #     "HSBC BANK USA NA (D)  LARGAESPADA SILVIA",
            # }

            '''
            Making a request to the django backend url providing the data as the form data
            '''
            for data in my_data:
                yield requests.post('http://127.0.0.1:8000/available-cases', data=data)

    '''
    in the code below I wanted to get the csv open it and that could have made the work easier but it is 
    hard to get that so I opted to use pandas to read the tables

    use this code to run this script................
    ---------scrapy crawl miami to run it
    '''


# code below is not to be used ..................
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
