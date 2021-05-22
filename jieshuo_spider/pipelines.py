# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
from urllib.parse import urlparse

import scrapy
import json

from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline
from itemadapter import ItemAdapter


class DocPipeline(FilesPipeline):

    def file_path(self, request, response=None, info=None, *, item=None):
        return os.path.join('output/docs', os.path.basename(item['doc_title']) + '.docx')

    def get_media_requests(self, item, info):
        adapter = ItemAdapter(item)
        for file_url in adapter['file_urls']:
            yield scrapy.Request(file_url)

    def item_completed(self, results, item, info):
        file_paths = [x['path'] for ok, x in results if ok]
        if not file_paths:
            raise DropItem("Item contains no files")
        adapter = ItemAdapter(item)
        adapter['file_paths'] = file_paths
        return item


class CoverPipeline(FilesPipeline):

    def file_path(self, request, response=None, info=None, *, item=None):
        return os.path.join('output/images',  os.path.basename(urlparse(request.url).path))

    def get_media_requests(self, item, info):
        for image_url in item['image_urls']:
            yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item


class JsonWriterPipeline:

    def open_spider(self, spider):
        output_path = os.path.join('files', 'output')
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        self.file = open(os.path.join(output_path, 'items.json'), 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

