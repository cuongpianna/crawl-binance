import scrapy
import urllib.parse
import re
from datetime import datetime
from scrapy import Spider, Request
import html2text

from demo.items import NewsItem


class CatholicAndEthnicNewspaperSpider(scrapy.Spider):
    name = 'CatholicAndEthnicNewspaper'
    site_name = 'cgvdt.vn'
    allowed_domains = ['cgvdt.vn']
    start_urls = ['http://www.cgvdt.vn/ban-doc_at15', 'http://www.cgvdt.vn/giao-hoi-viet-nam_at44',
                  'http://www.cgvdt.vn/cong-giao-viet-nam_at7',
                  'http://www.cgvdt.vn/cong-giao-viet-nam/dau-chan-muc-tu_at61',
                  'http://www.cgvdt.vn/cong-giao-the-gioi_at6', 'http://www.cgvdt.vn/loi-chua-va-cuoc-song_at8',
                  'http://www.cgvdt.vn/duc-giam-muc-bui-tuan_at9', 'http://www.cgvdt.vn/linh-muc-ngo-phuc-hau_at10',
                  'http://www.cgvdt.vn/xa-hoi_at89']

    def parse(self, response):
        current_page = response.xpath('//li[@class="page-number pgCurrent"]/text()').get()

        if current_page != '1':
            hentry_post = response.xpath('//div[@class="news_home hentry"]/a').css('::attr(href)').get()

            yield Request(hentry_post, callback=self.parse_post)

            hot_news = response.xpath('//ul[@id="divTinMoi"]/li/a').css('::attr(href)').extract()

            for post in hot_news:
                yield Request(post, callback=self.parse_post)

            views_news = response.xpath('//ul[@id="divTinXemNhieu"]/li/a').css('::attr(href)').extract()

            for post in views_news:
                yield Request(post, callback=self.parse_post)

        posts = response.xpath('//div[@class="news_row hentry"]/a').css('::attr(href)')

        for post in posts:
            url_extract = post.extract()
            yield Request(url_extract, callback=self.parse_post)

        next_page = response.xpath('//li[@class="pgNext"]/a')

        if next_page:
            next_url = response.xpath('//li[@class="pgNext"]/a').css('::attr(href)').get()
            yield Request(next_url)

    def parse_post(self, response):
        # author = response.xpath('//div[@class="author"]').css('::text').extract()[1] if \
        #     response.xpath('//div[@class="author"]').css('::text').extract()[1] else ''
        item = NewsItem(
            # title=response.xpath('//h1/text()').get(),
            # timestamp=self.parse_timestamp(response),
            # content_html=response.xpath('//div[@class="news_content entry-content"]').get(),
            # body=html2text.html2text(response.xpath('//div[@class="news_content entry-content"]').get()),
            # link=response.url,
            # subhead='',
            # pic=self.parse_pictures(response),
            date=self.parse_date(response),
            author=''
        )
        yield item

    @staticmethod
    def parse_timestamp(response):
        # 07/10/2020 05:28 GMT+7
        created_raw = response.xpath('//body//div[@class="date-time"]/text()').get()
        created_raw = created_raw.replace("GMT+7", "GMT+0700")
        created_at = datetime.strptime(created_raw.strip(), '%d/%m/%Y %H:%M %Z%z')
        return created_at

    def parse_date(self, response):
        # 07/10/2020
        created_raw = response.xpath('//p[@class="date published"]').get()
        print(created_raw)
        date_split = created_raw.split(',')
        day_month = date_split[1].strip().split(' ', 1)
        print(day_month)
        month = self.convert_month(day_month[1])
        print(month)
        # created_raw = created_raw.replace("GMT+7", "GMT+0700")
        # created_at = datetime.strptime(created_raw.strip(), '%d/%m/%Y %H:%M %Z%z')
        # return created_at.strftime('%m/%d/%Y')
        return 12

    @staticmethod
    def parse_pictures(response):
        urls = response.xpath('//div[@id="main-detail-body"]//div[@type="Photo"]//img/@src').extract()
        captions = response.xpath('//div[@id="main-detail-body"]//div[@type="Photo"]//img/@title').extract()
        res = [i + '|' + j for i, j in zip(urls, captions)]
        if urls:
            result = '&&'.join(res)
            return result
        else:
            return ''

    @staticmethod
    def convert_month(month):
        month = month.strip()
        # print(month)
        # print('Tháng Tư')
        # print(month == 'Tháng Tư')
        if month == 'Thang Tám':
            return 8
        elif month == 'Tháng Tư':
            return 4
        elif month == 'Tháng Chín':
            return 9
        elif month == 'Tháng Mười':
            return 10