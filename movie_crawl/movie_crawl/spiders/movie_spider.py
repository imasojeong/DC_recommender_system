import scrapy
from scrapy_splash import SplashRequest


class MovieSpider(scrapy.Spider):
    name = "movie"
    allowed_domains = ["kobis.or.kr"]
    start_urls = ["https://www.kobis.or.kr/kobis/business/mast/mvie/searchMovieList.do"]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='render.html', args={'wait': 0.5})

    def parse(self, response):
        movie_list = response.css('#content > div.rst_sch > table > tbody')

        # 테이블의 각 행에 대한 반복
        for i in range(1, 10):
            relative_link = movie_list.css(f'tr:nth-child({i}) > td:nth-child(1) > span > a::attr(href)').get()

            # 상대 경로를 절대 경로로 변환
            link = response.urljoin(relative_link)

            script = f"""
                function main(splash)
                    splash:go('{link}')
                    splash:wait(0.5)  -- Adjust the wait time as needed

                    -- Additional Lua script for handling the popup
                    -- For example, click on an element to open the popup

                    return {{
                        html = splash:html(),
                        url = splash:url(),
                    }}
                end
            """

            yield SplashRequest(url=response.url, callback=self.parse_detail, endpoint='execute', args={'lua_source': script, 'wait': 0.5, 'timeout': 90})

    def parse_detail(self, response):
        title = response.css('div.ui-dialog-titlebar > div > div > strong::text').get()
        synopsis = response.css('#ui-id-1 > div > div.item_tab.basic > div:nth-child(5) > p::text').get()

        if title and synopsis:
            item = {
                'title': title.strip(),
                'synopsis': synopsis.strip(),
            }

            print("title: " + title)
            print("synopsis: " + synopsis)

            yield item
