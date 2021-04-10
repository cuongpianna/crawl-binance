from scrapy import Spider, Request
import re
from datetime import datetime
from html2text import html2text
from demo.items import WelderItem
from scrapy_selenium import SeleniumRequest
import os
import urllib.parse
from urllib.request import urlretrieve
import time

dir_path = os.path.dirname(os.path.realpath(__file__))


class IMDBSpider(Spider):
    name = 'LincolnSpider'
    start_urls = ['https://www.lincolnelectric.com/en/Products/Equipment/Welding-Equipment/MIG-Welding-Equipment',
                  'https://www.lincolnelectric.com/en/Products/Equipment/Welding-Equipment/TIG-Welding-Equipment',
                  'https://www.lincolnelectric.com/en/Products/Equipment/Welding-Equipment/Stick-Welding-Equipment',
                  'https://www.lincolnelectric.com/en/Products/Equipment/Welding-Equipment/Multi-Process-Welding-Equipment',
                  'https://www.lincolnelectric.com/en/Products/Equipment/Welding-Equipment/Engine-Drive-Welding-Equipment',
                  'https://www.lincolnelectric.com/en/Products/Equipment/Welding-Equipment/Advanced-Process-Welders-Welding-Equipment',
                  'https://www.lincolnelectric.com/en/Products/Equipment/Welding-Equipment/Submerged-Arc-Welding-Equipment',
                  'https://www.lincolnelectric.com/en/Products/Equipment/Welding-Equipment/Multioperator-Welding-Equipment'
                  ]

    base_url = 'https://www.lincolnelectric.com/'

    def parse(self, response):
        top_post = response.xpath('//a[@class="card card--product-grid"]/@href')

        for post in top_post:
            url = post.get()
            yield Request(url=url, callback=self.parse_post, meta={'prev_url': response.request.url})

    def parse_post(self, response):
        item = WelderItem(
            name=response.xpath('//h1/text()').get().strip(),
            cate=self.parse_category(response),
            brand='EastWood',
            # sku=response.xpath('//div[@class="product-sku"]/h3/text()').get().strip(),
            # # rate=response.xpath('//*[@class="pr-snippet-rating-decimal"]/text()').get().strip() if response.xpath(
            # #     '//*[@class="pr-snippet-rating-decimal/text()"]') else 0,
            # description=response.xpath('//div[@class="short-description"]/div[@class="std"]/text()').get().strip(),
            # # images=self.parse_images(response),
            # included=self.parse_included(response),
            # detail=response.xpath('//div[@class="well mb-4"]').get(),
            # contents=response.xpath('//div[@class="Contents"]/ul'),
            # # included=self.parse_included(response),
            # specifications=self.parse_specifications(response),
            # global_link=response.request.url

        )
        # yield item

    def parse_specifications(self, response):
        result = dict(

        )
        return result

    def parse_category(self, response):
        cate = response.xpath('//div[@class="breadcrumbs "]//a[5]/text()').get().strip()
        if cate == 'MIG':
            return 'MIG'
        elif cate == 'TIG Welders':
            return 'TIG'
        elif cate == 'Multi-Process':
            return 'Multiprocess'
        elif cate == 'Engine Drive':
            return 'Engine Driven'
        elif cate == 'Stick' or cate == 'Submerged Arc':
            return 'STICK / ARC'
        elif cate == 'Advanced Process Equipment':
            return 'Advanced Process Equipment'
        elif cate == 'Multi-Operator':
            return 'Multi-Operator'

    def parse_images(self, response):
        directory = "images"
        path = os.path.join(dir_path, directory)
        if not os.path.exists(path):
            os.makedirs(path)
        images = response.xpath('//div[@class="more-views"]//img/@src').extract()
        result = []
        for img in images:
            if img:
                image_url = urllib.parse.urljoin(self.base_url, img)
                image_url.replace('mw=70', 'mw=450')
                image_url.replace('mh=70', 'mw=450')
                dt = datetime.now()
                seq = dt.strftime("%Y%m%d%H%M%S")

                img_path = os.path.join(path, seq + '.png')
                urlretrieve(image_url, img_path)
                result.append(seq + '.png')
        return result

    def parse_included(self, response):
        included = response.xpath('//div[@class="included"]/ul//li/text()').extract()
        return included

    def parse_features(self, response):
        features = response.xpath('(//div[@id="tab_content_desc"]//ul[@type="disc"])[last()]/li/b/text()').extract()
        return features
