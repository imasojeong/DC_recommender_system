import time

import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class MovieSpider(scrapy.Spider):
    name = "movie"
    allowed_domains = ["kobis.or.kr"]
    start_urls = ["https://www.kobis.or.kr/kobis/business/mast/mvie/searchMovieList.do"]

    def __init__(self, *args, **kwargs):
        super(MovieSpider, self).__init__(*args, **kwargs)
        self.driver = webdriver.Chrome()

    def parse(self, response):
        # 직접 URL 문자열 사용
        url = "https://www.kobis.or.kr/kobis/business/mast/mvie/searchMovieList.do"
        self.driver.get(url)

        # 페이지가 로딩될 때까지 잠시 대기
        time.sleep(3)

        # 검색 세부사항 더보기 버튼 클릭
        more_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div[3]/div[2]/a[1]'))
        )
        more_btn.click()

        # 제작 상태 모달창 클릭
        production_status_checkbox = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="sPrdtStatStr"]'))
        )
        production_status_checkbox.click()

        # 제작 상태가 '개봉'인 영화만 클릭
        release_checkbox = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="mul_chk_det0"]'))
        )
        release_checkbox.click()

        # 확인 버튼 클릭
        confirm_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="layerConfirmChk"]'))
        )
        confirm_btn.click()

        # 조회 버튼 클릭
        search_btn = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="searchForm"]/div[1]/div[5]/button[1]'))
        )
        search_btn.click()

        # 테이블의 tbody 선택
        # movie_list = response.css('#content > div.rst_sch > table > tbody')

        for i in range(1, 10):
            movie_detail_xpath = f'//*[@id="content"]/div[4]/table/tbody/tr[{i}]/td[1]/span/a'

            movie_datail_link = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, movie_detail_xpath))
            )
            movie_datail_link.click()

            title_xpath = '/html/body/div[3]/div[1]/div[1]/div/strong'
            title = self.driver.find_element(By.XPATH, title_xpath).text

            synopsis_xpath = '/html/body/div[3]/div[2]/div/div[1]/div[5]/p'
            synopsis = self.driver.find_element(By.XPATH, synopsis_xpath).text

            # 모달창 닫기
            close_btn = '/html/body/div[3]/div[1]/div[1]/a[2]'
            self.driver.find_element(By.XPATH, close_btn).click()

            # 가져온 정보를 yield하여 Scrapy 아이템으로 전달
            yield {
                'title': title.strip(),
                'synopsis': synopsis.strip()
            }

    def closed(self, reason):
        self.driver.quit()
