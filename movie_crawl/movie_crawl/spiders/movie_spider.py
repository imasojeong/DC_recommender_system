from pathlib import Path

import scrapy
import time


class MovieSpider(scrapy.Spider):
    name = "movie"

    def start_requests(self):
        urls = [
            "https://www.melon.com/chart/",
            "https://www.melon.com/chart/hot100/",
            "https://www.melon.com/chart/day/",
            "https://www.melon.com/chart/week/",
            "https://www.melon.com/chart/month/",
        ]
        num_documents = 0
        start_time = time.time()
        # 페이지 순회
        for url in urls:
            num_documents += 1
            yield scrapy.Request(url=url, callback=self.parse, meta={'site': url})
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"수집된 문서 수 : {num_documents}")
        print(f"수집하는 데 걸린 시간 : {elapsed_time} seconds")

    def parse(self, response):
        site_name = response.meta.get('site', '').split('/')[-2]

        music_sels_50 = response.css('tbody > tr.lst50')
        music_sels_100 = response.css('tbody > tr.lst100')

        # 50위 곡 정보 저장
        for music_sel in music_sels_50:
            item = {
                'site': site_name,
                'rank': music_sel.css('span.rank::text').get(),
                'title': music_sel.css('div.ellipsis.rank01 > span > a::text').get(),
                'artist': music_sel.css('div.ellipsis.rank02 > span > a::text').get()
            }
            yield item

        # 100위 곡 정보 저장
        for music_sel in music_sels_100:
            item = {
                'site': site_name,
                'rank': music_sel.css('span.rank::text').get(),
                'title': music_sel.css('div.ellipsis.rank01 > span > a::text').get(),
                'artist': music_sel.css('div.ellipsis.rank02 > span > a::text').get()
            }
            yield item