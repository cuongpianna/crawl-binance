import re
import urllib.parse
from scrapy import Spider, Request
from datetime import datetime
from html2text import html2text
from dateutil import parser

categories = [
    '/tin-tuc/thoi-su',
    '/tin-tuc/chuyen-nguoi-linh',
    '/tin-tuc/kinh-doanh',
    '/tin-tuc/bat-dong-san',
    '/tin-tuc/phap-luat',
    '/tin-tuc/giao-duc',
    '/tin-tuc/doi-song',
    '/tin-tuc/e-magagine'
]


class HoanhapSpider(Spider):
    name = 'VocationalGuidanceAndIntegrationReview'
    allowed_domains = ['hoanhap.vn']
    start_urls = ['http://hoanhap.vn/']
    url_template = 'https://hoanhap.vn/{category}?page={page}'
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    def start_requests(self):
        for category in categories:
            url = self.url_template.format(category=category, page=1)
            yield Request(url, self.parse_first_page)

    def parse_first_page(self, response):
        pages = response.xpath("//li[@class='page-item']/a[@class='page-link']/text()").extract()
        max_page = max(map(lambda page: int(page) if page.isdigit() else -1, pages))
        top_post = response.xpath(
            "//figure[@class='item v1']/div[@class='inner']/div[@class='info']/h3[@class='title']/a/@href").get()
        right_post = response.xpath(
            "//div[@class='col-12 col-lg-3']/figure[@class='item v2']/div[@class='inner']/div[@class='info']/h3[@class='title']/a/@href").extract()
        posts = response.xpath(
            "//div[@class='c-group-item']/figure[@class='item']/div[@class='inner']/div[@class='info']/h3[@class='title']/a/@href").extract()
        posts += right_post
        if top_post is not None:
            posts.append(top_post)
        # yield from response.follow_all(urls=posts, callback=self.parse_post)
        for post in posts:
            yield Request(url=post, callback=self.parse_post)
        for page in range(2, max_page + 1):
            path = urllib.parse.urlparse(response.url).path
            url = self.url_template.format(category=path, page=page)
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        top_post = response.xpath(
            "//figure[@class='item v1']/div[@class='inner']/div[@class='info']/h3[@class='title']/a/@href").get()
        right_post = response.xpath(
            "//div[@class='col-12 col-lg-3']/figure[@class='item v2']/div[@class='inner']/div[@class='info']/h3[@class='title']/a/@href").extract()
        posts = response.xpath(
            "//div[@class='c-group-item']/figure[@class='item']/div[@class='inner']/div[@class='info']/h3[@class='title']/a/@href").extract()
        posts += right_post
        if top_post is not None:
            posts.append(top_post)
        for post in posts:
            yield Request(url=post, callback=self.parse_post)

    def parse_post(self, response):
        timestamp = response.xpath(
            "//div[@class='col-12 col-lg-9']/section[@class='c-detail']/div[@class='detail-header']/div[@class='date']/span/text()").get()
        datetime_parse = datetime.strptime(timestamp.strip(), '%Y-%m-%d %H:%M:%S')
        date = datetime_parse.strftime('%d/%m/%y')
        title = response.xpath("//div[@class='detail-header']/h1[@class='title']/text()").get()
        subhead = response.xpath("//div[@class='hot-news']/b/text()").get()
        body_html = response.xpath("//div[@class='detail-main']").get()
        author = response.xpath("//section[@class='c-detail']/div[@class='detail-copyright']/text()").get()
        return {
            'date': date,
            'title': title.strip(),
            'subhead': subhead.strip(),
            'body': html2text(body_html),
            'author': author.strip(),
            'original_link': response.url,
            'print': '',
            'source': '',
            'pic_list': self.parse_pic(response),
            'site': '127_HuongNghiepvaHoanhap'
        }

    @staticmethod
    def parse_pic(response):
        pics = []
        img_elements = []
        cap_elements = []

        if len(response.xpath("//span/span/img")) > 0:
            img_elements = response.xpath("//span/span/img")
            cap_elements = response.xpath("//span[contains(@style,'color:#3498db')]")
            if len(cap_elements) == 0:
                cap_elements = response.xpath("//span[contains(@style,'color:#27ae60')]")
            is_parse_cap = len(img_elements) == len(cap_elements)

            for index, img_element in enumerate(img_elements):
                src = img_element.xpath('@src').get()
                cap = ""
                if is_parse_cap:
                    cap_html = cap_elements[index].get()
                    cap = re.sub(r'(?i)<\\/[^>]*>|<[^>]*>', '', cap_html) or ""
                if index % 2 == 0:
                    pics.append(f"{src}|{cap}")
                else:
                    pics.append(f"{src}_{cap}")
        elif len("//td/img") > 0:
            img_elements = response.xpath("//td/img")
            for index, img_element in enumerate(img_elements):
                src = img_element.xpath('@src').get()
                cap = img_element.xpath("../../../tr[last()]/td/text()").get() or ""
                if index % 2 == 0:
                    pics.append(f"{src.strip()}|{cap.strip()}")
                else:
                    pics.append(f"{src.strip()}_{cap.strip()}")

        return "&&".join(pics)
