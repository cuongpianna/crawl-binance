from datetime import datetime
import re

import html2text
import requests
from dateutil.parser import parse as date_parse
from scrapy import Spider, Request
from html2text import html2text
from sqlalchemy.orm import sessionmaker
from demo.items import NewsItem
from demo.models import db_connect, create_table, Article

categories = ['thoi-su', 'kinh-doanh', 'giai-tri', 'the-gioi', 'giao-duc', 'doi-song', 'phap-luat', 'the-thao',
              'cong-nghe', 'suc-khoe', 'bat-dong-san', 'ban-doc', 'tuanvietnam', 'oto-xe-may']


class VietnamNetSpider(Spider):
    name = 'VietnamNet'
    site_name = 'vietnamnet.vn'
    allowed_domains = ['vietnamnet.vn']

    base_url = 'https://vietnamnet.vn/'
    url_templates = 'https://vietnamnet.vn/jsx/loadmore/?domain=desktop&c={cate}&p={page}&s=15&a=5'

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
    }

    def __init__(self, page=1500, *args, **kwargs):
        super(VietnamNetSpider, self).__init__(*args, **kwargs)
        self.page = int(page)

    def start_requests(self):
        urls = []

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
        }

        for cate in categories:
            for i in range(1, self.page + 1):
                url = self.url_templates.format(page=i, cate=cate)
                rq = requests.get(url, headers=headers).text
                matchs = re.findall(r'"link": ".*"', rq)
                for link in matchs:
                    link = link.replace('"link": ', '')
                    link = link[1:-1]
                    if self.check_exist_article(link):
                        break
                urls.append(url)
        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        """
            Get all article urls and yield it to parse_post function
            :param response:
            :return:
        """
        rq = requests.get(response.url).text
        matchs = re.findall(r'"link": ".*"', rq)
        for link in matchs:
            link = link.replace('"link": ', '')
            link = link[1:-1]
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

        item = NewsItem(

            site='103_vietnamnet',
            title=response.xpath('//h1[@class="title f-22 c-3e"]/text()').get().strip(),
            original_link=response.url,
            body=html2text(response.xpath('//*[@id="ArticleContent"]').get()),
            date=self.parse_timestamp(response),
            subhead=html2text(response.xpath('//*[@class="bold ArticleLead"]').get()),
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
                :param response: 2020-04-09T10:30:00
                :return: date
        """
        created_raw = response.xpath('//span[@class="ArticleDate"]/text()').get()
        created_at = date_parse(created_raw)
        return created_at.strftime('%d/%m/%Y')

    def parse_author(self, response):
        """
        Get author from response
        :param response:
        :return: the author of article or '' if None
        """
        if response.xpath('//*[@id="ArticleContent"]/p[last()]').get():
            return html2text(
                response.xpath('//*[@id="ArticleContent"]/p[last()]').get())
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

        image_list = response.xpath('//*[@id="ArticleContent"]//img/@src').extract()
        captions_list = response.xpath('//*[@id="ArticleContent"]//img/@alt').extract()

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
