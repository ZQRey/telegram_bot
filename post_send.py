import requests
import random
from fake_useragent import UserAgent


def create(category='Консультация и обучение', name='test', priority="medium", number_kab="120",
           number_phone='8777000888',
           korpus='Главный корпус',
           theme='Проблема', msg='Что то случилось'):
    if 'Отказ оборудования или связи' in category:
        category_send = 15
    elif 'Учетные записи, роли, логины и пароли' in category:
        category_send = 4
    elif 'Консультация и обучение' in category:
        category_send = 5
    else:
        category_send = 1

    num = '0123456789'
    buk = 'qwertyuioplkjhgfdsazxcvbnm'
    token = ''
    for i in range(0, 20):
        token += random.choice(num) + random.choice(buk)

    data = {
        'name': name,
        'email': 'email@mail.ru',
        'priority': priority,
        'custom1': number_kab,
        'custom3': number_phone,
        'custom2': korpus,
        'custom4': '',
        'subject': theme,
        'message': msg,
        'attachment[1]': '(двоичный)',
        'attachment[2]': '(двоичный)',
        'token': token,
        'category': category_send,
        'hx': 3,
        'hy': '',
    }

    send(data)


def send(datas):
    ua = UserAgent()
    header = {'User-Agent': ua.chrome}
    url = 'http://hesk.gp1.loc/submit_ticket.php?submit=1'
    send = requests.post(url, data=datas, headers=header)
    print(send.status_code)


create()
