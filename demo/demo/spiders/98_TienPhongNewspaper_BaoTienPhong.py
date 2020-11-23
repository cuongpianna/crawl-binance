from scrapy import Spider, Request
from html2text import html2text
from sqlalchemy.orm import sessionmaker
from dateutil import parser
from demo.items import NewsItem
from demo.models import db_connect, create_table, Article


class TienPhongNewspaperSpider(Spider):
    name = 'TienPhongNewspaper'
    allowed_domains = ['www.tienphong.vn']

    base_url = 'https://www.tienphong.vn/'

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
    }

    start_urls = [
        'https://www.tienphong.vn/xa-hoi/', 'https://www.tienphong.vn/kinh-te/', 'https://www.tienphong.vn/dia-oc/',
        'https://www.tienphong.vn/suc-khoe/', 'https://www.tienphong.vn/the-gioi/',
        'https://www.tienphong.vn/gioi-tre/', 'https://www.tienphong.vn/xe/',
        'https://www.tienphong.vn/phap-luat/', 'https://www.tienphong.vn/hoa-hau/',
        'https://www.tienphong.vn/the-thao/', 'https://www.tienphong.vn/ban-doc/',
        'https://www.tienphong.vn/hanh-trang-nguoi-linh/', 'https://www.tienphong.vn/van-hoa/',
        'https://www.tienphong.vn/giai-tri/', 'https://www.tienphong.vn/giao-duc/',
        'https://www.tienphong.vn/cong-nghe/', 'https://www.tienphong.vn/photo/', 'https://www.tienphong.vn/megastory/',
        'https://www.tienphong.vn/infographics/', 'https://www.tienphong.vn/nhip-song-thu-do/',
        'https://www.tienphong.vn/toi-nghi/'
    ]

    def __init__(self, max_page=1000, *args, **kwargs):
        """
        :param max_page: Max page to crawl
        """
        super(TienPhongNewspaperSpider, self).__init__(*args, **kwargs)
        self.max_page = int(max_page)

    def parse(self, response):
        """
        Get all article urls and yield it to parse_post function
        :param response:
        :return:
        """

        flag = True

        posts = response.xpath('//div[@class="highlight-v2"]//a/@href')
        for post in posts:
            yield Request(post.extract(), callback=self.parse_post)

        articles = response.xpath('//article[@class="story left-story border-story "]/a/@href')
        for post in articles:
            if self.check_exist_article(post.extract()):
                flag = False
            yield Request(post.extract(), callback=self.parse_post)

        next_page = response.xpath('//*[@id="ctl00_mainContent_ContentList1_pager"]/ul/li[last()]/a/@href').get()
        if next_page and not flag:
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

        content_html = response.xpath('//div[@id="article-body"]').get()
        item = NewsItem(
            title=response.xpath('//h1[@id="headline"]/text()').get().strip(),
            body=html2text(content_html),
            original_link=response.url,
            subhead=html2text(response.xpath('//p[@class="article-sapo cms-desc"]').get()),
            pic_list=self.parse_pic(response),
            date=self.parse_timestamp(response, 'date'),
            author=self.parse_author(response),
            site='98_bao_tien_phong',
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

        images = []
        captions = []
        img = response.xpath('//*[@class="article-avatar cms-body"]//img/@src').get()
        if img:
            images.append(img)
            caption = response.xpath('//*[@class="article-avatar cms-body"]//img/@alt').get()
            captions.append(caption)

        image_list = response.xpath('//*[@id="article-body"]//img/@src').extract()
        captions_list = response.xpath('//*[@id="article-body"]//img/@alt').extract()

        if image_list:
            images = images + image_list
            captions = captions + captions_list
        res = [i + '|' + j for i, j in zip(images, captions)]

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
        str_timestamp = response.xpath('//p[@class="byline-dateline"]/time/text()').get()
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
        if response.xpath('//p[@class="article-author cms-author"]').get():
            return html2text(response.xpath('//p[@class="article-author cms-author"]').get())
        return ''

    def check_exist_article(self, url):
        engine = db_connect()
        create_table(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        exist_article = session.query(Article).filter_by(original_link=url).first()
        return exist_article
