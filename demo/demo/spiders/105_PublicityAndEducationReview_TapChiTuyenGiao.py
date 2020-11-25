import re

import html2text
from dateutil.parser import parse as date_parse
from scrapy import Spider, Request
from html2text import html2text
from sqlalchemy.orm import sessionmaker
from demo.items import NewsItem
from demo.models import db_connect, create_table, Article
from urllib.parse import urljoin


class PublicityAndEducationReviewSpider(Spider):
    name = 'PublicityAndEducationReview'
    site_name = 'www.tuyengiao.vn'
    allowed_domains = ['www.tuyengiao.vn']

    base_url = 'http://www.tuyengiao.vn/'

    start_urls = [
        'http://www.tuyengiao.vn/thoi-su',
        'http://www.tuyengiao.vn/nhip-cau-tuyen-giao',
        'http://www.tuyengiao.vn/theo-guong-bac',
        'http://www.tuyengiao.vn/bao-ve-nen-tang-tu-tuong-cua-dang',
        'http://www.tuyengiao.vn/van-hoa-xa-hoi',
        'http://www.tuyengiao.vn/khoa-giao',
        'http://www.tuyengiao.vn/kinh-te',
        'http://www.tuyengiao.vn/the-gioi',
        'http://www.tuyengiao.vn/tu-lieu'
    ]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.93 Safari/537.36',
    }

    def parse(self, response):
        flag_break = False
        posts = response.xpath('//div[@class="zonepage-l"]//h4/a/@href')
        for post in posts:
            url = urljoin(self.base_url, post.extract())
            if self.check_exist_article(url):
                flag_break = True
            yield Request(url, callback=self.parse_post)

        # next = response.xpath('//div[@class="datapager"]/span[@class="active"]/following-sibling::a[1]/@href').get()
        # if next and not flag_break:
        #     yield Request(urljoin(self.base_url, next))

    def parse_post(self, response):
        print('@@@@@@@@@@@@')
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

            site='105_tapchituyengiao',
            title=response.xpath('//span[@class="story_headline"]/text()').get().strip(),
            original_link=response.url,
            body=html2text(response.xpath('//*[@class="story_body"]').get()),
            date=self.parse_timestamp(response),
            subhead=html2text(response.xpath('//*[@class="story_teaser clearfix"]').get()),
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
        created_raw = response.xpath('//span[@class="story_date"]/text()').get()
        match_time = re.search(r'[0-9]{1,2}\/[0-9]{1,2}\/[0-9]{4}', created_raw).group(0)
        created_at = date_parse(match_time)
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

    def parse_pic(self, response):
        """
        Get pictures list from response. Format: link|title&&link|title
        Or
        return ' '
        :param response:
        :return: list pictures
        """

        avatar = response.xpath('//*[@class="story_avatar_b"]/img/@src').get()
        caption = response.xpath('//*[@class="story_avatar_b"]/span/text()').get()

        images = [avatar]
        captions = [caption]

        image_list = response.xpath('//div[@class="storydetail clearfix"]//table[@class="tbl-image"]//img/@src').extract()
        captions_list = response.xpath('//div[@class="storydetail clearfix"]//table[@class="tbl-image"]//td[@class="td-image-desc"]/p/text()').extract()

        image_list = images + image_list
        image_list = [urljoin(self.base_url, item) for item in image_list]
        captions = images + captions_list

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
