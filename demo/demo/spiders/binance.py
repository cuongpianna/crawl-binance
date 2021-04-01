from scrapy import Spider, Request
import re
from datetime import datetime
from html2text import html2text
from demo.items import ProjectItem


class BinanceSpider(Spider):
    name = 'BinanceSpider'
    start_urls = ['https://research.binance.com/en/projects']
    base_url = 'research.binance.com'

    def parse(self, response):
        top_post = response.xpath(
            '//div[@class="jsx-2930351579 list"]/a/@href')

        for post in top_post:
            yield response.follow(post.get(), callback=self.parse_post)

    def parse_post(self, response):
        name, crypt = self.parse_name(response)
        item = ProjectItem(
            Crypt=name,
            Name=name,
            Tagline=html2text(response.xpath('//em').get()).strip(),
            Date=html2text(response.xpath('//time').get()).strip(),
            Description=html2text(response.xpath('//div[@class="jsx-341700367"]').get()).strip(),
            Website=response.xpath('//ul[@class="jsx-2167690016"]/li/a[text()="Website"]/@href').get(),
            Explorer=response.xpath('//ul[@class="jsx-2167690016"]/li/a[text()="Explorer"]/@href').get(),
            SourceCode=response.xpath('//ul[@class="jsx-2167690016"]/li/a[text()="Source Code"]/@href').get(),
            TechnicalDocument=response.xpath('//ul[@class="jsx-2167690016"]/li/a[text()="Technical Documentation"]/@href').get()
        )
        yield item

    def parse_name(self, response):
        name_html = html2text(response.xpath('//h1/text()').get()).strip()
        crypt = re.findall(r'(\(.*?\))', name_html)
        crypt = crypt[0]
        crypt = crypt[1:-1]
        name = name_html[:name_html.index('(')]
        return name, crypt

    @staticmethod
    def parse_pic(response):
        pics = []
        img_elements = response.xpath("//div[@id='cotent_detail']/div/center/img/@src").extract()
        for index, img_element in enumerate(img_elements):
            src = img_element
            cap = response.xpath(
                '(//div[@id="cotent_detail"]/div/center/img)[{}]/..//following-sibling::*/text()'.format(index + 1))
            if index % 2 == 0:
                pics.append(f"{src}|{cap}")
            else:
                pics.append(f"{src}_{cap}")
        return "&&".join(pics)

    def parse_author(self, response):
        """
        Get author from response
        :param response:
        :return: the author of article or '' if None
        """
        if response.xpath(
                "//div[@class='col660 fl bg_white']/div[@id='cotent_detail']/*[@style='text-align: right;']").get():
            return html2text(
                response.xpath(
                    "//div[@class='col660 fl bg_white']/div[@id='cotent_detail']/*[@style='text-align: right;']").get())
        return ''
