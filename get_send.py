import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def get_send(request_number):
    ua = UserAgent()
    header = {'User-Agent': ua.random}
    url = 'http://hesk.gp1.loc/ticket.php?track=' + request_number
    send = requests.get(url, headers=header).text
    soup = BeautifulSoup(send, 'lxml')
    block = soup.find('div').find('main').findAll('section')[2].findAll('div')
    answer = soup.find('div').find('main').findAll('p')
    print(len(answer))
    if len(answer) >= 2:
        answer = answer[len(answer)-2].text
    data = {
        'ID': block[3].text,
        'Status': block[9].text,
        'Create': block[15].text,
        'Update': block[18].text,
        'Last_send': block[21].text,
        'answer': answer,
    }
    print(data)
    return data

if __name__ == '__main__':
    get_send('MJS-8TT-9QRA')