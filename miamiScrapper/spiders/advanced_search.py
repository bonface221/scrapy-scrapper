from bs4 import BeautifulSoup as bs
import scrapy
from scrapy.utils.response import open_in_browser
from scrapy import FormRequest
import pandas as pd
import requests
import json
from datetime import date
from math import nan,isnan

# THIS IS THE ADVANCED SEARCH =>URL 2  'https://www2.miami-dadeclerk.com/ocs/Search.aspx?type=premier'
class MiamiSpider(scrapy.Spider):
    name = 'advanced'
    advanced_records_url = 'https://www2.miami-dadeclerk.com/ocs/Search.aspx?type=premier'
    start_urls = [
        'https://www2.miami-dadeclerk.com/PremierServices/login.aspx']

    def parse(self, response):
        # SENDING A LOGIN REQUEST TO THE WEBSITE
        loginPayload = {
            'ctl00$cphPage$txtUserName': 'hirolex',
            'ctl00$cphPage$txtPassword': 'hirolex231',
            'ctl00$cphPage$btnLogin': 'Login',
            'ctl00$cphPage$registrationEmail': ''
        }
        yield FormRequest.from_response(response, formdata=loginPayload, callback=self.step2)

    def step2(self, response):
        # open_in_browser(response)
        # RESPONSE IS BACK NOW WE ARE LOGGED IN
        # WE CAN CONTINUE WITH THE SCRAPPING

        return scrapy.Request(self.advanced_records_url, method='GET', callback=self.step3)

    def step3(self, response):
        # SENDING CREADENTIALS TO THE SERVER AND GETTING A RESPONSE WHICH NEEDS TO BE CLICKED TO EXPOSE DOCKETS AND PARIES
        '''
        CaseType FIELDS explained=>
        # ctl00$ContentPlaceHolder1$ddlCaseType_PRM_generalContent
        RPMF COMMERCIAL =>27185
        RPMF HOMESTEAD =>27186
        RPMF NON-HOMESTEAD =>27187
        '''

        # Check these dates these are hard- coded which was for testing there is 
        # if there was a way to create dynamic data that would be nice
        # 'ctl00$ContentPlaceHolder1$pFiling_Date_From_generalContent': '11/1/2022',
        #'ctl00$ContentPlaceHolder1$pFiling_Date_To_generalContent': '11/3/2022',
        # 

        # open_in_browser(response)
        advanced_payload = {
            '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$btnGeneralSearch',
            'ctl00$ContentPlaceHolder1$lastTab': '',
            'ctl00$ContentPlaceHolder1$txtLCNYear_generalContent': '',
            'ctl00$ContentPlaceHolder1$txtLCNSeq_generalContent': '',
            'ctl00$ContentPlaceHolder1$LCNCodeDropList_generalContent': '--',
            'ctl00$ContentPlaceHolder1$txtLCNLoc_generalContent': '',
            'ctl00$ContentPlaceHolder1$txtSCNYear_generalContent': '',
            'ctl00$ContentPlaceHolder1$txtSCNCode_generalContent': '--',
            'ctl00$ContentPlaceHolder1$txtSCNSeq_generalContent': '',
            'ctl00$ContentPlaceHolder1$txtSCNPartyId_generalContent': '0000',
            'ctl00$ContentPlaceHolder1$txtSCNLoc_generalContent': '',
            'ctl00$ContentPlaceHolder1$txtPartyName1_generalContent': '',
            'ctl00$ContentPlaceHolder1$ddlPartyType_PRM_generalContent': '',
            'ctl00$ContentPlaceHolder1$pP1_Atty_Bar_Num_generalContent': '',
            'ctl00$ContentPlaceHolder1$txtPartyName2_generalContent': '',
            'ctl00$ContentPlaceHolder1$pFiling_Date_From_generalContent': '11/1/2022',
            'ctl00$ContentPlaceHolder1$pFiling_Date_To_generalContent':'11/3/2022',
            'ctl00$ContentPlaceHolder1$ddlSections_generalContent': '',
            'ctl00$ContentPlaceHolder1$ddlCaseType_PRM_generalContent': '27187',
            'ctl00$ContentPlaceHolder1$txtImgBook_generalContent': '',
            'ctl00$ContentPlaceHolder1$txtImgPage_generalContent': '',
            'ctl00$ContentPlaceHolder1$txtLCNYearDockets': '',
            'ctl00$ContentPlaceHolder1$txtLCNSeqDockets': '',
            'ctl00$ContentPlaceHolder1$DropDownListLCNCodeDockets': '--',
            'ctl00$ContentPlaceHolder1$txtLCNLocDockets_generalContent': '',
            'ctl00$ContentPlaceHolder1$txtSCNYearDockets': '',
            'ctl00$ContentPlaceHolder1$DropDownListtxtSCNCourtDockets': '--',
            'ctl00$ContentPlaceHolder1$txtSCNSeqDockets': '',
            'ctl00$ContentPlaceHolder1$txtSCNPartyIdDockets': '0000',
            'ctl00$ContentPlaceHolder1$txtSCNLocDockets': '',
            'ctl00$ContentPlaceHolder1$ddlDockets1': '',
            'ctl00$ContentPlaceHolder1$ddlDockets2': '',
            'ctl00$ContentPlaceHolder1$txtDocketDateFrom': '',
            'ctl00$ContentPlaceHolder1$txtDocketDateTo': '',
            'ctl00$ContentPlaceHolder1$attorneyBarNumberHidden_myHearingContent': '',
            'ctl00$ContentPlaceHolder1$txtHearingStartDate_advancedHearingContent': '',
            'ctl00$ContentPlaceHolder1$txtHearingEndDate_advancedHearingContent': '',
            'ctl00$ContentPlaceHolder1$attorneyBarNumberHidden_myCaseContent': '',
            'ctl00$ContentPlaceHolder1$myCasesStartDate_myCaseContent': '',
            'ctl00$ContentPlaceHolder1$myCasesEndDate_myCaseContent': '',
            'ctl00$ContentPlaceHolder1$ddlCaseType_PRM_myCasesContent': '',
            'ctl00$ContentPlaceHolder1$ddlSections_myCasesContent': '',
        }

        yield FormRequest.from_response(response, formdata=advanced_payload, callback=self.step4)

    def step4(self, response):
        # Response is back we can now immitate a click......and we get the details of the click .....
        # Here we need to send this to the server I just hardcoded the event target of the first result => so we only get results for the first item.
        no_search_found = response.xpath(
            '//*[@id="ctl00_ContentPlaceHolder1_panelNoResults"]/div/text()').get()

        if not no_search_found:
            final_click_payload = {
                '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$reResults$ctl00$ctl01',
                'ctl00$ContentPlaceHolder1$lastTab': ''
                }
            yield FormRequest.from_response(response,formdata=final_click_payload, callback=self.step5)

    def step5(self, response):
        # We now manipulate the data using pandas and send back to the server which is our django app
        # open_in_browser(response)

        try:
            dfs2 = response.xpath('//*[@id="bodySearchCriteria"]/table').get()

        except TypeError:
            return

        try:
            dfs2_read= pd.read_html(dfs2,na_values=str)

        except ValueError:
            return
        # self.logger.info(dfs[0])
        

        for x, df in enumerate(dfs2_read):
            # y = df.to_dict('tight')
            y = df.T.to_dict().values()
            # y = df.to_dict('records')
        
        if list(y):
            my_data = list(y)
            cleaned_data = []
            for i in my_data:
                if i == my_data[-1]:
                    break
                i[3] = ''
                my_dict = {}
                my_dict['Party Description'] = i[0]
                my_dict['Party Name'] = i[1]
                my_dict['Attorney Information'] = i[2]
                cleaned_data.append(my_dict)

            # print(cleaned_data)

            
            for data in cleaned_data:
                yield requests.post('http://127.0.0.1:8000/Advanced-search-results',data=data)

        dockets_list = []

        dfs = pd.read_html(response.text)

        for x, df in enumerate(dfs):
            # y = df.to_dict('tight')
            z = df.T.to_dict().values()

        if list(z):
            my_data_dockets = list(z)

            for i in my_data_dockets:
                if i['Number']:
                    i['Number'] = str(i['Number'])
                else:
                    i['Number']=''
                dockets_dict = {}
                dockets_dict['Number'] = str(i['Number'])
                dockets_dict['Date'] = i['Date']
                dockets_dict['Book/Page'] = i['Book/Page']
                dockets_dict['Docket Entry'] = i['Docket Entry']
                dockets_dict['Event Type'] = i['Event Type']
                dockets_dict['Comments'] = i['Comments']

                dockets_list.append(dockets_dict)
            
            for data_dockets in dockets_list:
                yield requests.post('http://127.0.0.1:8000/Advanced-search-results',data=data_dockets)
            local_case_number = response.xpath('//*[@id="ctl00_ContentPlaceHolder1_lblCaseNoLocal"]/text()').get()
            local_case_dict={
                'case_number':local_case_number
            }
            yield requests.post('http://127.0.0.1:8000/Advanced-search-results',data=local_case_dict)
            
