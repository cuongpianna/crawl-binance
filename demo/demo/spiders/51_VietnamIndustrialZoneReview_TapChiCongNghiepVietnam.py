from scrapy import Spider, Request
from html2text import html2text
from datetime import datetime
import re

categories = {
    'tin-tuc': '/1/',
    'vrdf-2020': '/37/',
    'nguyen-cuu-trao-doi': '/13/',
    'hop-tac-quoc-te': '/5/',
    'hoi-thao-khoa-hoc': '/3/',
    'dao-tao': '/4/',
    'de-tai-de-an': '/2/',
    'tu-van': '/16/',
    'sach-thu-vien': '/35/',
    'an-phan': '/6/',
    'gioi-thieu-vien': '/7/',
}


class VidsSpider(Spider):
    name = 'VietnamIndustrialZoneReview'
    allowed_domains = ['vids.mpi.gov.vn']
    start_urls = ['http://vids.mpi.gov.vn/']

    base_url = 'http://vids.mpi.gov.vn/'
    url_templates = 'http://vids.mpi.gov.vn{path}'

    def __init__(self, page=1, *args, **kwargs):
        super(VidsSpider, self).__init__(*args, **kwargs)
        self.page = int(page)

    def start_requests(self):
        urls = []

        for category in categories.values():
            url = self.url_templates.format(path=category)
            urls.append(url)
        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        urls = response.xpath("/html/body/table[@id='Table_04']/tr/td/table[2]/tr/td[1]/div/a/@href").extract()
        full_urls = [self.url_templates.format(path=url) for url in urls]
        yield from response.follow_all(full_urls, self.parse_post)

        next_url = response.xpath('//div[@align="center"]/a[@class="link-othernews"]/@href').get()
        if next_url is not None:
            yield Request(self.url_templates.format(path=next_url), self.parse)

    def parse_post(self, response):
        content_html = response.xpath('//div[@class="Normal"]').get()
        yield {
            'date': self.parse_timestamp(response, 'date'),
            'timestamp': self.parse_timestamp(response, 'iso'),
            'title': response.xpath('//div[@id="tTitle"]/span/text()').get(),
            'subhead': response.xpath("//tbody/tr/td/table/tbody/tr/td/div[@class='Lead']/div/span/text()").get(),
            'link': response.url,
            'pic': self.parse_pic(response),
            'body': html2text(content_html),
            'content_html': content_html,
            'author': self.parse_author(response),
            'site': '51_tap_chi_cong_nghiep_viet_nam',
            'source': '',
            'print': ''
        }

    @staticmethod
    def parse_pic(response):
        pic = ''
        img_elements = response.xpath('//div[@align="center"]/img')
        images = []
        captions = []

        for img_element in img_elements:
            src = img_element.xpath("@src").get()
            caption = img_element.xpath("@alt").get()
            pic += f'&&{src}_{caption}'
            images.append(src)
            captions.append(caption)
        result = [i + '|' + j for i, j in zip(images, captions)]
        pic = '&&'.join(result)
        return pic

    @staticmethod
    def parse_timestamp(response, type_parse):
        str_timestamp = response.css(".item-date::text").get().strip().split(',')[1]
        str_timestamp = re.findall(r'[\d\/\:]+', str_timestamp)
        str_timestamp = ' '.join(str_timestamp)
        timestamp = datetime.strptime(str_timestamp, '%d/%m/%Y %H:%M:%S')
        if type_parse is 'iso':
            return timestamp.isoformat()
        else:
            return timestamp.strftime('%d/%m/%Y')

    def parse_author(self, response):
        if response.xpath('//div[@class="Normal"]/p[@align="right"][last()]').get():
            return html2text(response.xpath('//div[@class="Normal"]/p/b/span/text()').get())
        return ''
