from scrapy import Spider, Request
from html2text import html2text
from sqlalchemy.orm import sessionmaker
from dateutil import parser
from demo.items import NewsItem
from demo.models import db_connect, create_table, Article


class VietnamNewsSpider(Spider):
    name = 'VietnamNews'
    allowed_domains = ['vnexpress.net']

    base_url = 'https://vnexpress.net'

    start_urls = [
        'https://vnexpress.net/thoi-su', 'https://vnexpress.net/suc-khoe',
        'https://vnexpress.net/the-gioi', 'https://vnexpress.net/doi-song',
        'https://vnexpress.net/kinh-doanh', 'https://vnexpress.net/du-lich',
        'https://vnexpress.net/giai-tri', 'https://vnexpress.net/khoa-hoc',
        'https://vnexpress.net/the-thao', 'https://vnexpress.net/so-hoa',
        'https://vnexpress.net/phap-luat', 'https://vnexpress.net/oto-xe-may',
        'https://vnexpress.net/giao-duc', 'https://vnexpress.net/y-kien',
        'https://vnexpress.net/hai'
    ]

    def parse(self, response):
        """
        Get all article urls and yield it to parse_post function
        :param response:
        :return:
        """

        flag_break = True

        top_news = response.xpath('//*[@class="item-news full-thumb article-topstory"]/div/a/@href').get()
        if top_news:
            yield Request(top_news, callback=self.parse_post)

        sub_news = response.xpath('//*[@class="sub-news-top"]//h3/a/@href')
        for post in sub_news:
            yield Request(post.extract(), callback=self.parse_post)

        articles = response.xpath('//*[@class="width_common list-news-subfolder"]/article/h3/a/@href')
        for post in articles:
            yield Request(post.extract(), callback=self.parse_post)
            if self.check_exist_article(post.extract()):
                flag_break = False

        next_page = response.xpath('//a[@class="btn-page next-page "]/@href').get()
        if next_page and not flag_break:
            yield response.follow(next_page)

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

        content_html = response.xpath('//article[@class="fck_detail "]').get()
        item = NewsItem(
            title=response.xpath('//h1[@class="title-detail"]/text()').get().strip(),
            body=html2text(content_html),
            original_link=response.url,
            subhead=html2text(response.xpath('//p[@class="description"]/text()').get()),
            pic_list=self.parse_pic(response),
            date=self.parse_timestamp(response, 'date'),
            author=self.parse_author(response),
            site='102_vnexpress',
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

        image_list = response.xpath('//article[@class="fck_detail "]//img/@data-src').extract()
        captions_list = response.xpath('//article[@class="fck_detail "]//img/@alt').extract()

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
        str_timestamp = response.xpath('//span[@class="date"]/text()').get().split(',')[1].strip()
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
        if response.xpath('//p[@class="author_mail"]').get():
            return html2text(response.xpath('//p[@class="author_mail"]').get()).replace('[__](javascript:;)', '')
        elif response.xpath('//p[@style="text-align:right;"]/strong/text()').get():
            return response.xpath('//p[@style="text-align:right;"]/strong/text()').get()
        return ''

    def check_exist_article(self, url):
        engine = db_connect()
        create_table(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        exist_article = session.query(Article).filter_by(original_link=url).first()
        return exist_article
