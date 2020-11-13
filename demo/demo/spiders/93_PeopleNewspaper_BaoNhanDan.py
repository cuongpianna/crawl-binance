from scrapy import Spider, Request
from urllib.parse import urljoin

from html2text import html2text
from dateutil import parser

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


class PeopleNewspaperSpider(Spider):
    name = 'PeopleNewspaper'
    allowed_domains = ['nhandan.com.vn']

    base_url = 'https://nhandan.com.vn/'
    url_templates = 'https://nhandan.com.vn/article/Paging?categoryId={cate_id}&pageIndex={page}&pageSize=20&fromDate=&toDate=&displayView=PagingPartial'

    def __init__(self, page=10, *args, **kwargs):
        super(PeopleNewspaperSpider, self).__init__(*args, **kwargs)
        self.page = int(page)

    def start_requests(self):
        """
        Get all page urls to crawl
        :return:
        """
        urls = []

        for category in categories.values():
            for i in range(1, self.page):
                url = self.url_templates.format(cate_id=category, page=i)
                urls.append(url)
        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        """
        Get all article urls and yield it to parse_post function
        :param response:
        :return:
        """
        posts = response.xpath('//div[@class="box-title"]/a/@href')
        for post in posts:
            url = urljoin(self.base_url, post.extract())
            yield Request(url, self.parse_post)

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

        content_html = response.xpath('//div[@class="detail-content-body "]').get()
        return {
            'date': self.parse_timestamp(response, 'date'),
            'timestamp': self.parse_timestamp(response, 'iso'),
            'title': response.xpath('//h1/text()').get(),
            'subhead': response.xpath('//div[@class="box-des-detail this-one"]/p/text()').get(),
            'link': response.url,
            'pic': self.parse_pic(response),
            'body': html2text(content_html),
            'content_html': content_html,
            'author': self.parse_author(response)
        }

    @staticmethod
    def parse_pic(response):
        """
        Get pictures list from response. Format: link|title&&link|title
        Or
        return ' '
        :param response:
        :return: list pictures
        """

        top_image_str = ''
        top_image = response.xpath('//div[@class="box-detail-thumb uk-text-center"]//img/@src').get()
        if top_image:
            caption = html2text(
                response.xpath('//div[@class="box-detail-thumb uk-text-center"]//img//following-sibling::em').get())
            top_image_str = top_image + '|' + caption

        urls = response.xpath('//div[@class="detail-content-body "]//img/@src').extract()
        captions = response.xpath('//div[@class="detail-content-body "]//img/@alt').extract()
        res = [i + '|' + j for i, j in zip(urls, captions)]
        if urls:
            result = '&&'.join(res)
            return top_image_str + result
        else:
            return top_image_str + ''

    @staticmethod
    def parse_timestamp(response, type_parse):
        """
        Convert publish date string format to datetime format
        :param response:
        :param type_parse: date or iso
        :return: Timestamp or date
        """
        str_timestamp = response.xpath('//div[@class="box-date pull-left"]/text()').get().split(',')

        str_timestamp = str_timestamp[1].strip() + ' ' + str_timestamp[2].strip()
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
        if response.xpath('//div[@class="box-author uk-text-right uk-clearfix"]/strong/text()').get():
            return html2text(response.xpath('//div[@class="box-author uk-text-right uk-clearfix"]/strong/text()').get())
        return ''
