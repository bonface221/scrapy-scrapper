from bs4 import BeautifulSoup as bs
import scrapy
from scrapy.utils.response import open_in_browser
from scrapy import FormRequest
import pandas as pd
import requests
import json


class MiamiSpider(scrapy.Spider):
    name = 'advanced'
    advanced_records_url = 'https://www2.miami-dadeclerk.com/ocs/Search.aspx?type=premier'
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

        return scrapy.Request(self.advanced_records_url, method='GET', callback=self.step3)

    def step3(self, response):
        '''
        CaseType FIELDS explained=>
        # ctl00$ContentPlaceHolder1$ddlCaseType_PRM_generalContent
        RPMF COMMERCIAL =>27185
        RPMF HOMESTEAD =>27186
        RPMF NON-HOMESTEAD =>27187
        '''
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
            'ctl00$ContentPlaceHolder1$pFiling_Date_From_generalContent': '11/01/2022',
            'ctl00$ContentPlaceHolder1$pFiling_Date_To_generalContent': '11/03/2022',
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

        final_click_payload = {
            '__EVENTTARGET': 'ctl00$ContentPlaceHolder1$reResults$ctl00$ctl01',
            'ctl00$ContentPlaceHolder1$lastTab': ''
            }
        yield FormRequest.from_response(response,formdata=final_click_payload, callback=self.step5)

    def step5(self, response):
        open_in_browser(response)
        dfs = pd.read_html(response.text)
        # self.logger.info(dfs[0])
        for x, df in enumerate(dfs):
            # y = df.to_dict('tight')
            y = df.T.to_dict().values()

        my_data = list(y)
        print(my_data)
