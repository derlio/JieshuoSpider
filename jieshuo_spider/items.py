# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JieshuospiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    category = scrapy.Field()
    detail_url = scrapy.Field()
    image_urls = scrapy.Field()
    image_paths = scrapy.Field()
    desc = scrapy.Field()
    doc_title = scrapy.Field()
    file_urls = scrapy.Field()
    file_paths = scrapy.Field()
    movie_url = scrapy.Field()
