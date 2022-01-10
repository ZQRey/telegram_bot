import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


ua = UserAgent()
header = {'User-Agent': ua.random}
url = 'http://hesk.gp1.loc/ticket.php?track=W84-2JT-NUJP'
send = requests.get(url, headers=header).text
soup = BeautifulSoup(send, 'lxml')
block = soup.find('div').find('main').findAll('section')[2].findAll('div')
print('Last_send' + block[31].text)