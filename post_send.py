import requests
import random
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

def create(category='Отказ оборудования или связи (включая интернет)', name='Бот', priority="medium", number_kab="120",
           number_phone='8777000888',
           korpus='Главный корпус',
           theme='Был перезапуск бота', msg='Перезапуск бота'):
    if 'Отказ оборудования или связи (включая интернет)' in category:
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

#    ua = UserAgent()
#    header = {'User-Agent': ua.chrome}
    url = 'http://hesk.gp1.loc/submit_ticket.php?submit=' + str(category_send)
    send = requests.post(url, data=data).text
    soup = BeautifulSoup(send, 'lxml')
    block = soup.find('div').findAll('span')[2].text
    print(block)
    print("Произошла отправка заявки")
    return block



if __name__ == '__main__':
    create()
