import scrapy
import urllib.parse
from datetime import datetime
from scrapy import Request, FormRequest
from dateutil import parser
import html2text

from demo.items import NewsItem


class VietnamJournalOfConstructionSpider(scrapy.Spider):
    name = 'VietnamJournalOfConstruction'
    site_name = 'tapchixaydungbxd.vn'
    allowed_domains = ['tapchixaydungbxd.vn']

    base_url = 'http://tapchixaydungbxd.vn/'
    base_api = 'http://tapchixaydungbxd.vn/?module=Content.Listing&moduleId=23&cmd=redraw&site=13255&url_mode=rewrite&submitFormId=23&moduleId=23&page=customPage&site=13255'

    def __init__(self, page=10, *args, **kwargs):
        super(VietnamJournalOfConstructionSpider, self).__init__(*args, **kwargs)
        self.page = int(page)

    def start_requests(self):
        for i in range(1, self.page):
            form_data = {"layout": "Article.List.highLight", "itemsPerPage": "10",
                         "orderBy": "sortOrder DESC", "service": "Content.Article.selectAll", "pageNo": str(i)}

            yield FormRequest(self.base_api, formdata=form_data, callback=self.parse)

    def parse(self, response):
        posts = response.xpath('//figure/a/@href')
        if posts:
            for p in posts:
                url = p.extract()
                url = urllib.parse.urljoin(self.base_url, url)
                yield Request(url, callback=self.parse_post)

    def parse_post(self, response):
        time_format, short_date = self.parse_date(response)
        item = NewsItem(
            title=response.xpath('//h1[@itemprop="headline"]/text()').get(),
            timestamp=time_format,
            content_html=response.xpath('//div[@class="content-detail"]').get(),
            body=html2text.html2text(response.xpath('//div[@class="content-detail"]').get()),
            link=response.url,
            subhead=html2text.html2text(response.xpath('//div[@class="brief-detail"]').get()),
            pic=self.parse_pictures(response),
            date=short_date,
            author=self.parse_author(response)
        )
        yield item

    def parse_date(self, response):
        """
        Convert time string to timestamp
        :param response:
        :return:
        """
        raw_time = html2text.html2text(response.xpath('//*[@class="news-date"]/text()').get())
        converted_time = parser.parse(raw_time)
        publish_date = datetime(year=converted_time.year, minute=converted_time.minute, hour=converted_time.hour,
                                day=converted_time.day,
                                month=converted_time.month)
        return publish_date.isoformat(), '{}/{}/{}'.format(converted_time.month, converted_time.day,
                                                           converted_time.year)

    def parse_pictures(self, response):
        """
        Get pictures from response.
        :param response:
        :return:
        """
        if response.xpath('//div[@class="content-detail"]/table//img/@src').get():  # image in <table>
            urls = response.xpath('//div[@class="content-detail"]/table//img/@src').extract()
            urls = [urllib.parse.urljoin(self.base_url, item) for item in urls]
            count = 1
            captions = []
            for _ in urls:
                if response.xpath('//div[@class="content-detail"]/table[{}]//tbody/tr[2]/td'.format(count)):
                    caption = html2text.html2text(
                        response.xpath('//div[@class="content-detail"]/table[{}]//tbody/tr[2]/td'.format(count)).get())
                    captions.append(caption)
                else:
                    captions.append(' ')
                count += 1
            res = [i + '|' + j for i, j in zip(urls, captions)]
            return '&&'.join(res)
        elif response.xpath('//div[@class="content-detail"]/p//img/@src'):  # image in <p>
            urls = response.xpath('//div[@class="content-detail"]/p//img[1]/@src').extract()
            urls = [urllib.parse.urljoin(self.base_url, item) for item in urls]
            captions = []
            for ind, val in enumerate(urls):
                if response.xpath(
                        '(//div[@class="content-detail"]/p//img[{}])/ancestor::p//following-sibling::p[1]//strong'.format(
                            ind + 1)):
                    caption = html2text.html2text(response.xpath(
                        '(//div[@class="content-detail"]/p//img[{}])/ancestor::p//following-sibling::p[1]//strong'.format(
                            ind + 1)).get())
                elif response.xpath(
                        '(//div[@class="content-detail"]/p//img[{}])/ancestor::p//following-sibling::p[1]//em'.format(
                            ind + 1)):
                    caption = html2text.html2text(response.xpath(
                        '(//div[@class="content-detail"]/p//img[{}])/ancestor::p//following-sibling::p[1]//em'.format(
                            ind + 1)).get())
                elif html2text.html2text(
                        response.xpath(
                            '(//div[@class="content-detail"]/p//img[{}])/ancestor::a/ancestor::span'.format(
                                ind + 1)).get()):
                    caption = html2text.html2text(
                        response.xpath('(//div[@class="content-detail"]/p//img[{}])/ancestor::a/ancestor::span'.format(
                            ind + 1)).get())
                else:
                    caption = ' '
                captions.append(caption)
                res = [i + '|' + j for i, j in zip(urls, captions)]
                return '&&'.join(res)
        return ''

    @staticmethod
    def parse_author(response):
        if response.xpath('//div[@class="content-detail"]/p[last()]'):
            return html2text.html2text(response.xpath('//div[@class="content-detail"]/p[last()]').get())
        return ''

    def parse_content(self, response):
        raw_text = response.xpath('//div[@class="post-content "]/p/text()').extract()
        raw_html = response.xpath('//div[@class="post-content "]/p').extract()
        return ' '.join(raw_text), ' '.join(raw_html)
