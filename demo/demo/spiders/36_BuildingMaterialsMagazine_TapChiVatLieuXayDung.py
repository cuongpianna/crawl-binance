import scrapy
import urllib.parse
import re
from datetime import datetime
from scrapy import Spider, Request
import html2text
from dateutil import parser

from demo.items import NewsItem


class BuildingMaterialsMagazineSpider(scrapy.Spider):
    name = 'BuildingMaterialsMagazine'
    site_name = 'http://tapchivatlieuxaydung.vn/'
    allowed_domains = ['tapchivatlieuxaydung.vn']

    base_url = 'http://tapchivatlieuxaydung.vn'
    start_urls = ['http://tapchivatlieuxaydung.vn/tin/mua-gi-o-dau-1137-1',
                  'https://nguoixaydung.com.vn/chuyen-muc/xay-dunghttp://tapchivatlieuxaydung.vn/tin/thoi-su-1132-1',
                  'http://tapchivatlieuxaydung.vn/tin/thi-truong-vat-lieu-xay-dung-1133-1',
                  'http://tapchivatlieuxaydung.vn/tin/dau-tu-xanh-1131-1',
                  'http://tapchivatlieuxaydung.vn/tin/tai-chinh-ngan-hang-1150-1',
                  'http://tapchivatlieuxaydung.vn/tin/khoa-hoc-cong-nghe-1136-1'
                  ]

    def parse(self, response):
        posts = response.xpath('//article[@class="post"]//h3/a').css('::attr(href)')

        if posts:
            for post in posts:
                url_extract = urllib.parse.urljoin(self.base_url, post.extract())
                yield Request(url_extract, callback=self.parse_post)

        next_page = response.xpath('//*[@id="pagination"]/li/a[@hidden="hidden"]')

        if not next_page:
            next_url = response.xpath('//*[@id="pagination"]/li[last()]/a"]').css('::attr(href)').get()
            yield Request(next_url)

    def parse_post(self, response):
        author = self.parse_author(response)
        time_format, short_date = self.parse_date(response)
        item = NewsItem(
            title=response.xpath('//h1/text()').get(),
            body=html2text.html2text(response.xpath('//div[@class="entry-post"]').get()),
            original_link=response.url,
            subhead='',
            pic_list=self.parse_pictures(response),
            date=short_date,
            author=author,
            site='tap_chi_vat_lieu_xay_dung',
            source='',
            print=''
        )
        yield item

    def parse_date(self, response):
        """
        :param response: Đăng lúc 8/8/2020 12:00:00 AM
        :return:
        """
        created_raw = response.xpath('//div[@class="meta"]/span/text()').get().strip()
        match_time = re.search(r'\d{1,2}\/\d{1,2}\/\d{4} \d{2}:\d{2}:\d{2}', created_raw).group(0)
        true_time = parser.parse(match_time)
        publish_date = datetime(year=true_time.year, minute=true_time.minute, hour=true_time.hour, day=true_time.day,
                                month=true_time.month)
        return publish_date.isoformat(), '{}/{}/{}'.format(true_time.month, true_time.day, true_time.year)

    @staticmethod
    def parse_pictures(response):
        urls = response.xpath('//div[@class="entry-post"]//img/@src').extract()
        if urls:
            result = '&&'.join(urls)
            return result
        else:
            return ''

    @staticmethod
    def parse_author(response):
        return response.xpath('//div[@class="entry-post"]/p[@style="text-align: right;"]/strong/text()').get()
