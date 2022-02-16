# http://hesk.gp1.loc/admin/change_status.php?s=3&track=номер_заявки&token=генерируемый_токен
'''
    Модуль для закрытия заявок
'''
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def close_request(request_track, login, password):
    try:
        session = requests.Session()

        data_login = {
            'user': login,
            'pass': password,
            'remember_user': 'NOTHANKS',
            'a': 'do_login',
        }

        ua = UserAgent()
        header = {'User-Agent': ua.random}
        url_auth = 'http://hesk.gp1.loc/admin/index.php'
        send_login = session.post(url_auth, data=data_login, headers=header).text
        soup = BeautifulSoup(send_login, 'lxml')
        block = soup.find('section').findAll('a')[1]
        token = str(block)[38:78]

        data_send = {
            's': '3',
            'track': str(request_track),
            'token': str(token),
        }

        url_close_request = 'http://hesk.gp1.loc/admin/change_status.php'
        send_request = session.post(url_close_request, data=data_send).text
        session.close()
        return "Заявка была закрыта"
    except Exception as e:
        return "Ошибка закрытия заявки: " + e
# http://hesk.gp1.loc/admin/change_status.php?s=3&track=29Z-VV7-E145&token=12e7ff72af283b3ba13935ae1a65f985400298d9


if __name__ == '__main__':
    close_request('', '', '')

