import os
import threading

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait

from logger import logger

logger = logger('Rabota')
"""
Инициализация класса + функция авторизации
"""


class Rabota(threading.Thread):
    def __init__(self, headless=False, download_path=os.getcwd() + '\\download'):
        super().__init__()
        self.chrome_options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_settings.popups': 0,
                 "download.prompt_for_download": False,
                 'download.default_directory': download_path}
        # self.chrome_options.binary_location = "GoogleChromePortable\\GoogleChromePortable.exe"
        self.chrome_options.add_argument('--disable-download-notification')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_experimental_option('prefs', prefs)
        self.chrome_options.headless = headless
        self.driver = webdriver.Chrome(options=self.chrome_options, executable_path='chromedriver.exe')

        # self.opts = webdriver.FirefoxOptions()
        # self.opts.headless = headless
        # self.opts.set_preference("browser.download.folderList", 2)
        # self.opts.set_preference("browser.download.dir", download_path)
        # self.opts.set_preference("browser.download.useDownloadDir", True)
        # self.opts.set_preference("pdfjs.disabled", True)
        # self.opts.set_preference("browser.helperApps.neverAsk.saveToDisk", 'application/RTF,application/pdf')
        # self.driver = webdriver.Firefox(firefox_binary=r'C:\Users\KIEV-COP-4\AppData\Local\Mozilla Firefox\firefox.exe',
        #                                 options=self.opts)

    def authorisation(self, login, password):
        logger.info(f'Авторизация {login}:{password}')
        url = 'https://rabota.ua/employer/login'
        self.driver.get(url)
        self.driver.set_page_load_timeout(45)
        if self.driver.execute_script('return document.readyState;') == 'complete':
            login_xpath = '//input[@class="txtName"]'
            try:
                WebDriverWait(self.driver, 40).until(lambda d: self.driver.find_element_by_xpath(login_xpath))
            except Exception as error:
                logger.critical(error, exc_info=True)
                return False
            self.driver.find_element_by_xpath(login_xpath).send_keys(login)
            password_xpath = '//input[@class="txtPassword"]'

            self.driver.find_element_by_xpath(password_xpath).send_keys(password)

            entrance = '//a[text()="Вход"]'
            self.driver.find_element_by_xpath(entrance).click()
            try:
                assert 'Неправильный логин или пароль' not in self.driver.page_source  # fixme
                return True
            except AssertionError as error:
                logger.exception(error)
                return False

    def end(self):
        self.driver.quit()

    def test(self):
        self.driver.execute_script("window.open('');")
        self.driver.switch_to.window(self.driver.window_handles[-1])
