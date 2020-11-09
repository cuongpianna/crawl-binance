import scrapy
from datetime import datetime
from scrapy import Request
import html2text

from demo.items import NewsItem


class VietnamChamberOfCommerceAndIndustry(scrapy.Spider):
    name = 'VietnamChamberOfCommerceAndIndustry'
    site_name = 'vhdn.vn'
    allowed_domains = ['vhdn.vn']
    start_urls = ['https://vhdn.vn/tin-tuc-vcci/', 'https://vhdn.vn/van-hoa-doanh-nhan/',
                  'https://vhdn.vn/van-hoa-doanh-nhan/', 'https://vhdn.vn/phap-luat/',
                  'https://vhdn.vn/ket-noi-doanh-nghiep/', 'https://vhdn.vn/clb-van-hoa-doanh-nhan/',
                  'https://vhdn.vn/quy-le-luu/']

    def parse(self, response):
        posts = response.xpath('//div[@class="content-page"]//article//div[@class="post_content"]/a').css(
            '::attr(href)')
        if posts:
            for post in posts:
                url_extract = post.extract()
                yield Request(url_extract, callback=self.parse_post)

        next_page = response.xpath('//li[@class="next"]/a')

        if next_page and posts:
            next_url = response.xpath('//li[@class="next"]/a').css('::attr(href)').get()
            yield Request(next_url)

    def parse_post(self, response):
        author = self.parse_author(response)
        time_format, short_date = self.parse_date(response)
        item = NewsItem(
            title=response.xpath('//h1/text()').get(),
            timestamp=time_format,
            content_html=response.xpath('//div[@class="post_content"]').get(),
            body=html2text.html2text(response.xpath('//div[@class="post_content"]').get()),
            link=response.url,
            subhead='',
            pic=self.parse_pictures(response),
            date=short_date,
            author=author
        )
        yield item

    def parse_date(self, response):
        # 12:46 sáng | 28/08/2020

        raw_time = response.xpath('//div[@class="datetime"]/span[@class="time"]/text()').get()
        hh_mm = raw_time.split(' ')[0]

        hour = int(hh_mm.split(':')[0])

        if 'sáng' in raw_time and hour == 12:
            hour = 0

        minute = hh_mm.split(':')[1]
        day = response.xpath('//div[@class="datetime"]/span[@class="day"]/text()').get()
        month = response.xpath('//div[@class="datetime"]/span[@class="month"]/span/text()').get().replace('/', '')
        year = response.xpath('//div[@class="datetime"]/span[@class="month"]/span/text()').get().replace('/', '')

        result = datetime(year=int(year), month=int(month), day=int(day), minute=int(minute), hour=hour)

        return result.isoformat(), '{}/{}/{}'.format(month, day, year)

    @staticmethod
    def parse_pictures(response):
        urls = response.xpath('//div[@class="post_content"]//img/@src').extract()
        if urls:
            result = '&&'.join(urls)
            return result
        else:
            return ''

    @staticmethod
    def parse_author(response):
        if response.xpath('//div[@class="post_content"]//p[@style="text-align: right;"]/strong/text()').get():
            return response.xpath('//div[@class="post_content"]//p[@style="text-align: right;"]/strong/text()').get()
        if response.xpath('//div[@class="post_content"]//p[@style="text-align: right;"]/strong/span/text()').get():
            return response.xpath('//div[@class="post_content"]//p[@style="text-align: right;"]/strong/span/text()').get()
