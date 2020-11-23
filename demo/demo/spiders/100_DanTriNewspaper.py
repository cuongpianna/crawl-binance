import urllib.parse
from datetime import datetime

import html2text

from scrapy import Spider, Request
from html2text import html2text
from sqlalchemy.orm import sessionmaker
from demo.items import NewsItem
from demo.models import db_connect, create_table, Article

categories = {
    'xa_hoi': 'xa-hoi',
    'the_gioi': 'the-gioi',
    'the_thao': 'the-thao',
    'lao_dong_viec_lam': 'lao-dong-viec-lam',
    'suc_khoe': 'suc-khoe',
    'nhan_ai': 'tam-long-nhan-ai',
    'kinh_doanh': 'kinh-doanh',
    'bat_dong_san': 'bat-dong-san',
    'xe++': 'o-to-xe-may',
    'suc_manh_so': 'suc-manh-so',
    'giao_duc': 'giao-duc-huong-nghiep',
    'van_hoa': 'van-hoa',
    'du_lich': 'du_lich',
    'phap_luat': 'phap_luat',
    'nhip_song_tre': 'nhip-song-tre'
}


class DanTriNewspaperSpider(Spider):
    name = 'DanTriNewspaper'
    site_name = 'dantri.com.vn'
    allowed_domains = ['dantri.com.vn']
    start_urls = ['http://dantri.com.vn']

    base_url = 'https://dantri.com.vn/'
    url_templates = 'https://dantri.com.vn/{category}/trang-{page}.htm'

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
    }

    def __init__(self, page=1000, *args, **kwargs):
        super(DanTriNewspaperSpider, self).__init__(*args, **kwargs)
        self.page = int(page)

    def start_requests(self):
        urls = []

        for cate in categories.values():
            for i in range(1, self.page + 1):
                url = self.url_templates.format(page=i, category=cate)
                urls.append(url)
        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        """
            Get all article urls and yield it to parse_post function
            :param response:
            :return:
        """
        posts = response.xpath('//div[@class="col col--highlight-news clearfix"]//h3/a/@href')

        for post in posts:
            url_extract = post.extract()
            url = urllib.parse.urljoin(self.base_url, url_extract)
            yield Request(url, callback=self.parse_post)

        articles = response.xpath('//ul[@class="dt-list dt-list--lg"]/li/div/a/@href')
        for post in articles:
            url_extract = post.extract()
            url = urllib.parse.urljoin(self.base_url, url_extract)
            yield Request(url, callback=self.parse_post)

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

            site='100_dan_tri',
            title=response.css('h1::text').extract_first().strip(),
            original_link=response.url,
            body=html2text(response.xpath('//*[@class="dt-news__content"]').get()),
            date=self.parse_timestamp(response),
            subhead=response.xpath('//div[@class="dt-news__sapo"]/h2/text()').get(),
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
        created_raw = response.xpath('//span[@class="dt-news__time"]/text()').get().split(',')[1]
        created_at = datetime.strptime(created_raw.strip(), '%d/%m/%Y - %H:%M')
        return created_at.strftime('%d/%m/%Y')

    def parse_author(self, response):
        """
        Get author from response
        :param response:
        :return: the author of article or '' if None
        """
        if response.xpath('//div[@class="dt-news__content"]/p[@style="text-align:right"]/strong').get():
            return html2text(response.xpath('//div[@class="dt-news__content"]/p[@style="text-align:right"]/strong').get())
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

        image_list = response.xpath('//div[@class="dt-news__content"]//img/@src').extract()
        captions_list = response.xpath('//div[@class="dt-news__content"]//img/@alt').extract()

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
