import sys
import requests
import bs4
import re
import csv
from datetime import datetime

if (len(sys.argv) == 1):
    raise Exception('Please pass number of pages as an argument')

BASE_URL = 'https://news.ycombinator.com/news?p='
BASE_FILENAME = 'front-'

scraping_articles = []
points = []
comments = []

ranking = 1
max_page = int(sys.argv[1]) 

for num in range(max_page):
    res = requests.get(BASE_URL + str(num + 1))
    page = bs4.BeautifulSoup(res.content, 'lxml')
    articles = page.find_all('a', class_='storylink')
    all_meta_data = page.find_all('td', class_="subtext")

    # Preprocess meta_data and store in list
    for meta_data in all_meta_data:
        s = meta_data.get_text()

        # Extract all numbers
        point = re.search(r'\d+\spoint', s)
        if point is None:
            points.append(0)
        else:
            points.append(point.group().replace(' point', ''))
            
        comment = re.search(r'\d+\scomment', s)
        if comment is None:
            comments.append(0)
        else:
            comments.append(comment.group().replace('\xa0comment', ''))
            
    for article in articles:
        payload = {'ranking': ranking,
        'article': article.get_text(),
        'url': article.get('href'),
        'points': points[ranking - 1],
        'comments': comments[ranking - 1]
        }
        scraping_articles.append(payload)
        ranking += 1

keys = scraping_articles[0].keys()
timestamp = str(datetime.now().strftime('%d-%m-%y %H.%M'))
filename = BASE_FILENAME + timestamp + '.csv'

with open(filename, 'w', encoding='utf-8') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(scraping_articles)
