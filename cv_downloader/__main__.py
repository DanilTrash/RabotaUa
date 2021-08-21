import os
import re
from shutil import rmtree
from time import sleep
import argparse

import pandas as pd
import telebot
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from telebot import types

from rabota import Rabota
from cv_downloader import CvDownloader
from logger import logger
LOGGER = logger('CvCollector')


class CvCollector(Rabota):
    def __init__(self, headless=False):
        super().__init__(headless)

    def collect_vacancies(self):
        vacancies_urls = []
        vacancie_name = []
        self.driver.set_page_load_timeout(45)
        if self.driver.execute_script('return document.readyState;') == 'complete':
            try:
                vacancies_xpath = '//employer-vacancies-vacancy-item/a'
                vacancies_list = WebDriverWait(self.driver, 10).until(
                    lambda d: self.driver.find_elements(By.XPATH, vacancies_xpath))
                sleep(3)
                for vacancie in vacancies_list:
                    var = vacancie.location_once_scrolled_into_view
                    vacancie_text_split = vacancie.text.split('\n')
                    for text in vacancie_text_split:
                        if re.search('новый|новых', text):
                            vacancie_name.append(vacancie_text_split[0])
                            vacancies_urls.append(vacancie.get_attribute('href'))
                return vacancies_urls, vacancie_name
            except Exception as error:
                LOGGER.debug(error, exc_info=True)
                return [], []

    def check_applies(self, url):
        appliences_urls = []
        self.driver.get(url)
        self.driver.set_page_load_timeout(45)
        if self.driver.execute_script('return document.readyState;') == 'complete':
            try:
                employer_applies_list_xpath = '//employer-applies-list-item/div/a'
                employer_applies_list = WebDriverWait(self.driver, 10).until(
                    lambda d: self.driver.find_elements(By.XPATH, employer_applies_list_xpath))
                for cv in employer_applies_list:
                    var = cv.location_once_scrolled_into_view
                    cv_text_split = cv.text.split('\n')
                    for var in cv_text_split:
                        if re.search('Непросмотренный', var):
                            appliences_urls.append(cv.get_attribute('href'))
                            LOGGER.info(cv_text_split)
                return appliences_urls
            except Exception as error:
                LOGGER.debug(error, exc_info=True)
                return []


TOKEN = "1818693422:AAEPTlql6dsAQs-1czDk_0U7koHe0C38x6E"
bot = telebot.TeleBot(TOKEN, parse_mode=None)
parser = argparse.ArgumentParser()
headless = True

parser.add_argument("--headless", dest="headless", default=headless, help='Используй для режима без браузера',
                    type=bool)
args = parser.parse_args()


@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    logger('TgBot').info(user.first_name)
    keyboard = types.InlineKeyboardMarkup()
    start = types.InlineKeyboardButton(text='Запустить?', callback_data='start')
    keyboard.add(start)
    bot.send_message(chat_id=user.id, text=f"Привет {user.first_name}", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    user = call.from_user
    bot.send_message(chat_id=user.id, text=f'Компании проверяются')
    try:
        df = pd.read_csv('https://docs.google.com/spreadsheets/d/1rRSGmvwnPjrV5QhcX7X-BI8SL7U7RM5znb7y9a81EgI/'
                         'export?format=csv&id=1rRSGmvwnPjrV5QhcX7X-BI8SL7U7RM5znb7y9a81EgI&gid=128190461')
        login = df['login'].dropna().tolist()
        password = df['password'].dropna().tolist()
        companys = df['company'].dropna().tolist()
        for index, company in enumerate(companys):
            bot.send_message(user.id, f'*{company}*', parse_mode='Markdown')
            LOGGER.info(company)
            cv_collector = CvCollector(args.headless)
            if cv_collector.authorisation(login=login[index], password=password[index]):
                vacancies_urls, vacancie_name = cv_collector.collect_vacancies()
                if not vacancies_urls:
                    LOGGER.info('Нет новых откликов')
                    bot.send_message(user.id, 'Нет новых откликов', parse_mode='Markdown')
                    cv_collector.end()
                    continue
                for i, url in enumerate(vacancies_urls):
                    cv_urls = cv_collector.check_applies(url)
                    if len(cv_urls) == 1:
                        msg = 'новый'
                    else:
                        msg = 'новых'
                    bot.send_message(user.id, f'В {vacancie_name[i]} {len(cv_urls)} \n{msg}',
                                     parse_mode='Markdown')
                    download_path = f'{os.getcwd()}\\download\\{company}\\{vacancie_name[i]}'
                    downloader = CvDownloader(headless=args.headless,
                                                 bot=bot,
                                                 user=user,
                                                 download_path=download_path,
                                                 cv_urls=cv_urls)
                    downloader.authorisation(login[index], password[index])
                    downloader.download()
                    downloader.check_downloads()
                    sleep(5)  # fixme
                    LOGGER.info('Sending resumes')
                    downloader.send()
                    downloader.end()
                cv_collector.end()
        bot.send_message(user.id, 'Готово!')
        LOGGER.info('Deleting downloads')
        os.system(f'Xcopy /E /I download sended')
        for directory in os.listdir('download'):
            rmtree(f'download\\{directory}')
    except Exception as error:
        LOGGER.exception(error)


bot.infinity_polling()
