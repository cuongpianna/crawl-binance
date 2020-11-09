import scrapy
from datetime import datetime
from scrapy import Request
import html2text
from urllib.parse import urljoin
from scrapy_selenium import SeleniumRequest
from dateutil import parser
import time

from demo.items import NewsItem


class EnterpriseForumNewspaper(scrapy.Spider):
    name = 'EnterpriseForumNewspaper'
    site_name = 'enternews.vn'
    allowed_domains = ['enternews.vn']
    start_urls = ['https://enternews.vn/thoi-su-c82']
    base_url = 'https://enternews.vn/'

    # custom_settings = {
    #     'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    #     'SELENIUM_DRIVER_NAME': 'chrome',
    #     'SELENIUM_DRIVER_EXECUTABLE_PATH': 'D:\WORKING\DEMO\demo\chromedriver.exe',
    #
    # }

    def parse(self, response):

        top_item = response.xpath('//div[@class="top-item"]//h2/a').css('::attr(href)').get()
        if top_item:
            yield Request(top_item, callback=self.parse_post)

        scroll_news = response.xpath('//div[@id="top-news-scroll"]/ul/li//a[@class="font-16"]').css('::attr(href)')
        if scroll_news:
            for new in scroll_news:
                yield Request(new.extract(), callback=self.parse_post)

        posts = response.xpath('//ul[@class="feed"]/li/h2/a').css('::attr(href)')

        for post in posts:
            url_extract = post.extract()
            yield SeleniumRequest(url=url_extract, callback=self.parse_post)

        next_page = response.xpath('//a[@class="btn btn-xs font-14 btn-primary"]')

        if next_page:
            next_url = response.xpath('//a[@class="btn btn-xs font-14 btn-primary"]').css('::attr(href)').get()
            yield SeleniumRequest(url=next_url)

    def parse_post(self, response):
        time_format, short_date = self.parse_date(response)
        content, html = self.parse_content(response)
        # print(content)
        item = NewsItem(
            title=response.xpath('//h1[@class="post-title main-title"]/text()').get(),
            timestamp=time_format,
            content_html=content,
            body=html,
            link=response.url,
            subhead=response.xpath('//h2[@class="post-sapo"]/strong/text()').get(),
            pic=self.parse_pictures(response),
            date=short_date,
            author=''
        )
        yield item

    def parse_date(self, response):
        print('@@@@@@@@@@@@@@')
        print(response.xpath('//script[@type="application/ld+json"][3]'))
        if response.xpath('//div[@class="post-author cl"]/span/text()').get():
            raw_time = response.xpath('//div[@class="post-author cl"]/span/text()').get().replace('| ', '').strip()
            true_time = parser.parse(raw_time)
            publish_date = datetime(year=true_time.year, minute=true_time.minute, hour=true_time.hour, day=true_time.day,
                                    month=true_time.month)
            return publish_date.isoformat(), '{}/{}/{}'.format(true_time.month, true_time.day, true_time.year)
        else:
            print(response.xpath('//body'))
            return '', ''

    def parse_pictures(self, response):
        urls = response.xpath('//img[@class="image_center"]/@src').extract()
        urls = [urljoin(self.base_url, item) for item in urls]
        captions = response.xpath('//img[@class="image_center"]/@alt').extract()
        res = [i + '|' + j for i, j in zip(urls, captions)]
        if urls:
            result = '&&'.join(res)
            return result
        else:
            return ''

    def parse_content(self, response):
        raw_text = response.xpath('//div[@class="post-content "]/p/text()').extract()
        raw_html = response.xpath('//div[@class="post-content "]/p').extract()
        return ' '.join(raw_text), ' '.join(raw_html)
