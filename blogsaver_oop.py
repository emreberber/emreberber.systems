from bs4 import BeautifulSoup
import urllib2
import re
import requests
import os

'''
title : <title> </title>

./title
    title.html
    .img/
        img_01
        img_02
        ...
'''

class Blog():
	def __init__(self, source_url):
		self.source_url   = source_url

		self.site 	      = 'https://emreberber.systems/'
		response          = urllib2.urlopen(self.source_url)
		self.page_source  = response.read()

		self.source_html  = self.get_between(self.page_source)
		self.title        = self.get_between(self.page_source, '<title>', '|')

		self.create_html()
		self.create_img()


    # Returns between two strings
	@staticmethod
	def get_between(text, first='<section class="col-xs-12">', last='</section>'):
		try:
			start = text.index(first) + len(first)
			end   = text.index(last, start)
			return  text[start:end].strip()
		except ValueError:
			return -1


	# Add related images into the folder named img
	def create_img(self):
		os.mkdir(os.getcwd() +  '/img')
		os.chdir(os.getcwd() + '/img')

		response = requests.get(self.source_url)

		soup     = BeautifulSoup(response.text, 'html.parser')
		img_tags = soup.find_all('img')
		urls     = [img['src'] for img in img_tags]

		for url in urls:
			filename = re.search(r'/([\w_-]+[.](jpg|jpeg|gif|png))$', url)
			with open(filename.group(1), 'wb') as f:
				if 'http' not in url:
					print(url)
					url = '{}{}'.format(self.site, url)
				response = requests.get(url)
				f.write(response.content)


	# Creates a .html file with html codes
	def create_html(self):
		os.mkdir(os.getcwd() + '/' + self.title)
		os.chdir(os.getcwd() + '/' + self.title)

		with open(self.title + '.html', "w") as text_file:
			text_file.write("{0}".format(self.source_html))



if __name__ == '__main__':
	a = Blog('https://emreberber.systems/centos-zabbix-agent-kurulumu-ve-zabbix-host-ekleme/')

