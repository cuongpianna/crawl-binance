import os
import scrapy
from datetime import datetime
from scrapy import Request
import html2text
from urllib.parse import urljoin
from scrapy_selenium import SeleniumRequest
from dateutil import parser
import time

from demo.items import NewsItem


class SecurityReviewSpider(scrapy.Spider):
    name = 'SecurityReview'
    # site_name = 'enternews.vn'
    # allowed_domains = ['enternews.vn']
    # base_url = 'https://enternews.vn/'
    url = 'https://www.ssc.gov.vn/ubck/faces/vi/vilinks/vipageslink/vilinksquery_aptc/tapchichungkhoan?_adf.ctrl-state=15rte8ayhf_18&_afrLoop=11809071372000'

    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'SELENIUM_DRIVER_NAME': 'chrome',
        'SELENIUM_DRIVER_EXECUTABLE_PATH': os.path.join(os.path.abspath(os.curdir), 'chromedriver.exe'),
    }

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

                time.sleep(1)
                magazines = self.driver.find_elements_by_xpath('//*[@id="pt1:soc3::content"]/option')
                magazines = magazines[::-1]

                for index, magazine in enumerate(magazines):
                    magazines_flag = self.driver.find_elements_by_xpath('//*[@id="pt1:soc2::content"]/option')
                    magazines_flag = magazines_flag[::-1]

                    magazines_flag[index].click()


                    button = self.driver.find_element_by_xpath('//*[@id="pt1:ctb1"]/a')
                    time.sleep(1)
                    self.driver.execute_script("arguments[0].click();", button)
                    time.sleep(1)

                    posts = self.driver.find_elements_by_xpath('//*[@id="pt1:pbl24"]//a')
                    for p in posts:
                        href = p.get_attribute('href')
                        urls.append(href)
                        yield Request(href, callback=self.parse_post)

                count += 1
        print('@@@@@@@@@@@')
        print(urls)
        time.sleep(5)

    def parse_post(self, response):
        print('!!!!!!!!')
        print(response)
        # time_format, short_date = self.parse_date(response)
        # content, html = self.parse_content(response)
        # if response.xpath('//h1[@class="post-title main-title"]/text()').get():
        #     item = NewsItem(
        #         title=response.xpath('//h1[@class="post-title main-title"]/text()').get(),
        #         timestamp=time_format,
        #         content_html=content,
        #         body=html,
        #         link=response.url,
        #         subhead=response.xpath('//h2[@class="post-sapo"]/strong/text()').get(),
        #         pic=self.parse_pictures(response),
        #         date=short_date,
        #         author=''
        #     )
        #     yield item
    #
    # def parse_date(self, response):
    #     print(response.xpath('//script[@type="application/ld+json"][3]'))
    #     if response.xpath('//div[@class="post-author cl"]/span/text()').get():
    #         raw_time = response.xpath('//div[@class="post-author cl"]/span/text()').get().replace('| ', '').strip()
    #         true_time = parser.parse(raw_time)
    #         publish_date = datetime(year=true_time.year, minute=true_time.minute, hour=true_time.hour,
    #                                 day=true_time.day,
    #                                 month=true_time.month)
    #         return publish_date.isoformat(), '{}/{}/{}'.format(true_time.month, true_time.day, true_time.year)
    #     else:
    #         print(response.xpath('//body'))
    #         return '', ''
    #
    # def parse_pictures(self, response):
    #     urls = response.xpath('//img[@class="image_center"]/@src').extract()
    #     urls = [urljoin(self.base_url, item) for item in urls]
    #     captions = response.xpath('//img[@class="image_center"]/@alt').extract()
    #     res = [i + '|' + j for i, j in zip(urls, captions)]
    #     if urls:
    #         result = '&&'.join(res)
    #         return result
    #     else:
    #         return ''
    #
    # def parse_content(self, response):
    #     raw_text = response.xpath('//div[@class="post-content "]/p/text()').extract()
    #     raw_html = response.xpath('//div[@class="post-content "]/p').extract()
    #     return ' '.join(raw_text), ' '.join(raw_html)
