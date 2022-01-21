import os
import re
import shutil
from io import BytesIO
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from logger import logger

LOGGER = logger('Rabota')


class Rabota:
    def __init__(self, headless=False, tg_bot=None, user=None):
        self.tg_bot = tg_bot
        self.user = user
        self.download_path = os.getcwd() + '\\download'
        self.chrome_options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_settings.popups': 0,
                 "download.prompt_for_download": False,
                 'download.default_directory': self.download_path}
        self.chrome_options.add_argument('--disable-download-notification')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.chrome_options.add_experimental_option('prefs', prefs)
        self.chrome_options.headless = headless
        self.driver = webdriver.Chrome(options=self.chrome_options)

    def parsing(self):
        boys = (
            'https://rabota.ua/candidates/all/%D0%BA%D0%B8%D0%B5%D0%B2?period=%22Today%22&gender=%2'
            '2Male%22&age=%7B%22from%22%3A18%2C%22to%22%3A25%7D&salary=%7B%22from%22%3Anull%2C%22to%22%3A16000%7'
            'D&moveability=false&scheduleIds=%5B%221%22%5D'
        )
        girls = (
            'https://rabota.ua/candidates/all/%D0%BA%D0%B8%D0%B5%D0%B2?period=%22Today%22&gender=%22Female%22&'
            'age=%7B%22from%22%3A18%2C%22to%22%3A40%7D&salary=%7B%22from%22%3Anull%2C%22to%22%3A16000%7D'
            '&moveability=false&scheduleIds=%5B%221%22%5D'
        )
        for category in [girls, boys]:
            self.driver.get(category)
            page = 1
            while True:
                self.driver.refresh()
                try:
                    if self.driver.execute_script('return document.readyState;') == 'complete':
                        print(f'\n{page}\n')
                        cards = '//alliance-employer-cvdb-cv-list-card'
                        WebDriverWait(self.driver, 40).until(lambda d: self.driver.find_elements_by_xpath(cards))
                        elements = self.driver.find_elements_by_xpath(cards)
                        for element in elements:
                            if element.is_displayed():
                                var = element.location_once_scrolled_into_view
                            try:
                                element.find_element(By.TAG_NAME, 'lib-cv-viewed')
                                continue
                            except NoSuchElementException:
                                pass
                            a = element.find_element_by_tag_name('a')
                            info = [i.text for i in a.find_elements_by_tag_name('p')][:-2]
                            if info[1] == 'Анонимный соискатель':
                                continue
                            if info[3] == 'Готов переехать':
                                continue
                            info.append(a.get_attribute('href'))
                            for i in info:
                                print(i)
                        try:
                            if page == 1:
                                button_next = '//div/nav/santa-pagination/div/div[6]'
                            else:
                                button_next = '//div/nav/santa-pagination/div/div[7]'
                            next_page = self.driver.find_element_by_xpath(button_next)
                            var = next_page.location_once_scrolled_into_view
                            next_page.click()
                        except NoSuchElementException:
                            print('Страницы закончились')
                            break
                except (StaleElementReferenceException, TimeoutException) as e:
                    LOGGER.warning(e)
                page += 1
        self.driver.quit()

    def authorisation(self, login, password):
        LOGGER.info(f'{login} : {password}')
        url = 'https://rabota.ua/employer/login'
        self.driver.get(url)
        try:
            login_xpath = '//input[@class="txtName"]'
            WebDriverWait(self.driver, 15).until(lambda d: self.driver.find_element_by_xpath(login_xpath))
            self.driver.find_element_by_xpath(login_xpath).send_keys(login)
            password_xpath = '//input[@class="txtPassword"]'
            self.driver.find_element_by_xpath(password_xpath).send_keys(password)
            entrance = '//a[text()="Вход"]'
            self.driver.find_element_by_xpath(entrance).click()
            WebDriverWait(self.driver, 15).until_not(
                lambda d: self.driver.find_element_by_xpath(entrance),
                f'Компания не авторизирована')
            WebDriverWait(self.driver, 15).until_not(
                lambda d: 'К сожалению, нам пришлось закрыть вам доступ к блокноту' in self.driver.page_source,
                f'Компания заблокирована')
            return True
        except Exception as error:
            LOGGER.exception(error)
            self.tg_bot.send_message(self.user.id, str(error))
            return False

    def collect_vacancies(self):
        self.driver.get('https://rabota.ua/my/vacancies')
        vacancies_urls = []
        vacancie_names = []
        sleep(2)
        try:
            vacancies_xpath = '//*/employer-vacancies-vacancy-item-desktop'
            vacancies_list = WebDriverWait(self.driver, 15).until(
                lambda d: self.driver.find_elements(By.XPATH, vacancies_xpath))
            for vacancie in vacancies_list:
                vacancie_text_split = vacancie.text.split('\n')
                for text in vacancie_text_split:
                    if re.search('новый|новых', text):
                        vacancies_urls.append(vacancie.find_element(By.TAG_NAME, 'a').get_attribute('href'))
                        LOGGER.info(vacancie_text_split[0])
                        vacancie_names.append(vacancie_text_split[0])
                var = vacancie.location_once_scrolled_into_view
            return vacancies_urls, iter(vacancie_names)
        except Exception as error:
            LOGGER.exception(error)
            self.tg_bot.send_message(self.user.id, str(error))
            return [], []

    def check_applies(self, vacancie_url):
        self.driver.get(vacancie_url)
        appliences_urls = []
        sleep(2)
        try:
            employer_applies_list_xpath = '//*/employer-applies-list-item'
            employer_applies_list = WebDriverWait(self.driver, 20).until(
                lambda d: self.driver.find_elements(By.XPATH, employer_applies_list_xpath))
            for cv in employer_applies_list:
                cv_text_split = cv.text.split('\n')
                for text in cv_text_split:
                    if re.search('Непросмотренный', text):
                        appliences_urls.append(cv.find_element_by_xpath('div/a').get_attribute('href'))
                        LOGGER.info(cv_text_split)
                var = cv.location_once_scrolled_into_view
            return appliences_urls
        except Exception as error:
            LOGGER.exception(error)
            self.tg_bot.send_message(self.user.id, str(error))
            return []

    def download_all(self, cv_url):
        LOGGER.info(cv_url)
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.get(cv_url)
        try:
            filter_button_xpath = '//*/div/div/div/span[3]'
            WebDriverWait(self.driver, 10).until(
                lambda d: self.driver.find_element_by_xpath(filter_button_xpath)).click()
            check_box = '//*/employer-applies-list-item/div/div/santa-checkbox'
            download_button_element = WebDriverWait(self.driver, 20).until(
                lambda f: self.driver.find_element(By.XPATH, check_box))
            download_button_element.click()
        except Exception as error:
            LOGGER.exception(error)

    def download(self, cv_url):
        LOGGER.info(cv_url)
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
        self.driver.get(cv_url)
        result = False
        while result is False:
            try:
                download_button_xpath = '//*[text()="Скачать"]'
                download_button_element = WebDriverWait(self.driver, 20).until(
                    lambda f: self.driver.find_element(By.XPATH, download_button_xpath))
                download_button_element.click()
                sleep(2)
                return True
            except Exception as error:
                LOGGER.exception(error)
                self.tg_bot.send_message(self.user.id, str(error))
                return False

    def send_resume(self):
        listdir = os.listdir(self.download_path)
        for resume in listdir:
            sleep(1)
            try:
                with open(f'{self.download_path}\\{resume}', 'rb') as misc:
                    file = BytesIO(misc.read())
                    file.name = resume
                self.tg_bot.send_document(self.user.id, file)
                shutil.move(f'{self.download_path}\\{resume}', f'sended\\{resume}')
            except FileNotFoundError as error:
                LOGGER.error(error)
