import re
import urllib.parse
from scrapy import Spider, Request
from datetime import datetime
from html2text import html2text
from dateutil import parser

categories = {
    '/thoi-su/chuyen-hom-nay': '1',
    '/thoi-su/goc-nhin': '2',
    '/thoi-su/phiem-va-bien': '3',
    '/thoi-su/phong-su': '4',
    '/thoi-su/ban-doc': '5',
    '/thoi-su/chinh-sach-moi': '66',
    '/nhip-song-do-thi/giao-thong': '6',
    '/nhip-song-do-thi/the-gioi-hem': '7',
    '/nhip-song-do-thi/dich-vu-do-thi': '8',
    '/nhip-song-do-thi/song-thien-nguyen': '9',
    '/di-san/ky-uc-do-thi': '14',
    '/di-san/dau-an-kien-thuc': '15',
    '/di-san/thu-vien-di-san': '16',
    '/di-san/do-thi-hoc-thuong-thuc': '62',
    '/moi-truong/su-kien': '10',
    '/moi-truong/bien-doi-khi-hau': '11',
    '/moi-truong/tai-nguyen': '12',
    '/moi-truong/ket-noi-thien-nhien': '13',
    '/the-gioi/noi-mang-toan-cau': '17',
    '/the-gioi/bien-dong': '18',
    '/the-gioi/ho-so': '19',
    '/kinh-doanh/thi-truong-doanh-nghiep': '26',
    '/kinh-doanh/bat-dong-san': '27',
    '/kinh-doanh/tai-chinh-dau-tu': '28',
    '/kinh-doanh/doanh-nhan': '29',
    '/kinh-doanh/the-gioi-xe': '30',
    '/kinh-doanh/san-pham-dich-vu-moi': '31',
    '/kinh-doanh/thuc-pham-minh-bach': '63',
    '/van-hoa-giai-tri/nghe-xem': '20',
    '/van-hoa-giai-tri/doi-nghe-si': '21',
    '/van-hoa-giai-tri/van-hoc': '22',
    '/van-hoa-giai-tri/cau-chuyen-van-hoa': '23',
    '/van-hoa-giai-tri/hau-truong-showbiz': '24',
    '/van-hoa-giai-tri/thoi-trang-lam-dep': '25',
    '/loi-song/dung-lai-nguoi': '32',
    '/loi-song/nghi-viet': '33',
    '/loi-song/phong-cach-thi-dan': '34',
    '/giao-duc/chuyen-hoc-hanh': '49',
    '/giao-duc/tro-chuyen-triet-hoc': '50',
    '/giao-duc/du-hoc-hoc-bong': '51',
    '/am-thuc/con-duong-gia-vi': '35',
    '/am-thuc/quan-mon': '36',
    '/am-thuc/dau-bep': '37',
    '/am-thuc/hanh-trinh-thia-vang': '38',
    '/suc-khoe/an-toan-thuc-pham': '42',
    '/suc-khoe/cau-chuyen-bac-si': '43',
    '/suc-khoe/dinh-duong': '44',
    '/suc-khoe/chan-benh': '45',
    '/du-lich/dau-chan-lu-hanh': '39',
    '/du-lich/tour-moi': '40',
    '/du-lich/khach-san-resort': '41',
}


class UrbanPeopleMagazineSpider(Spider):
    name = 'UrbanPeopleMagazine'
    site_name = 'nguoidothi.net.vn'
    allowed_domains = ['nguoidothi.net.vn']
    start_urls = ['https://nguoidothi.net.vn']

    base_url = 'https://nguoidothi.net.vn'
    url_templates = 'https://nguoidothi.net.vn/Zone/_getListNews?ZoneId={category_id}&page={page}&X-Requested-With=XMLHttpRequest'
    url_templates_newest = 'https://nguoidothi.net.vn/Category/_getListNews?catId={category_id}'

    def __init__(self, page=1000, *args, **kwargs):
        super(UrbanPeopleMagazineSpider, self).__init__(*args, **kwargs)
        self.page = int(page)

    def start_requests(self):
        for category_id in categories.values():
            url = self.url_templates_newest.format(category_id=category_id)
            yield Request(url=url, callback=self.parse_first_page)

    def parse_first_page(self, response):
        pages = response.xpath("//div[@class='paging']/ul[@class='pagination']/li/a/text()").extract()
        posts = response.xpath('//div[@class="col-sm-8"]/div[@class="dvTitleCat"]/a/@href').extract()

        urls = [urllib.parse.urljoin(self.base_url, post) for post in posts]
        yield from response.follow_all(urls, callback=self.parse_post)

        max_page = max(map(lambda page: int(page) if page.isdigit() else -1, pages))
        query = urllib.parse.urlparse(response.url).query
        params = urllib.parse.parse_qs(query)
        category_id = params['catId'][0]
        url_pages = []
        for page in range(2, max_page):
            url_pages.append(self.url_templates.format(category_id=category_id, page=page))
        yield from response.follow_all(url_pages, callback=self.parse)

    def parse(self, response):
        posts = response.xpath('//div[@class="col-sm-8"]/div[@class="dvTitleCat"]/a/@href').extract()

        urls = [urllib.parse.urljoin(self.base_url, post) for post in posts]
        yield from response.follow_all(urls, callback=self.parse_post)

    def parse_post(self, response):
        date_element = response.xpath("//div[@class='col-sm-12 articleDetail']/span").get()
        _, _, d, m, y, _ = re.findall("[\d]+", date_element)
        date = f'{d}/{m}/{y}'
        title = response.xpath('//div[@class="row"]/div[@class="col-sm-12 articleDetail"]/h1/text()').get()
        subhead = response.xpath(
            '//div[@class="row"]/div[@class="col-sm-12 articleDetail"]/div[@class="dvTeaser"]/text()').get()
        body_html = response.xpath(
            '//div[@class="col-sm-12 articleDetail"]/div[@id="dvContent"]/p[position()<last()]').extract()
        body_str = "\n".join(body_html)
        author = html2text(
            response.xpath('//div[@class="col-sm-12 articleDetail"]/div[@id="dvContent"]/p[last()]').get())
        yield {
            'date': date,
            'title': title.strip(),
            'subhead': subhead.strip(),
            'body': html2text(body_str),
            'author': author.strip(),
            'original_link': response.url,
            'print': '',
            'source': '',
            'pic_list': self.parse_pic(response),
            'site': '128_nguoidothi'
        }

    @staticmethod
    def parse_pic(response):
        pics = []
        img_elements = response.xpath("//div[@id='dvContent']//p//img/@src")
        for index, img_element in enumerate(img_elements):
            src = img_element.extract()
            cap = response.xpath(
                "(//div[@id='dvContent']//p//img)[{}]/../..//following-sibling::*[1]//em/text()".format(
                    index + 1)).get() or \
                  ""
            if index % 2 == 0:
                pics.append(f"{src}|{cap}")
            else:
                pics.append(f"{src}_{cap}")
        return "&&".join(pics)
