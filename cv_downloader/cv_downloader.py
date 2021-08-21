from time import sleep
import os
from io import BytesIO

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from threading import Thread
import rabota
from logger import logger

LOGGER = logger('CvDownloader')


class CvDownloader(rabota.Rabota, Thread):
    def __init__(self,
                 headless=False,
                 download_path=os.getcwd() + '\\download',
                 login=None,
                 password=None,
                 cv_urls=None,
                 bot=None,
                 user=None):
        super().__init__(download_path=download_path, headless=headless)
        self.login = login
        self.password = password

        self.user = user
        self.bot = bot

        self.cv_urls = cv_urls
        self.path = download_path

    def download(self):
        # todo отправка резюме больше 1
        for cv_url in self.cv_urls:
            LOGGER.info(cv_url)
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get(cv_url)
            download_button_xpath = '//*[text()="Скачать"]'
            try:
                # fixme check wait
                download_button_element = WebDriverWait(self.driver, 20).until(
                    lambda f: self.driver.find_element(By.XPATH, download_button_xpath))
                download_button_element.click()
            except Exception as error:
                LOGGER.debug(error, exc_info=True)
                breakpoint()

    def check_downloads(self):
        # self.driver.execute_script("window.open('');")
        # self.driver.switch_to.window(self.driver.window_handles[-1])
        # self.driver.get("chrome://downloads")
        while True:
            try:
                if len(os.listdir(self.path)) == len(self.cv_urls):
                    return True
            except FileNotFoundError:
                sleep(1)
                pass

    def send(self):
        for resume in os.listdir(self.path):
            with open(f'{self.path}\\{resume}', 'rb') as misc:  # fixme FileNotFoundError
                file = BytesIO(misc.read())
                file.name = resume
            self.bot.send_document(self.user.id, file)
