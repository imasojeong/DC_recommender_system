from scrapy.exporters import CsvItemExporter


# pipelines.py

from itemadapter import ItemAdapter
import csv

class CsvPipeline:
    def __init__(self):
        self.file = open("output/movie.csv", 'w', newline='', encoding='utf-8')
        self.writer = csv.writer(self.file)
        self.writer.writerow(['Title', 'Synopsis'])  # CSV 파일의 헤더

    def process_item(self, item, spider):
        title = item.get('title')
        synopsis = item.get('synopsis')

        self.writer.writerow([title, synopsis])

        return item

    def close_spider(self, spider):
        self.file.close()

