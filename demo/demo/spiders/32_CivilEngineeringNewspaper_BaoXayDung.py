import scrapy
import urllib.parse
from datetime import datetime
from scrapy import Request
from dateutil import parser
import html2text

from demo.items import NewsItem

categories = {
    'su_kien_binh_luan': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyMjE2KQ',
    'thoi_su': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTI4KQ',
    'quy_hoach_kien_truc': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNDY1KQ',
    'bat_dong_san': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTE4KQ',
    'vat_lieu': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNDYxKQ',
    'khoa_hoc_cong_nghe': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNDk4KQ',
    'kinh_te': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTIxKQ',
    'xa_hoi': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTM2KQ',
    'phap_luat': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTI5KQ',
    'ban_doc': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTMwKQ',
    'the_gioi': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTM1KQ',
    'van_hoa': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNDkzKQ',
    'giai_tri': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTI3KQ',
    'du_lich': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNDI0KQ',
    'suc_khoe': 'IEFORCBhLmlkIE5PVCBJTiAoMjkyNTQwKQ'
}


class CivilEngineeringNewspaperSpider(scrapy.Spider):
    name = 'CivilEngineeringNewspaper'
    site_name = 'baoxaydung.com.vn'
    allowed_domains = ['baoxaydung.com.vn']

    base_url = 'https://baoxaydung.com.vn/apicenter@/article_lm&sid=1469&cond={0}==&cond_2=IEpPSU4gdGJsX2FydGljbGVfY2F0ZWdvcmllcyBhYyBPTiAoYS5pZD1hYy5hcnRpY2xlX2lkKSA=&cond_3=IEFORCBtZW51X2lkID0gNDU=&cond_4=IE9SREVSIEJZIGEuYXJ0aWNsZV9wdWJsaXNoX2RhdGUgREVTQw==&BRSR={1}&lim=30&tf=dHBsX2Rlc2t0b3AvbGlzdC5odG1s'

    urls = [
        'https://baoxaydung.com.vn/suc-khoe', 'https://baoxaydung.com.vn/su-kien-binh-luan',
        'https://baoxaydung.com.vn/thoi-su', 'https://baoxaydung.com.vn/quy-hoach-kien-truc',
        'https://baoxaydung.com.vn/bat-dong-san', 'https://baoxaydung.com.vn/vat-lieu',
        'https://baoxaydung.com.vn/kinh-te', 'https://baoxaydung.com.vn/xa-hoi',
        'https://baoxaydung.com.vn/khoa-hoc-cong-nghe', 'https://baoxaydung.com.vn/phap-luat',
        'https://baoxaydung.com.vn/ban-doc', 'https://baoxaydung.com.vn/the-gioi', 'https://baoxaydung.com.vn/van-hoa',
        'https://baoxaydung.com.vn/giai-tri', 'https://baoxaydung.com.vn/du-lich'
    ]

    def __init__(self, page=1, *args, **kwargs):
        super(CivilEngineeringNewspaperSpider, self).__init__(*args, **kwargs)
        self.page = int(page)

    def start_requests(self):
        for url in self.urls:
            yield Request(url, callback=self.parse)

        urls = []
        for cate in categories.values():
            for i in range(0, self.page + 1):
                url = self.base_url.format(cate, i * 30)
                urls.append(url)

    def parse(self, response):
        if response.url == 'https://baoxaydung.com.vn/thoi-su':
            top_news = response.xpath('//div[@class="first-item mb10 clearfix"]//li/a/@href').get()
            yield Request(top_news, callback=self.parse_post)

            posts = response.xpath(
                '//ul[@class="list-news layout-gocnhin list-vt img-float img-left bordered-top __MB_LIST_ITEM"]/li//div[@class="box-title"]/a').css(
                '::attr(href)')
            if posts:
                for post in posts:
                    url = post.extract()
                    yield Request(url, callback=self.parse_post)
        else:
            top_news = response.xpath('//div[@id="list1"]//li/a/@href').get()
            yield Request(top_news, callback=self.parse_post)

            posts = response.xpath(
                '//div[@class="section-content category clearfix"]/div[@class="left w470"]//li/div[@class="box-title"]/a').css(
                '::attr(href)')
            if posts:
                for post in posts:
                    url = post.extract()
                    yield Request(url, callback=self.parse_post)

    def parse_post(self, response):
        author = self.parse_author(response)
        time_format, short_date = self.parse_date(response)
        item = NewsItem(
            title=response.xpath('//h1/text()').get(),
            timestamp=time_format,
            content_html=response.xpath(
                '//div[@class="category article-content __MASTERCMS_CONTENT __MB_CONTENT_FOR_PRINTER"]').get(),
            body=html2text.html2text(response.xpath(
                '//div[@class="category article-content __MASTERCMS_CONTENT __MB_CONTENT_FOR_PRINTER"]').get()),
            link=response.url,
            subhead=response.xpath('//div[@class="category article-content __MASTERCMS_CONTENT __MB_CONTENT_FOR_PRINTER"]//p[1]/strong[1]/text()').get(),
            pic=self.parse_pictures(response),
            date=short_date,
            author=author
        )
        yield item

    def parse_date(self, response):
        # 17:48 | 01/11/2020
        string_time = response.xpath('//span[@class="format_time"]/text()').get()
        string_date = response.xpath('//span[@class="format_date"]/text()').get()
        raw_time = string_time + ' ' + string_date
        converted_time = parser.parse(raw_time)
        publish_date = datetime(year=converted_time.year, minute=converted_time.minute, hour=converted_time.hour,
                                day=converted_time.day,
                                month=converted_time.month)
        return publish_date.isoformat(), '{}/{}/{}'.format(converted_time.month, converted_time.day,
                                                           converted_time.year)

    @staticmethod
    def parse_pictures(response):
        urls = response.xpath(
            '//div[@class="category article-content __MASTERCMS_CONTENT __MB_CONTENT_FOR_PRINTER"]//img/@src').extract()
        captions = response.xpath(
            '//div[@class="category article-content __MASTERCMS_CONTENT __MB_CONTENT_FOR_PRINTER"]//img/@title').extract()
        res = [i + '|' + j for i, j in zip(urls, captions)]
        if urls:
            result = '&&'.join(res)
            return result
        else:
            return ''

    @staticmethod
    def parse_author(response):
        if response.xpath('//i[@id="theo"]/i/text()'):
            return response.xpath('//i[@id="theo"]/i/text()').get()
        elif response.xpath('//div[@class="category article-content __MASTERCMS_CONTENT __MB_CONTENT_FOR_PRINTER"]/p[@align="right"]/strong/text()'):
            return response.xpath('//div[@class="category article-content __MASTERCMS_CONTENT __MB_CONTENT_FOR_PRINTER"]/p[@align="right"]/strong/text()').get()
        elif response.xpath('//div[@class="category article-content __MASTERCMS_CONTENT __MB_CONTENT_FOR_PRINTER"]//p[@style="text-align: right;"]/strong/text()'):
            return response.xpath('//div[@class="category article-content __MASTERCMS_CONTENT __MB_CONTENT_FOR_PRINTER"]//p[@style="text-align: right;"]/strong/text()').get()
        else:
            return ''

    def handle_top_news(self, response):
        top_news = response.xpath('//*[@id="blockone"]//h3/a').css('::attr(href)').get()
        url_extract = urllib.parse.urljoin(self.base_url, top_news)
        yield Request(url_extract, callback=self.parse_post)

        follow_news = response.xpath('//*[@class="list-sub-feature"]//h3/a').css('::attr(href)')
        if follow_news:
            for new in follow_news:
                url_extract = urllib.parse.urljoin(self.base_url, new.extract())
                yield Request(url_extract, callback=self.parse_post)
