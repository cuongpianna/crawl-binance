import os

import html2text
import requests
from dateutil.parser import parse as date_parse
from scrapy import Spider, Request
from html2text import html2text
from sqlalchemy.orm import sessionmaker
from demo.items import NewsItem
from demo.models import db_connect, create_table, Article


class CommunistReviewSpider(Spider):
    name = 'CommunistReview'
    site_name = 'www.tapchicongsan.org.vn'
    allowed_domains = ['www.tapchicongsan.org.vn']

    base_url = 'https://www.tapchicongsan.org.vn/'

    start_urls = [
        'https://www.tapchicongsan.org.vn/web/guest/chinh-tri-xay-dung-dang',
        'https://www.tapchicongsan.org.vn/web/guest/kinh-te',
        'https://www.tapchicongsan.org.vn/web/guest/van_hoa_xa_hoi',
        'https://www.tapchicongsan.org.vn/web/guest/quoc-phong-an-ninh-oi-ngoai1',
        'https://www.tapchicongsan.org.vn/web/guest/the-gioi-van-de-su-kien',
        'https://www.tapchicongsan.org.vn/web/guest/thuc-tien-kinh-nghiem1',
        'https://www.tapchicongsan.org.vn/web/guest/nghien-cu',
        'https://www.tapchicongsan.org.vn/web/guest/thong-tin-ly-luan'
    ]

    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'SELENIUM_DRIVER_NAME': 'chrome',
        'SELENIUM_DRIVER_EXECUTABLE_PATH': os.path.join(os.path.abspath(os.curdir), 'chromedriver.exe'),
        'SELENIUM_DRIVER_ARGUMENTS': ['headless']

    }

    def parse(self, response):
        """
            Get all article urls and yield it to parse_post function
            :param response:
            :return:
        """
        print(requests.get(response.url).text)
        flag = False
        posts = response.xpath('//h4[@class="titleNews"]/a/@href')
        print(posts)
        for post in posts:
            if self.check_exist_article(post.extract()):
                flag = True
            yield Request(post.extract(), callback=self.parse_post)

        next_page = response.xpath('//a[@aria-label="Next"]/@href').get()
        print('@@@@@')
        print(response.xpath('//*[@class="search-results"]'))
        print(next_page)
        if 'javascript' not in next_page and not flag:
            yield Request(next_page)

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

        item = NewsItem(

            site='104_tapchicongsan',
            title=response.xpath('//h2/a/text()').get().strip(),
            original_link=response.url,
            body=html2text(response.xpath('//*[@class="detailContent"]').get()),
            date=self.parse_timestamp(response),
            subhead=html2text(response.xpath('//*[@class="sumary"]').get()),
            pic_list=self.parse_pic(response),
            author=self.parse_author(response),
            source='',
            print=''
        )
        yield item

    @staticmethod
    def parse_timestamp(response):
        """
                Convert publish date string format to datetime format
                :param response: 22:45, ngày 22-11-2020
                :return: date
        """
        created_raw = response.xpath('//*[@class="publishdate mt15"]/text()').get().split('ngày')[1].strip()
        created_at = date_parse(created_raw)
        return created_at.strftime('%d/%m/%Y')

    def parse_author(self, response):
        """
        Get author from response
        :param response:
        :return: the author of article or '' if None
        """
        if response.xpath('//*[@class="author"]/text()').get():
            return html2text(
                response.xpath('//*[@class="author"]/text()').get())
        return ''

    @staticmethod
    def parse_pic(response):
        """
        Get pictures list from response. Format: link|title&&link|title
        Or
        return ' '
        :param response:
        :return: list pictures
        """

        image_list = response.xpath('//*[@class="detailContent"]/figure/img/@src').extract()
        captions_list = response.xpath('//*[@class="detailContent"]/figure/figcaption/text()').extract()

        res = [i + '|' + j for i, j in zip(image_list, captions_list)]

        if res:
            result = '&&'.join(res)
            return result
        else:
            return ''

    def check_exist_article(self, url):
        engine = db_connect()
        create_table(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        exist_article = session.query(Article).filter_by(original_link=url).first()
        return exist_article
