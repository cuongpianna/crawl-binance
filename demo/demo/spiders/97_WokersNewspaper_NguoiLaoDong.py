from scrapy import Spider, Request
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from html2text import html2text
from sqlalchemy.orm import sessionmaker
from dateutil import parser
from demo.items import NewsItem
from demo.models import db_connect, create_table, Article


categories = {
    'trong_nuoc': 1002,
    'quoc_te': 1006,
    'cong_doan': 1010,
    'ban_doc': 1042,
    'giao_duc': 1017,
    'van_nghe': 1020,
    'giai_tri': 1588,
    'the_thao': 1026,
    'cong_nghe': 1317,
    'diem_den': 1580
}


class WorkersNewspaperSpider(Spider):
    name = 'WorkersNewspaper'
    allowed_domains = ['nld.com.vn']

    base_url = 'https://nld.com.vn/'
    api_template = 'https://nld.com.vn/loadmorecategory-{cate_id}-{page}.htm'

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',

    }

    def __init__(self, max_page=1000, page=500, *args, **kwargs):
        """
        :param max_page: Max page to crawl
        """
        super(WorkersNewspaperSpider, self).__init__(*args, **kwargs)
        self.max_page = int(max_page)
        self.page = int(page)

    def start_requests(self):
        urls = []
        for cate in categories.values():
            for i in range(1, self.page + 1):
                url = self.api_template.format(page=i, cate_id=cate)
                urls.append(url)
                rq = requests.get(url).text
                soup = BeautifulSoup(rq, 'lxml')

                for link in soup.find_all('a', href=True):
                    url_item = urljoin(self.base_url, link['href'])
                    if self.check_exist_article(url_item):
                        break

        for url in urls:
            yield Request(url, callback=self.parse)

    def parse(self, response):
        """
        Get all article urls and yield it to parse_post function
        :param response:
        :return:
        """

        posts = response.xpath('//li/a/@href')
        for post in posts:
            link = urljoin(self.base_url, post.extract())
            yield Request(link, callback=self.parse_post)

    def parse_post(self, response):
        """ This function returns newspaper articles on a given date in a given structure.

            Return data structure:
            [
                {
                    'title': string,                        # The title of a article
                    'author'                                # The author of a article, of '' if none
                    'subhead': string,                      # The subtitle of a article, or '' if there is no subtitle
                    'date': string in '%Y-%m-%d' format,    # The publish date of a article
                    'body': string                          # The body of a article
                    'pic_list': string in                    # The link of pictures of a article, or '' if there are no pictures
                                                                f"{link1}|{text2}&&..." format
                    'original_link': string                   # The url of a article
                    'source': string
                    'print': string
                },
                        ...
            ]
            or
            None

            :param response: The scrapy response
            :return:
            """

        content_html = response.xpath('//*[@id="content-id"]').get()
        item = NewsItem(
            title=response.xpath('//h1[@class="title-content"]/text()').get().strip(),
            body=html2text(content_html),
            original_link=response.url,
            subhead=html2text(response.xpath('//*[@class="sapo-detail"]').get()),
            pic_list=self.parse_pic(response),
            date=self.parse_timestamp(response, 'date'),
            author=self.parse_author(response),
            site='97_nguoi_lao_dong',
            source='',
            print=''
        )
        yield item

    @staticmethod
    def parse_pic(response):
        """
        Get pictures list from response. Format: link|title&&link|title
        Or
        return ' '
        :param response:
        :return: list pictures
        """

        image_list = response.xpath('//*[@id="content-id"]//img/@src').extract()
        captions_list = response.xpath('//*[@id="content-id"]//img/@alt').extract()

        res = [i + '|' + j for i, j in zip(image_list, captions_list)]

        if res:
            result = '&&'.join(res)
            return result
        else:
            return ''

    @staticmethod
    def parse_timestamp(response, type_parse):
        """
        Convert publish date string format to datetime format
        :param response:
        :param type_parse: date or iso
        :return: Timestamp or date
        """
        str_timestamp = response.xpath('//*[@data-field="createddate"]/text()').get()
        timestamp = parser.parse(str_timestamp)
        if type_parse is 'iso':
            return timestamp.isoformat()
        else:
            return timestamp.strftime('%d/%m/%Y')

    def parse_author(self, response):
        """
        Get author from response
        :param response:
        :return: the author of article or '' if None
        """
        if response.xpath('//*[@data-field="author"]').get():
            return html2text(response.xpath('//*[@data-field="author"]').get())
        return ''

    def check_exist_article(self, url):
        engine = db_connect()
        create_table(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        exist_article = session.query(Article).filter_by(original_link=url).first()
        return exist_article
