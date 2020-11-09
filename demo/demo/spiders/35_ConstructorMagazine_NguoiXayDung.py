import scrapy
import urllib.parse
from datetime import datetime
from scrapy import Request
import html2text

from demo.items import NewsItem


class ConstructorMagazineSpider(scrapy.Spider):
    name = 'ConstructorMagazine'
    site_name = 'nguoixaydung.com.vn'
    allowed_domains = ['nguoixaydung.com.vn']

    base_url = 'https://nguoixaydung.com.vn'
    start_urls = ['https://nguoixaydung.com.vn/chuyen-muc/tieu-diem', 'https://nguoixaydung.com.vn/chuyen-muc/xay-dung',
                  'https://nguoixaydung.com.vn/chuyen-muc/do-thi',
                  'https://nguoixaydung.com.vn/chuyen-muc/pha-luat-ve-xay-dung',
                  'https://nguoixaydung.com.vn/chuyen-muc/thi-truong-bds',
                  'https://nguoixaydung.com.vn/chuyen-muc/thuong-hieu',
                  'https://nguoixaydung.com.vn/chuyen-muc/khoa-hoc-cong-nghe',
                  'https://nguoixaydung.com.vn/chuyen-muc/thu-toa-soan', 'https://nguoixaydung.com.vn/chuyen-muc/anh',
                  'https://nguoixaydung.com.vn/chuyen-muc/tap-chi-in']

    def parse(self, response):
        current_page = response.xpath('//a[@class="btn-page type_page active"]').get()

        if not current_page:
            self.handle_top_news(response)
        else:
            if response.xpath('//a[@class="btn-page type_page active"]/text()').get().strip() == '1':
                self.handle_top_news(response)

        posts = response.xpath('//div[@id="blockthree"]//h3/a').css('::attr(href)')

        print(response.url)

        if posts:
            for post in posts:
                url_extract = urllib.parse.urljoin(self.base_url, post.extract())
                yield Request(url_extract, callback=self.parse_post)

        next_page = response.xpath('//a[@class="btn-page next-page"]')

        if next_page and posts:
            next_url = response.xpath('//a[@class="btn-page next-page"]').css('::attr(href)').get()
            yield Request(next_url)

    def parse_post(self, response):
        author = self.parse_author(response)
        time_format, short_date = self.parse_date(response)
        item = NewsItem(
            title=response.xpath('//h1/text()').get(),
            timestamp=time_format,
            content_html=response.xpath('//*[@class="fck_detail"]').get(),
            body=html2text.html2text(response.xpath('//*[@class="fck_detail"]"]').get()),
            link=response.url,
            subhead=response.xpath('//p[@class="description"]/strong/text()').get(),
            pic=self.parse_pictures(response),
            date=short_date,
            author=author
        )
        yield item

    def parse_date(self, response):
        # 17:48 | 01/11/2020
        created_raw = response.xpath('//span[@class="format_date"]/text()').get().strip()
        hour_format = created_raw.split('|')[0].strip()
        hour = hour_format.split(':')[0]
        minute = hour_format.split(':')[1]

        date_format = created_raw.split('|')[1].strip()
        dd = date_format.split('/')[0]
        mm = date_format.split('/')[1]
        yyyy = date_format.split('/')[2]

        publish_date = datetime(year=yyyy, minute=minute, hour=hour, day=dd, month=mm)
        return publish_date.isoformat(), '{}/{}/{}'.format(mm, dd, yyyy)

    @staticmethod
    def parse_pictures(response):
        urls = response.xpath('//*[@class="fck_detail"]//img/@src').extract()
        captions = response.xpath('//*[@class="fck_detail"]//table/tbody/tr[2]/td/text()').extract()
        res = [i + '|' + j for i, j in zip(urls, captions)]
        if urls:
            result = '&&'.join(res)
            return result
        else:
            return ''

    @staticmethod
    def parse_author(response):
        return response.xpath('//p[@class="author_mail"]/strong/text()').get()

    def handle_top_news(self, response):
        top_news = response.xpath('//*[@id="blockone"]//h3/a').css('::attr(href)').get()
        url_extract = urllib.parse.urljoin(self.base_url, top_news)
        yield Request(url_extract, callback=self.parse_post)

        follow_news = response.xpath('//*[@class="list-sub-feature"]//h3/a').css('::attr(href)')
        if follow_news:
            for new in follow_news:
                url_extract = urllib.parse.urljoin(self.base_url, new.extract())
                yield Request(url_extract, callback=self.parse_post)
