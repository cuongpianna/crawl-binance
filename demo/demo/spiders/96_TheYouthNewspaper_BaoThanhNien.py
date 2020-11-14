from scrapy import Spider
from urllib.parse import urljoin

from html2text import html2text
from dateutil import parser
from demo.items import NewsItem

categories = {
    'chinh_tri': 1171,
    'kinh_te': 1185,
    'van_hoa': 1251,
    'xa_hoi': 1211,
    'phap_luat': 1287,
    'du_lich': 1257,
    'the_gioi': 1231,
    'the_thao': 1224,
    'giao_duc': 1303,
    'y_te': 1309,
    'khoa_hoc_cong_nghe': 1292,
    'ban_doc': 1315
}


class TheYouthNewspaperSpider(Spider):
    name = 'TheYouthNewspaper'
    allowed_domains = ['thanhnien.vn']

    base_url = 'http://thanhnien.vn/'

    start_urls = [
        'http://thanhnien.vn/thoi-su/',
        'http://thanhnien.vn/the-gioi/',
        'http://thanhnien.vn/tai-chinh-kinh-doanh/',
        'http://thanhnien.vn/doi-song/',
        'http://thanhnien.vn/giai-tri/',
        'http://thanhnien.vn/van-hoa/',
        'http://thanhnien.vn/giai-tri/',
        'http://thanhnien.vn/gioi-tre/',
        'http://thanhnien.vn/giao-duc/',
        'https://thanhnien.vn/the-thao/',
        'https://thanhnien.vn/suc-khoe/',
        'https://thanhnien.vn/du-lich/',
        'https://thanhnien.vn/xe/',
        'https://thanhnien.vn/game/'
    ]

    def __init__(self, max_page=1000, *args, **kwargs):
        """
        :param max_page: Max page to crawl
        """
        super(TheYouthNewspaperSpider, self).__init__(*args, **kwargs)
        self.max_page = int(max_page)

    def parse(self, response):
        """
        Get all article urls and yield it to parse_post function
        :param response:
        :return:
        """
        if response.xpath('//*[@class="pagination"]/li[@class="active"]/a/text()').get() == '1':
            top_news = response.xpath('//div[@class="highlight"]//h2/a/@href').get()
            yield response.follow(top_news, callback=self.parse_post)

            features_news = response.xpath('//div[@class="feature"]//h2/a/@href')
            if features_news:
                for item in features_news:
                    url = item.extract()
                    yield response.follow(url, callback=self.parse_post)

        posts = response.xpath('//*[@class="zone--timeline"]//h2/a/@href')
        for post in posts:
            url = urljoin(self.base_url, post.extract())
            yield response.follow(url, self.parse_post)

        current_page = response.xpath('//*[@class="zone--timeline"]//ul/li[@class="active"]/a/text()').get()
        if current_page:
            next_page = response.xpath(
                '//*[@class="zone--timeline"]//ul/li/a[text()="{}"]/@href'.format(int(current_page) + 1)).get()
            if next_page and int(current_page) + 1 <= self.max_page:
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
                    'timestamp': string in Iso 8061 format  # The ISO publish date of a article
                    'body': string                          # The body of a article
                    'pic': string in                        # The link of pictures of a article, or '' if there are no pictures
                                                                    f"{link1}|{text2}&&..." format
                    'link': string                          # The url of a article
                },
                        ...
            ]
            or
            None

            :param response: The scrapy response
            :return:
            """

        content_html = response.xpath('//*[@id="abody"]').get()
        item = NewsItem(
            title=response.xpath('//*[@class="details__headline"]/text()').get(),
            timestamp=self.parse_timestamp(response, 'iso'),
            content_html=content_html,
            body=html2text(content_html),
            link=response.url,
            subhead=html2text(response.xpath('//div[@class="sapo"]').get()),
            pic=self.parse_pic(response),
            date=self.parse_timestamp(response, 'date'),
            author=self.parse_author(response)
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
        img = response.xpath('//*[@id="contentAvatar"]//img/@src').get()
        if img:
            images.append(img)
            caption = response.xpath('//*[@id="contentAvatar"]//img/@alt').get()
            captions.append(caption)

        image_list = response.xpath('//div[@id="abody"]//img/@src').extract()
        captions_list = response.xpath('//div[@id="abody"]//img/@alt').extract()

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
        str_timestamp = response.xpath('//*[@class="details__meta"]//div[@class="meta"]/time/text()').get().split('-')
        str_timestamp = str_timestamp[0].strip() + ' ' + str_timestamp[1].strip()
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
        if response.xpath('//div[@class="left"]/h4/a/text()').get():
            return html2text(response.xpath('//div[@class="left"]/h4/a/text()').get())
        return ''
