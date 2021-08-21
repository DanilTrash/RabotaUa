from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

import rabota
from logger import logger

logger = logger('rabota_parser')


"""
Парсит базу резюме
"""


class Parser(rabota.Rabota):
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
                    logger.warning(e)
                page += 1
        self.driver.quit()


def main():
    headless = True
    parser = Parser(headless)
    password = '25091992Awdx'
    login = 'migashko.lena@yandex.ua'
    parser.authorisation(login, password)
    parser.parsing()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.critical(e, exc_info=True)

