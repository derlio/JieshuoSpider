import logging

import scrapy
from scrapy import Request, FormRequest
from ..items import JieshuospiderItem


class MySpider(scrapy.Spider):
    name = "jieshuo"
    allowed_domains = ['678gwy.com']
    start_urls = ['http://www.678gwy.com/ysjs']
    # start_urls = ['http://www.678gwy.com/ysjs/page/90']


    def start_requests(self):
        return [Request("http://www.678gwy.com/wp-login.php",
                        meta={'cookiejar': 1}, callback=self.post_login)]

    post_headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8,en;q=0.6",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 "
                      "Safari/537.36",
        "Referer": "www.678gwy.com/",
    }

    def post_login(self, response):
        return [FormRequest.from_response(response,
                                          url='http://www.678gwy.com/wp-login.php',
                                          meta={'cookiejar': response.meta['cookiejar']},
                                          headers=self.post_headers,  # 注意此处的headers
                                          formdata={
                                              'log': 'donix',
                                              'pwd': 'Mxy8ZmC4XxH9Fq',
                                          },
                                          callback=self.after_login,
                                          dont_filter=True
                                          )]

    def after_login(self, response):
        for url in self.start_urls:
            yield Request(url, meta={'cookiejar': response.meta['cookiejar']})

    def parse(self, response, **kwargs):
        for each in response.xpath('//header[contains(@class, "entry-header")]'):
            # 分类
            categories = each.xpath('./div/span/a/text()')
            category = ''
            for c in categories:
                if c.extract() != '影视解说':
                    category = c.extract()
                    break

            title = each.xpath('./h2/a/text()').extract_first()
            detail_url = each.xpath('./h2/a/@href').extract_first()

            item = JieshuospiderItem()
            item['category'] = category
            item['detail_url'] = detail_url
            item['title'] = title

            yield scrapy.Request(url=detail_url, callback=self.detail_parse,
                                 meta={'item': item, 'cookiejar': response.meta['cookiejar']})

        # 进入下一列表页继续
        next_page = response.xpath('//a[contains(@class, "next")]/@href').get()
        if next_page is not None:
            yield scrapy.Request(url=next_page, callback=self.parse, meta={'cookiejar': response.meta['cookiejar']})

    def detail_parse(self, response):
        item = response.meta['item']
        entry_content = response.xpath('//div[contains(@class, "entry-content")]/p')
        desc = ''
        for p in entry_content:
            # 第一个p是图片
            image_url = p.xpath('./img/@data-srcset').get()
            if image_url is None:
                image_url = p.xpath('./a/img/@data-srcset').get()
            if image_url is not None:
                item['image_urls'] = [image_url]

            # 文案描述
            line = p.xpath('./text()').extract_first()
            if line is not None:
                desc += line + '\n'
            item['desc'] = desc

        # 隐藏部分
        hide_content = response.xpath('//div[contains(@class, "content-hide-tips")]')
        doc_title = hide_content.xpath('./p/a/text()').get()
        if doc_title is None:
            doc_title = hide_content.xpath('./a/text()').get()

        doc_url = hide_content.xpath('./p/a/@href').get()
        if doc_url is None:
            doc_url = hide_content.xpath('./a/@href').get()
        item['doc_title'] = doc_title
        item['file_urls'] = [doc_url]

        # 电影下载地址
        movie_url = hide_content.xpath('./div[@id="ztxt"]/div/text()').get()
        if movie_url is None:
            # 需要暴力去找
            all_p = hide_content.xpath('p')
            for p in all_p:
                temp = p.xpath('./text()').get()
                if temp is not None and ('thunder://' in temp or 'magnet:?xt' in temp or 'ed2k://' in temp):
                    movie_url = temp
                    break

        item['movie_url'] = movie_url

        yield item
