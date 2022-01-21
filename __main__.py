import telebot
from telebot import types

from rabota import Rabota
from logger import logger

from data import Data

LOGGER = logger('CvCollector')

bot = telebot.TeleBot(Data.TOKEN, parse_mode=None)


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
    logins = Data('login')
    passwords = Data('password')
    companys = Data('company')
    for company in companys:
        LOGGER.info(company)
        bot.send_message(user.id, f'*{company}*', parse_mode='Markdown')
        headless = True,
        rabota = Rabota(headless=headless, tg_bot=bot, user=user)
        login = next(logins)
        password = next(passwords)
        authorised = rabota.authorisation(login, password)
        if not authorised:
            LOGGER.error(f'{company} не авторизирована')
            rabota.driver.quit()
            continue
        vacancies_urls, vacancie_names = rabota.collect_vacancies()
        if not vacancies_urls:
            LOGGER.info(f'{company} 0 откликов')
            bot.send_message(user.id, f'{company} 0 откликов')
            rabota.driver.quit()
            continue
        for vac_url in vacancies_urls:
            vac_name = next(vacancie_names)
            # rabota.download_all(vac_url)
            # rabota.send_resume()
            cv_urls = rabota.check_applies(vac_url)
            bot.send_message(user.id, f'{vac_name} {len(cv_urls)} резюме', parse_mode='Markdown')
            for cv_url in cv_urls:
                if not rabota.download(cv_url):
                    continue
                rabota.send_resume()
        rabota.driver.quit()
    bot.send_message(user.id, f'Готово!', parse_mode='Markdown')


if __name__ == '__main__':
    bot.infinity_polling()
