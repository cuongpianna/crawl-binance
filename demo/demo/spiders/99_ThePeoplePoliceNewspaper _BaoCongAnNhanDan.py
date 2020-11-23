from scrapy import Spider, Request
from html2text import html2text
from sqlalchemy.orm import sessionmaker
from dateutil import parser
from demo.items import NewsItem
from demo.models import db_connect, create_table, Article


class ThePeoplePoliceNewspaperSpider(Spider):
    name = 'ThePeoplePoliceNewspaper'
    allowed_domains = ['cand.com.vn']

    base_url = 'http://cand.com.vn/'

    start_urls = [
        'http://cand.com.vn/thoi-su/', 'http://cand.com.vn/Chong-dien-bien-hoa-binh/', 'http://cand.com.vn/cong-an/',
        'http://cand.com.vn/xa-hoi/', 'http://cand.com.vn/phap-luat/', 'http://cand.com.vn/quoc-te/',
        'http://cand.com.vn/van-hoa/', 'http://cand.com.vn/Ban-doc-cand/'
    ]

    def parse(self, response):
        """
        Get all article urls and yield it to parse_post function
        :param response:
        :return:
        """

        flag_break = True

        posts = response.xpath('//div[@id="LeftZoneTop"]//h1/a/@href')
        for post in posts:
            if self.check_exist_article(post.extract()):
                flag_break = False
            yield Request(post.extract(), callback=self.parse_post)

        next_page = response.xpath('//a[@class="next "]/@href').get()
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

        content_html = response.xpath('//*[@class="box-widget post-content"]').get()
        item = NewsItem(
            title=response.xpath('//h1[@class="box-widget titledetail"]/text()').get().strip(),
            body=html2text(content_html),
            original_link=response.url,
            subhead=html2text(response.xpath('//*[@class="box-widget desnews"]').get()),
            pic_list=self.parse_pic(response),
            date=self.parse_timestamp(response, 'date'),
            author=self.parse_author(response),
            site='99_bao_cong_an_nhan_dan',
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

        image_list = response.xpath('//*[@class="box-widget post-content"]//td[@class="img"]/img/@src').extract()
        captions_list = []

        for index, item in enumerate(image_list):
            if response.xpath('(//*[@class="box-widget post-content"]//td[@class="img"])[{}]/parent::tr/following-sibling::tr/td/text()'.format(index + 1)).get():
                captions_list.append(response.xpath('(//*[@class="box-widget post-content"]//td[@class="img"])[{}]/parent::tr/following-sibling::tr/td/text()'.format(index + 1)).get())
            else:
                captions_list.append(' ')

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
        str_timestamp = response.xpath('//div[@class="box-widget timepost"]/text()').get()
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
        if response.xpath('//div[@class="aliaspost"]/text()').get():
            return response.xpath('//div[@class="aliaspost"]/text()').get()
        return ''

    def check_exist_article(self, url):
        engine = db_connect()
        create_table(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        exist_article = session.query(Article).filter_by(original_link=url).first()
        return exist_article
