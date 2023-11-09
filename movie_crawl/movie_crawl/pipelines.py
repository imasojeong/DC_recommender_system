# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


import os
import csv


class CsvPipeline:
    def __init__(self):
        self.files = None

    def open_spider(self, spider):
        self.files = {}

    def close_spider(self, spider):
        for site_name, (file, writer) in self.files.items():
            file.close()
            current_path = f"{site_name}.csv"
            new_path = os.path.join('output', f"{site_name}.csv")
            os.rename(current_path, new_path)

    def process_item(self, item, spider):
        site_name = item['site']

        if site_name not in self.files:
            self.create_csv_file(site_name)

        file, writer = self.files[site_name]
        writer.writerow([item['rank'], item['title'], item['artist']])

        return item

    def create_csv_file(self, site_name):
        filename = f"{site_name}.csv"
        file = open(filename, 'w', newline='', encoding='utf-8')
        writer = csv.writer(file)
        writer.writerow(['Rank', 'Title', 'Artist'])  # Header

        self.files[site_name] = (file, writer)