import os
import scrapy
from datetime import datetime
from scrapy import Request
import html2text
from scrapy_selenium import SeleniumRequest
from dateutil import parser
import time

from demo.items import NewsItem


class SecurityReviewSpider(scrapy.Spider):
    name = 'SecurityReview'
    url = 'https://www.ssc.gov.vn/ubck/faces/vi/vilinks/vipageslink/vilinksquery_aptc/tapchichungkhoan?_adf.ctrl-state=15rte8ayhf_18&_afrLoop=11809071372000'

    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'SELENIUM_DRIVER_NAME': 'chrome',
        'SELENIUM_DRIVER_EXECUTABLE_PATH': os.path.join(os.path.abspath(os.curdir), 'chromedriver.exe'),
        'SELENIUM_DRIVER_ARGUMENTS': ['headless']

    }

    # SELENIUM_DRIVER_ARGUMENTS=['headless']
    # SELENIUM_DRIVER_ARGUMENTS = ['non headless', '--start-maximized']

    def __init__(self, *args, **kwargs):
        self.driver = None
        super().__init__(*args, **kwargs)

    def start_requests(self):
        yield SeleniumRequest(url=self.url, callback=self.parse)

    def parse(self, response):
        print('ssssssss')
        urls = []
        self.driver = response.meta['driver']
        news_type = response.xpath('//*[@id="pt1:soc1::content"]/option/text()').extract()
        news_type = news_type[::-1]
        for t in news_type:

            self.driver.find_element_by_xpath(
                    '//*[@id="pt1:soc1::content"]/option[text()="{}"]'.format(t)).click()
            time.sleep(1)

            years = self.driver.find_elements_by_xpath('//*[@id="pt1:soc2::content"]/option')
            years = years[::-1]
            count = 0

            for year in years:
                yearss = self.driver.find_elements_by_xpath('//*[@id="pt1:soc2::content"]/option')
                yearss = yearss[::-1]

                yearss[count].click()

                time.sleep(.8)
                magazines = self.driver.find_elements_by_xpath('//*[@id="pt1:soc3::content"]/option')
                magazines = magazines[::-1]

                for index, magazine in enumerate(magazines):
                    magazines_flag = self.driver.find_elements_by_xpath('//*[@id="pt1:soc2::content"]/option')
                    magazines_flag = magazines_flag[::-1]

                    magazines_flag[index].click()


                    button = self.driver.find_element_by_xpath('//*[@id="pt1:ctb1"]/a')
                    time.sleep(.8)
                    self.driver.execute_script("arguments[0].click();", button)
                    time.sleep(.8)

                    posts = self.driver.find_elements_by_xpath('//*[@id="pt1:pbl24"]//a')
                    for p in posts:
                        href = p.get_attribute('href')
                        urls.append(href)
                        yield Request(href, callback=self.parse_post)

                count += 1

    def parse_post(self, response):
        time_format, short_date = self.parse_date(response)
        content, html = self.parse_content(response)
        item = NewsItem(
            title=html2text.html2text(response.xpath('//*[@id="pt1:pbl16"]').get()),
            body=content,
            original_link=response.url,
            subhead=html2text.html2text(response.xpath('//*[@id="pt1:pbl18"]').get()),
            pic_list='',
            date=short_date,
            author='',
            site='44_tap_chi_chung_khoan',
            source='',
            print=''
        )
        yield item

    def parse_date(self, response):
        """

        :param response: Time format: 15/12/2018
        :return:
        """
        raw_time = response.xpath('//*[@id="pt1:pbl20"]//tbody//td[2]/text()').get().strip()
        true_time = parser.parse(raw_time)
        publish_date = datetime(year=true_time.year, minute=true_time.minute, hour=true_time.hour,
                                day=true_time.day,
                                month=true_time.month)
        return publish_date.isoformat(), '{}/{}/{}'.format(true_time.month, true_time.day, true_time.year)

    def parse_content(self, response):
        raw_text = html2text.html2text(response.xpath('//*[@id="pt1:pbl13"]').get())
        raw_html = response.xpath('//*[@id="pt1:pbl18"]').get()
        return raw_text, raw_html
