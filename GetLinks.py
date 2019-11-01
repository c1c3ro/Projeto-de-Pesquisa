from bs4 import BeautifulSoup
from urllib.request import urlopen
from datetime import timedelta, date
import re
import os
import json

k = 1
info = {}
url = 'https://g1.globo.com/busca/?q=meu+bairro+na+tv'
g1 = 'https://globoplay.globo.com/v/'
n = int(input("Digite o numero de paginas: "))
for i in range(1, n+1):
	j = 0
	print('Pegando informacoes da pagina ' + str(i))
	if (i != 1):
		url = url + '&page=' + str(i)
	html_page = urlopen(url)
	soup = BeautifulSoup(html_page, 'html.parser')
	links = soup.find_all('div', class_="widget--info__media-container")
	titles = soup.find_all('div',class_="widget--info__title product-color")
	dates = soup.find_all('div',class_="widget--info__meta")
	for link in links:        
		title = titles[j].text
		title = title.strip()
		if ((title.upper().find("MEU BAIRRO NA TV")) < 0):
			j += 1
			continue
		link = link.find('a').get('href')
		index = link.find('%2Fv%2')
		link = g1 + link[index+7:index+14]
		date1 = dates[j].text
		if(date1.find("dia") > 0):
			t1 = int(''.join(filter(str.isdigit, date1)))
			date1 = date.today() - timedelta(days = t1)
			date1 = date1.strftime("%d/%m/%Y")
		if(date1.find("hora") > 0):
			date1 = date.today()
			date1 = date1.strftime("%d/%m/%Y")
		info['video ' + str(k)] = {
			'titulo': title,
			'link': link,
            'data': date1
            }
		j += 1
		k += 1

with open('videosInfo.json', 'a') as outfile:
	json.dump(info, outfile, ensure_ascii=False)



