from scrapy import Spider, Request
import urllib.parse
from html2text import html2text
from datetime import datetime

categories = {
    'thoi-su': 'thoi-su/?trang=1',
    'dau-thau': 'dau-thau/?trang=1',
    'dau-gia': 'dau-gia/?trang=1',
    'kinh-doanh': 'kinh-doanh/?trang=1',
    'doanh-nghiep': 'doanh-nghiep/?trang=1',
    'tai-chinh': 'tai-chinh/?trang=1',
    'dau-tu': 'dau-tu/?trang=1',
    'bat-dong-san': 'bat-dong-san/?trang=1',
    'quoc-te': 'quoc-te/?trang=1',
}


class BiddingReviewSpider(Spider):
    name = 'BiddingReview'
    allowed_domains = ['baodauthau.vn']
    start_urls = ['http://baodauthau.vn/']

    base_url = 'https://baodauthau.vn/'
    url_templates = 'https://baodauthau.vn/{category}'

    def __init__(self, page=1, *args, **kwargs):
        super(BiddingReviewSpider, self).__init__(*args, **kwargs)
        self.page = int(page)

    def start_requests(self):
        urls = []

        for category in categories.values():
            url = self.url_templates.format(category=category)
            urls.append(url)
        for url in urls:
            yield Request(url=url, callback=self.load_page_category)

    def load_page_category(self, response):
        top_page = response.xpath('//a[@class="title is-font-18 margin-b--5 cms-link"]/@href').extract()
        pages = response.xpath('//a[@class="title cms-link"]/@href').extract()
        urls = top_page + pages

        yield from response.follow_all(urls, self.parse_post)
        next_url = response.css('ul.pagination-list a[title="Trang sau"]::attr(href)').get()

        if next_url is not None:
            yield Request(next_url, self.parse)

    def parse(self, response):
        urls = response.xpath('//div[@class="media"]/div[@class="media-content"]/a/@href').extract()
        yield from response.follow_all(urls, self.parse_post)

        next_url = response.css('ul.pagination-list a[title="Trang sau"]::attr(href)').get()
        if next_url is not None:
            yield Request(next_url, self.parse)

    def parse_post(self, response):
        content_html = response.xpath('//main[@class="body cms-body column main-content"]').get()
        yield {
            'date': self.parse_timestamp(response, 'date'),
            'timestamp': self.parse_timestamp(response, 'iso'),
            'title': response.xpath('//h1[@class="title cms-title"]/text()').get(),
            'subhead': '',
            'link': response.url,
            'pic': self.parse_pic(response),
            'body': html2text(response.xpath('//main[@class="body cms-body column main-content"]').get()),
            'content_html': content_html,
            'author': self.parse_author(response),
            'site': '49_dau_thau',
            'source': '',
            'print': ''
        }

    @staticmethod
    def parse_pic(response):
        pic = ''
        img_elements = response.xpath('//table[@class="picture"]')

        images = []
        captions = []

        for img_element in img_elements:
            caption = img_element.xpath("tbody/tr/td[@class='caption']/p/text()").get()
            src = img_element.xpath("tbody/tr/td/img[@class='cms-photo']/@src").get()
            images.append(src)
            captions.append(caption)
        result = [i + '|' + j for i, j in zip(images, captions)]
        pic = '&&'.join(result)
        return pic

    @staticmethod
    def parse_timestamp(response, type_date):
        str_timestamp = response.xpath('//li[@class="publish-date cms-date"]/text()').get()
        timestamp = datetime.strptime(str_timestamp.strip(), '%d/%m/%Y %H:%M')
        if type_date is 'iso':
            return timestamp.isoformat()
        else:
            return timestamp.strftime('%d/%m/%Y')

    def parse_author(self, response):
        if response.xpath('//li[@class="author"]/b[@class="cms-author"]/text()').get():
            return response.xpath('//li[@class="author"]/b[@class="cms-author"]/text()').get()
        elif response.xpath('//div[@class="cms-source"]/text()'):
            return response.xpath('//div[@class="cms-source"]/text()').get()

        return ''
