import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


def get_send():
    ua = UserAgent()
    header = {'User-Agent': ua.random}
    url = 'https://rp5.kz/%D0%9F%D0%BE%D0%B3%D0%BE%D0%B4%D0%B0_%D0%B2_%D0%A2%D0%B5%D0%BC%D0%B8%D1%80%D1' \
          '%82%D0%B0%D1%83,_%D0%9A%D0%B0%D0%B7%D0%B0%D1%85%D1%81%D1%82%D0%B0%D0%BD'
    send = requests.get(url, headers=header).text
    soup = BeautifulSoup(send, 'lxml')
    try:
        block = soup.find('div', id='archiveString')
        now = block.find('div', id='ArchTemp').text[0:4].strip()
        felt = block.find('div', 'TempStr').text[0:4].strip()
        msg = block.find('a', 'ArchiveStrLink').text.replace('Архив погоды на метеостанции', '').strip()
        data = {
            'now': now,
            'felt': felt,
            'msg': msg,
        }
        return data
    except IndexError as e:
        return 'Информация недоступна'



if __name__ == '__main__':
    get_send()
