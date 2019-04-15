# 
#   Post Saver for Coder Ghost Theme
#   written by Emre Berber
#
#   emreberber.systems
#   github.com/emreberber
# 

import urllib2
import re
import requests
from bs4 import BeautifulSoup
import os


def get_between(s, first, last):
    try:
        start = s.index(first) + len(first)
        end   = s.index(last, start)
        return  s[start:end].strip()
    except ValueError:
        return -1


source_url  = 'https://emreberber.systems/ubuntu-server-16-04-jira-kurulumu/'
response    = urllib2.urlopen(source_url)
page_source = response.read()

source_html = get_between(page_source, '<section class="col-xs-12">', '</section>')
title       = get_between(page_source, '<title>', '|')


os.mkdir(os.getcwd() + '/' + title)
os.mkdir(os.getcwd() + '/' + title + '/img')

# cd ./title
os.chdir(os.getcwd() + '/' + title)

# write source_html code into the .html file
with open(title + '.html', "w") as text_file:
    text_file.write("{0}".format(source_html))

# cd ./img
os.chdir(os.getcwd() + '/img')

response = requests.get(source_url)

soup     = BeautifulSoup(response.text, 'html.parser')
img_tags = soup.find_all('img')
urls     = [img['src'] for img in img_tags]

# save images into img folder
for url in urls:
    filename = re.search(r'/([\w_-]+[.](jpg|jpeg|gif|png))$', url)
    with open(filename.group(1), 'wb') as f:
        if 'http' not in url:
            print(url)
            url = '{}{}'.format('https://emreberber.systems/', url)
        response = requests.get(url)
        f.write(response.content)
