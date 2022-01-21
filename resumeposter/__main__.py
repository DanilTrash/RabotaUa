import os
from onesec_api import Mailbox
from logger import logger
from resumeposter import Poster

LOGGER = logger('resume_poster')


def main():
    while True:
        poster = Poster()
        mail = Mailbox()
        phone_number = '961439104'
        city = 'Киев'
        wanted_position = 'ОПератор колл центра'
        first_name = 'Ольга'
        second_name = 'Куриеенко'
        skills = 'Работа с холодной базой\nПоказатель отдела продаж вырос на 15%\nбассейная 2 не звонить'
        image_path = rf'{os.getcwd()}\image.png'
        poster.first_page(str(mail), phone_number, city, wanted_position, first_name, second_name)
        poster.second_page(skills, image_path)


try:
    if __name__ == '__main__':
        main()
except Exception as e:
    LOGGER.critical(e, exc_info=True)
