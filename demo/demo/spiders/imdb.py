from scrapy import Spider, Request
import re
from datetime import datetime
from html2text import html2text
from demo.items import FilmItem


class IMDBSpider(Spider):
    name = 'IMDBSpider'
    start_urls = ['https://www.imdb.com//search/title/?view=simple&sort=release_date,desc&start=1&ref_=adv_nxt']
    base_url = 'https://www.imdb.com/'

    def parse(self, response):
        top_post = response.xpath('//div[@class="lister-item mode-simple"]//div[@class="col-title"]//a/@href')

        for post in top_post:
            yield response.follow(post.get(), callback=self.parse_post)

        next_url = response.xpath('(//div[@class="desc"])[1]/a[@class="lister-page-next next-page"]/@href').get()
        print('cuonggggggggg')
        print(next_url)
        if next_url:
            yield response.follow(next_url, callback=self.parse)

    def parse_post(self, response):
        categories = self.parse_categories(response)
        item = FilmItem(
            name=response.xpath('//div[@class="title_wrapper"]/h1/text()').get().strip(),
            cates=categories
        )
        yield item

    def parse_categories(self, response):
        cates = response.xpath('//div[@class="see-more inline canwrap"]/a/text()').extract()
        result = []
        for cate in cates:
            if cate.strip() != '' and cate:
                result.append(cate)
        return result

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
