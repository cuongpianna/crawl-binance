import scrapy
from datetime import datetime
from scrapy import Request
import html2text

from demo.items import NewsItem


class CatholicAndEthnicNewspaperSpider(scrapy.Spider):
    name = 'CatholicAndEthnicNewspaper'  # Name of spiders
    site_name = 'cgvdt.vn'  # Site name
    allowed_domains = ['cgvdt.vn']

    # Urls will be crawl
    start_urls = ['http://www.cgvdt.vn/ban-doc_at15', 'http://www.cgvdt.vn/giao-hoi-viet-nam_at44',
                  'http://www.cgvdt.vn/cong-giao-viet-nam_at7',
                  'http://www.cgvdt.vn/cong-giao-viet-nam/dau-chan-muc-tu_at61',
                  'http://www.cgvdt.vn/cong-giao-the-gioi_at6', 'http://www.cgvdt.vn/loi-chua-va-cuoc-song_at8',
                  'http://www.cgvdt.vn/duc-giam-muc-bui-tuan_at9', 'http://www.cgvdt.vn/linh-muc-ngo-phuc-hau_at10',
                  'http://www.cgvdt.vn/xa-hoi_at89']

    def parse(self, response):
        """
        Get all post of page and yield it to parse_post function
        :param response:
        :return:
        """
        current_page = response.xpath('//li[@class="page-number pgCurrent"]/text()').get()

        if current_page != '1':
            hentry_post = response.xpath('//div[@class="news_home hentry"]/a').css('::attr(href)').get()
            yield Request(hentry_post, callback=self.parse_post)

            hot_news = response.xpath('//ul[@id="divTinMoi"]/li/a').css('::attr(href)').extract()
            for post in hot_news:
                yield Request(post, callback=self.parse_post)

            views_news = response.xpath('//ul[@id="divTinXemNhieu"]/li/a').css('::attr(href)').extract()
            for post in views_news:
                yield Request(post, callback=self.parse_post)

        posts = response.xpath('//div[@class="news_row hentry"]/a').css('::attr(href)')

        for post in posts:
            url_extract = post.extract()
            yield Request(url_extract, callback=self.parse_post)

        next_page = response.xpath('//li[@class="pgNext"]/a')

        if next_page:
            next_url = response.xpath('//li[@class="pgNext"]/a').css('::attr(href)').get()
            yield Request(next_url)

    def parse_post(self, response):
        """ This function returns newspaper articles on a given date in a given structure.

            Return data structure:
            [
                {
                    'title': string,                        # The title of a article
                    'author'                                # The author of a article, of '' if none
                    'subhead': string,                      # The subtitle of a article, or '' if there is no subtitle
                    'print': string,                        # The page number of a article
                    'date': string in '%Y-%m-%d' format,    # The publish date of a article
                    'body': string                          # The body of a article
                    'pic_list': string in                        # The link of pictures of a article, or '' if there are no pictures
                                                            f"{link1}|{text2}&&..." format
                    'original_link': string                          # The url of a article
                },
                ...
            ]
            or
            None

        :param response: The scrapy response
        :return:
        """
        author = self.parse_author(response)
        time_format, short_date = self.parse_date(response)
        item = NewsItem(
            site='bao_cong_giao_va_dan_toc',
            title=response.xpath('//h1/text()').get(),
            # timestamp=time_format,
            body=html2text.html2text(response.xpath('//div[@class="news_content entry-content"]').get()),
            original_link=response.url,
            subhead='',
            pic_list=self.parse_pictures(response),
            date=short_date,
            author=author,
            source='',
            print=''
        )
        # TODO: Parse article and yield it
        yield item

    def parse_date(self, response):
        """
        Convert date string to timestamp and date
        :param response: timeformat: 07/10/2020
        :return: Timestamp and date
        """
        created_raw = response.xpath('//p[@class="date published"]/text()').get()
        date_split = created_raw.split(',')
        day_month = date_split[1].strip().split(' ', 1)
        month = self.convert_month(day_month[1])
        day = day_month[0]

        yhm = date_split[2].strip()
        yyyy = yhm[:4]
        hh = yhm.split(' ')[1].split(':')[0]
        mm = yhm.split(' ')[1].split(':')[1]

        dt = datetime(year=int(yyyy), month=int(month), day=int(day), hour=int(hh), minute=int(mm))
        short_date = '{}/{}/{}'.format(dt.month, dt.day, dt.year)
        time_format = dt.isoformat()
        return time_format, short_date

    @staticmethod
    def parse_pictures(response):
        """
        :param response:
        :return: Pictures list
        """
        urls = response.xpath('//table[@class="image"]/tbody//img/@src').extract()
        caption_template = '//table[@class="image"][{}]/tbody/tr[2]/td/text()'

        count = 1
        captions = []
        for _ in urls:
            caption = response.xpath(caption_template.format(count)).get()
            if caption:
                captions.append(caption)
            else:
                captions.append(' ')
            count += 1

        res = [i + '|' + j for i, j in zip(urls, captions)]
        if urls:
            result = '&&'.join(res)
            return result
        return ''

    @staticmethod
    def convert_month(month):
        """
        Convert Vietnamese month to number
        :param month:
        :return:
        """
        month = month.strip()
        if month == 'Tháng Tám':
            return 8
        elif month == 'Tháng Tư':
            return 4
        elif month == 'Tháng Chín':
            return 9
        elif month == 'Tháng Mười':
            return 10
        elif month == 'Tháng Bảy':
            return 7
        elif month == 'Tháng Mười Hai':
            return 12
        elif month == 'Tháng Giêng':
            return 1
        elif month == 'Tháng Ba':
            return 3
        elif month == 'Tháng Hai':
            return 2
        elif month == 'Tháng Năm':
            return 5
        elif month == 'Tháng Sáu':
            return 6
        elif month == 'Tháng Mười Một':
            return 11

    def parse_author(self, response):
        """
        Get author from response
        :param response:
        :return: author
        """
        if response.xpath('//p[@style="text-align: right;"]/strong/text()').extract():
            author = response.xpath('//p[@style="text-align: right;"]/strong/text()')[-1].extract()
        elif response.xpath('//p[@style="text-align: right;"]/span/text()'):
            author = response.xpath('//p[@style="text-align: right;"]/span/text()')[-1].extract()
        else:
            author = ''
        return author
