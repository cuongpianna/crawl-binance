import scrapy
import urllib.parse
import re
from datetime import datetime
from scrapy import Spider, Request
import html2text

from demo.items import NewsItem


categories = {
    'the-gioi': '2',
    'thoi-su': '3',
    'kinh-doanh': '11',
    'van-hoa': '200017',
    'giao-duc': '3',
    'xe': '659',
    'nhip-so-tre': '7',
    'gia-tri': '10',
    'khoa-hoc': '661',
    'suc-khoe': '12'
}


class TuoitreSpider(scrapy.Spider):
    name = 'tuoitre'
    site_name = 'tuoitre.vn'
    allowed_domains = ['tuoitre.vn']
    start_urls = ['https://tuoitre.vn/']

    base_url = 'https://tuoitre.vn/'
    url_templates = 'https://tuoitre.vn/timeline/{category_id}/trang-{page}.htm'

    def __init__(self, page=1, *args, **kwargs):
        super(TuoitreSpider, self).__init__(*args, **kwargs)
        self.page = int(page)

    def start_requests(self):
        urls = []

        for cate in categories.values():
            for i in range(1, self.page + 1):
                url = self.url_templates.format(page=i, category_id=cate)
                urls.append(url)
        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        posts = response.xpath('//body/li/div/h3/a').css('::attr(href)')

        for post in posts:
            url_extract = post.extract()
            url = urllib.parse.urljoin(self.base_url, url_extract)
            yield Request(url, callback=self.parse_post)

    def parse_post(self, response):
        tags = response.xpath('//div[@class="tags-container"]/ul/li/a/@title').extract()
        cate = response.xpath('//meta[@property="article:section"]//@content').get()
        author = response.xpath('//div[@class="author"]').css('::text').extract()[1] if response.xpath('//div[@class="author"]').css('::text').extract()[1] else ''
        item = NewsItem(
            title=response.xpath('//h1[@class="article-title"]/text()').get(),
            timestamp=self.parse_timestamp(response),
            content_html=response.xpath('//div[@class="main-content-body"]').get(),
            body=html2text.html2text(response.xpath('//div[@class="main-content-body"]').get()),
            tags=tags,
            category=cate,
            original_link=response.url,
            subhead=response.xpath('//h2[@class="sapo"]/text()').get(),
            pic_list=self.parse_pictures(response),
            date=self.parse_date(response),
            author=author
        )
        yield item

    @staticmethod
    def parse_timestamp(response):
        # 07/10/2020 05:28 GMT+7
        created_raw = response.xpath('//body//div[@class="date-time"]/text()').get()
        created_raw = created_raw.replace("GMT+7", "GMT+0700")
        created_at = datetime.strptime(created_raw.strip(), '%d/%m/%Y %H:%M %Z%z')
        return created_at

    @staticmethod
    def parse_date(response):
        # 07/10/2020
        created_raw = response.xpath('//body//div[@class="date-time"]/text()').get()
        created_raw = created_raw.replace("GMT+7", "GMT+0700")
        created_at = datetime.strptime(created_raw.strip(), '%d/%m/%Y %H:%M %Z%z')
        return created_at.strftime('%m/%d/%Y')

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
