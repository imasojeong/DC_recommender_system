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
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        self.driver = webdriver.Chrome(options=options)

    def parse(self, response, **kwargs):
        url = "https://www.kobis.or.kr/kobis/business/mast/mvie/searchMovieList.do"
        self.driver.get(url)

        # 페이지 로딩될 때까지 잠시 대기
        time.sleep(1)

        # 크롤링 전 필터링
        def click_btn(xpath):
            btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            btn.click()

        def load_item(xpath):
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )

        # 검색 필터 '더보기' 버튼 클릭
        click_btn('//*[@id="content"]/div[3]/div[2]/a[1]')

        # 제작 상태 '개봉' 필터링
        click_btn('//*[@id="sPrdtStatStr"]')
        click_btn('//*[@id="mul_chk_det0"]')
        click_btn('//*[@id="layerConfirmChk"]')
        time.sleep(1)

        # 장르 제외 필터링
        click_btn('//*[@id="sGenreStr"]')
        load_item('//*[@id="tblChk"]')
        click_btn('//*[@id="chkAllChkBox"]')
        time.sleep(1)
        click_btn('//*[@id="mul_chk_det18"]')
        click_btn('//*[@id="mul_chk_det19"]')
        click_btn('//*[@id="mul_chk_det20"]')
        time.sleep(1)
        click_btn('//*[@id="layerConfirmChk"]')
        time.sleep(1)

        # 국적1(한국) 선택
        click_btn('//*[@id="sNationStr"]')
        load_item('//*[@id="tblChk"]')
        time.sleep(1)
        click_btn('//*[@id="mul_chk_det2"]')
        time.sleep(1)
        click_btn('//*[@id="layerConfirmChk"]')
        time.sleep(1)

        # 국적2(한국) 선택
        click_btn('//*[@id ="sRepNationStr"]')
        load_item('//*[@id="tblChk"]')
        time.sleep(1)
        click_btn('//*[@id="mul_chk_det2"]')
        time.sleep(1)
        click_btn('//*[@id="layerConfirmChk"]')
        time.sleep(1)

        # 등급 필터링
        # click_btn('//*[@id="sGradeStr"]')
        # load_item('//*[@id="tblChk"]')
        # time.sleep(1)
        # click_btn('//*[@id="mul_chk_det2"]')
        # click_btn('//*[@id="mul_chk_det3"]')
        # click_btn('//*[@id="mul_chk_det4"]')
        # click_btn('//*[@id="mul_chk_det5"]')
        # time.sleep(1)
        # click_btn('//*[@id="layerConfirmChk"]')
        # time.sleep(1)

        # 영화 종류 필터링
        click_btn('//*[@id="searchForm"]/div[2]/div[8]/div/label[2]')
        click_btn('//*[@id="searchForm"]/div[2]/div[8]/div/label[3]')
        time.sleep(1)

        # 필터링 후 검색
        click_btn('//*[@id="searchForm"]/div[1]/div[5]/button[1]')
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
