import time
import scrapy
from selenium import webdriver
from selenium.common import NoSuchElementException
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
        url = "https://www.kobis.or.kr/kobis/business/mast/mvie/searchMovieList.do"
        self.driver.get(url)

        # 페이지 로딩될 때까지 잠시 대기
        time.sleep(1)

        # 크롤링 전 필터링
        def btn_click(btn_xpath):
            btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, btn_xpath))
            )
            btn.click()

        # 검색 필터 '더보기' 버튼 클릭
        btn_click('//*[@id="content"]/div[3]/div[2]/a[1]')

        # 제작 상태 '개봉' 필터링
        btn_click('//*[@id="sPrdtStatStr"]')
        btn_click('//*[@id="mul_chk_det0"]')
        btn_click('//*[@id="layerConfirmChk"]')

        # 장르 제외 필터링
        btn_click('//*[@id="sGenreStr"]')
        btn_click('//*[@id="chkAllChkBox"]')

        # 전체 선택한 후 장르 제외
        btn_click('//*[@id="mul_chk_det18"]')
        btn_click('//*[@id="layerConfirmChk"]')

        # 국적1(한국) 선택
        btn_click('// *[ @ id = "sNationStr"]')
        btn_click('//*[@id="mul_chk_det2"]')
        btn_click('//*[@id="layerConfirmChk"]')

        # 국적2(한국) 선택
        btn_click('// *[ @ id = "sRepNationStr"]')
        btn_click('//*[@id="mul_chk_det2"]')
        btn_click('//*[@id="layerConfirmChk"]')

        # 등급 필터링
        btn_click('//*[@id="searchForm"]/div[2]/div[5]/div')
        btn_click('//*[@id="mul_chk_det2"]')
        btn_click('//*[@id="mul_chk_det3"]')
        btn_click('//*[@id="mul_chk_det4"]')
        btn_click('//*[@id="mul_chk_det5"]')
        btn_click('//*[@id="layerConfirmChk"]')

        # 영화 종류 필터링
        btn_click('//*[@id="sNomal"]')

        time.sleep(1)

        # 크롤링 시작
        # 페이지 순회
        page_numbers = self.driver.find_elements(By.XPATH, '//*[@id="pagingForm"]/div/ul/li')
        for num, row in enumerate(page_numbers, start=1):
            page_number_xpath = f'//*[@id="pagingForm"]/div/ul/li[{num}]'

            page_number_link = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, page_number_xpath))
            )
            page_number_link.click()

            # 페이지 로딩 대기
            time.sleep(2)

            # 각 페이지 테이블 내용 순회
            movie_rows = self.driver.find_elements(By.XPATH, '//*[@id="content"]/div[4]/table/tbody/tr')
            for idx, row in enumerate(movie_rows, start=1):
                movie_detail_xpath = f'//*[@id="content"]/div[4]/table/tbody/tr[{idx}]/td[1]/span/a'

                movie_detail_link = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, movie_detail_xpath))
                )
                movie_detail_link.click()

                title_xpath = '/html/body/div[3]/div[1]/div[1]/div/strong'
                title = self.driver.find_element(By.XPATH, title_xpath).text

                synopsis_xpath = '/html/body/div[3]/div[2]/div/div[1]/div[5]/p'
                try:
                    synopsis = self.driver.find_element(By.XPATH, synopsis_xpath).text
                except NoSuchElementException:
                    # 시놉시스가 없는 경우 빈 문자열로 설정
                    synopsis = ''

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
