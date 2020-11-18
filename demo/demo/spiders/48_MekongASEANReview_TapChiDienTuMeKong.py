from scrapy import Spider, Request
import urllib.parse
from datetime import datetime
from html2text import html2text
from dateutil import parser

categories = {
    'kinh-te-mekong-asean': 'kinh-te-mekong-asean',
    'dien-dan-dau-tu': 'dien-dan-dau-tu',
    'thuong-truong-asean': 'thuong-truong-asean',
    'hoi-nhap-quoc-te': 'the-gioi/hoi-nhap-quoc-te',
    'dau-tu-nuoc-ngoai': 'the-gioi/dau-tu-nuoc-ngoai',
    'mekong-asean-dong-chay': 'mekong-asean-dong-chay',
    'sac-mau-mekong-asean': 'sac-mau-mekong-asean',
}


class MekongseanSpider(Spider):
    name = 'MekongASEANReview'
    site_name = 'mekongsean.vn'
    allowed_domains = ['mekongsean.vn']
    start_urls = ['http://mekongsean.vn']

    base_url = 'https://mekongsean.vn/'
    url_templates = 'https://mekongsean.vn/{category}?dps_paged={page}'

    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
    }

    def __init__(self, page=1, *args, **kwargs):
        super(MekongseanSpider, self).__init__(*args, **kwargs)
        self.page = int(page)

    def start_requests(self):
        urls = []

        for category in categories.values():
            for i in range(1, self.page + 1):
                url = self.url_templates.format(page=i, category=category)
                urls.append(url)
        for url in urls:
            yield Request(url=url, callback=self.parse_category)

    def parse_category(self, response):
        pages = response.xpath("//nav[@class='display-posts-pagination']/div[@class='nav-links']\
            /a[not(contains(@class, 'next'))]/text()").extract()
        max_page = max([int(i) for i in pages])
        temp_url = response.url[:-1]
        for page in range(1, max_page + 1):
            url = temp_url + str(page)
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        posts = response.xpath('//h3[@class="entry-title td-module-title"]/a/@href')

        for post in posts:
            url_extract = post.extract()
            url = urllib.parse.urljoin(self.base_url, url_extract)
            yield Request(url=url, callback=self.parse_post)

    def parse_post(self, response):
        content_html = response.xpath('//div[@class="td-post-content"]').get()
        timestamp = response.xpath('//time[@class="entry-date updated td-module-date"]/@datetime').get()
        yield {
            'date': self.parse_timestamp(timestamp, 'date'),
            'timestamp': self.parse_timestamp(timestamp, 'iso'),
            'title': response.xpath('//h1[@class="entry-title"]/text()').get(),
            'subhead': response.xpath('//p[@class="td-post-sub-title"]/text()').get(),
            'link': response.url,
            'pic': self.parse_pic(response),
            'body': html2text(content_html),
            'content_html': content_html,
            'author': response.xpath('//div[@class="td-post-small-box"]/a/text()').get(),
            'site': '48_tap_chi_dien_tu_me_kong',
            'source': '',
            'print': ''
        }

    @staticmethod
    def parse_pic(response):
        pic = ''
        img_elements = response.css('[class*="wp-image-"]')
        images = []
        captions = []
        for img_element in img_elements:
            src = img_element.xpath('@src').get()
            figure_parent = img_element.xpath("ancestor::figure")
            if figure_parent.get() is None:
                caption = figure_parent.xpath('figcaption/text()').get()
                pic += f'&&{src}_{caption}'
                images.append(src)
                captions.append(caption)
            else:
                pic += f'&&{src}_'
                images.append(src)
                captions.append(' ')
        result = [i + '|' + j for i, j in zip(images, captions)]
        pic = '&&'.join(result)
        return pic

    @staticmethod
    def parse_timestamp(timestamp, type_parse):
        if timestamp is None:
            return ''
        else:
            datetime_parse = parser.isoparse(timestamp)
            if type_parse is 'iso':
                return datetime_parse.isoformat()
            else:
                return datetime_parse.strftime('%d/%m/%Y')
