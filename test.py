import requests


class Rabota:
    def __init__(self):
        self.session = requests.Session()

    def get_applies(self):
        req = self.session.get('https://rabota.ua/my/vacancies/8487856/applies')
        return req

    def get_my(self):
        req = self.session.get('https://notebook.rabota.ua/employer/notepad/profile')
        return req

    def auth(self, login, password):
        data = {
            '__EVENTTARGET': "ctl00$content$ZoneLogin$btnLogin",
            '__VIEWSTATE': "9HtDkVA6CZDkkzHgy1ntB+JtU2WxunBE804OJYrDmR7sXaX/rCuXs2DHBKETEKT8OYWpbODCirLGwDb9DctGu/LY/aCr5mpYVuc6Knk9CvJ+FPhFDQTxatheoztlhEukSQBGOM6Yo6J8WYFXl4whxnWz91wQUNJ4kfZfCrdFhRCQtUes3N91mb/S7OeVNHpHCkevV1VQv1i+BnxMUyrXpECmltBDhPcrZh9xMpXjECpt+oYqrlJYo/E9amhj2S+p80evZ3YbL6zs5cJb2olEfg==",
            '__VIEWSTATEGENERATOR': "BFE5824D",
            'ctl00$content$ZoneLogin$txLogin': login,
            'ctl00$content$ZoneLogin$txPassword': password,
            'ctl00$content$ZoneLogin$chBoxRemember': "on",
            'ctl00$Footer$footerLang': "ruLang"
        }
        req = self.session.post('https://rabota.ua/employer/login', data)
        return req

    def download_cv(self):
        req = self.session.get('https://rabota.ua/service/cvexport?resumeId=19225759&vacancyId=8487856&down=1')
        return req


if __name__ == '__main__':
    rabota = Rabota()
    login = 'p.ostmail1231234@gmail.com'
    password = "Zxcasdqwe123"
    rabota.auth(login, password)
    rabota.get_applies()
