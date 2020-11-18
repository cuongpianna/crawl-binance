from scrapy import Spider, Request
from html2text import html2text
from datetime import datetime
import pytz
import urllib.parse

categories = {
    'thoi-su': '2-thoi-su/10',
    'chinh-sach': '90-chinh-sach/10',
    'nhan-dinh': '91-nhan-dinh/10',
    'dau-tu': '90-dau-tu/10',
    'tai-chinh': '101-tai-chinh/10',
    'thi-truong': '100-thi-truong/10',
    'doanh-nghiep': '146-doanh-nghiep/10',
    'nganh-lanh-tho': '174-nganh-lanh-tho/10',
    'the-gioi': '197-the-gioi/10',
    'cong-bo-khoa-hoc': '230-cong-bo-khoa-hoc/10'
}


class EconomyAndForecastReviewSpider(Spider):
    name = 'EconomyAndForecastReview'
    allowed_domains = ['kinhtevadubao.vn']
    start_urls = ['http://kinhtevadubao.vn/']
    base_url = 'http://kinhtevadubao.vn/'
    url_templates = 'http://kinhtevadubao.vn/danh-sach/{category}/{page}.html'

    def __init__(self, page=1, *args, **kwargs):
        super(EconomyAndForecastReviewSpider, self).__init__(*args, **kwargs)
        self.page = int(page)

    def start_requests(self):
        urls = []

        for category in categories.values():
            url = self.url_templates.format(page=0, category=category)
            urls.append(url)
        for url in urls:
            yield Request(url=url, callback=self.parse_category)

    def parse_category(self, response):
        end_page = 1
        str_page_end = response.css('.pageNum a[title="End"]::text').get()
        if str_page_end is not None:
            end_page = int(str_page_end.strip())
        temp_url = response.url[:-6]
        for page in range(0, end_page):
            url = temp_url + str(page * 10) + '.html'
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        posts = response.xpath('//div[@class="news"]/div[@class="page_mid_title"]/a/@href')

        for post in posts:
            url_extract = post.extract()
            url = urllib.parse.urljoin(self.base_url, url_extract)
            yield Request(url, callback=self.parse_post)

    def parse_post(self, response):
        content_html = response.xpath('//div[@class="page_town_row"][4]').get()
        yield {
            'date': self.parse_timestamp(response, 'date'),
            'timestamp': self.parse_timestamp(response, 'iso'),
            'title': response.xpath('//div[@class="page_town_row"]/h2/text()').get(),
            'subhead': response.xpath('//div[@class="page_town_row2"]/p/text()').get(),
            'link': response.url,
            'pic': self.parse_pic(response),
            'body': html2text(content_html),
            'content_html': content_html,
            'author': self.parse_author(response),
            'site': '50_tap_chi_kinh_te_va_du_bao',
            'source': '',
            'print': ''
        }

    @staticmethod
    def parse_pic(response):
        pic = ''
        img_elements = response.xpath('//p[@class="MsoNormal"]/img')

        images = []
        captions = []

        for img_element in img_elements:
            src = img_element.xpath('@src').get()
            em_closest = img_element.xpath('../following-sibling::p/em/text()').get()
            if em_closest is None:
                pic += f'&&{src}_{em_closest}'
                images.append(src)
                captions.append(em_closest)
            else:
                pic += f'&&{src}_'
                images.append(src)
                captions.append('')
        if images:
            result = [i + '|' + j for i, j in zip(images, captions)]
            pic = '&&'.join(result)
            return pic
        return ''

    @staticmethod
    def parse_author(response):
        return response.xpath('//div[@class="left_news"]/div[@class="page_town_row"][last()]/text()').get() or \
               response.xpath('//div[@class="left_news"]/div[@class="page_town_row"]/p/strong/em/text()').get() or \
               response.xpath('//div[@class="left_news"]/div[last()]/p[last()]/text()').get() or html2text(response.xpath(
            '//div[@class="left_news"]//p[@class="post-source"]').get())

    @staticmethod
    def parse_timestamp(response, type_parse):
        try:
            raw_datetime = response.xpath('//div[@class="page_town_row"]/p/text()').get()
            timestamp = datetime.strptime(raw_datetime, 'Cập nhật ngày %d/%m/%Y - %H:%M:%S')
            timestamp.replace(tzinfo=pytz.timezone('Asia/Saigon'))
            if type_parse is 'iso':
                return timestamp.isoformat()
            else:
                return timestamp.strftime('%d/%y/%Y')
        except:
            return ''
