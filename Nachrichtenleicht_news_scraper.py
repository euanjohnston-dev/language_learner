#https://towardsdatascience.com/web-scraping-news-articles-in-python-9dd605799558
#https://towardsdatascience.com/the-complete-guide-for-topics-extraction-in-python-a6aaa6cedbbc


## Deutsch Welle

import requests
from bs4 import BeautifulSoup
import numpy as np
from datetime import datetime
import re
import mysql.connector
import pandas as pd


def get_news():
    # url definition
    url = "https://www.nachrichtenleicht.de/"

    # Request
    r1 = requests.get(url)
    r1.status_code

    # We'll save in coverpage the cover page content
    coverpage = r1.content

    # Soup creation
    soup1 = BeautifulSoup(coverpage, 'html5lib')

    # News identification

    secondary_page = []
    list_links = []
    list_titles = []
    introduction = []
    news_contents = []


    for ul in soup1.find_all('div', class_='dra-lsp-menu'):
        for li in ul.find_all('a'):
            link = url + li['href']
            secondary_page.append(link)
    secondary_page = secondary_page[:-1]


    for n in secondary_page:
        article = requests.get(n)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')
        for ul in  soup_article.find_all('p', class_='dra-lsp-element-headline'):
            for li in ul.find_all('a'):
                sub_link = url + li['href']
                list_links.append(sub_link)



    for n in list_links:
        article = requests.get(n)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')
        title = soup_article.find('div', class_='dra-lsp-artikel-haupttext-headline').get_text()
        list_titles.append(title)
    list_titles = [x.strip('\n              ') for x in list_titles]


    for n in list_links:
        article = requests.get(n)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')
        intro = soup_article.find('div', class_='dra-lsp-artikel-haupttex-kurztext').get_text()
        introduction.append(intro)

    for n in list_links:
        article = requests.get(n)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')
        news_contents_full = soup_article.find('div', class_='dra-lsp-artikel-haupttext-absatz').get_text()
        news_contents_full = re.sub(' +', ' ', news_contents_full)
        news_contents_full = news_contents_full.lstrip()
        news_contents.append(news_contents_full)
        news_contents = [w.replace('\n', ' ') for w in news_contents]
        news_contents = [w.replace('\xa0', '') for w in news_contents]

    add_data(list_titles, news_contents,introduction)


def add_data(list_titles,news_contents,introduction):
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d')

    source = []
    date = []

    i = len(list_titles)

    while i > len(source):
        source.append('Nachrichtenleicht')
        date.append(formatted_date)


    data_entry = list(zip(list_titles,introduction, news_contents,source,date))

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Arsenal-49"
    )

    mycursor = mydb.cursor()

    mycursor.executemany('INSERT INTO new_schema.news_articles (headline,introduction,news_article,source,date_) VALUES (%s,%s,%s,%s,%s)', data_entry)

    mydb.commit()

    data_frame(list_titles,news_contents,introduction,source,date)

def data_frame(list_titles,news_contents,introduction,source,date):

    L = [list_titles,introduction,news_contents,source,date]

    df = pd.DataFrame(L)
    df = df.transpose()

    df.to_csv('scrape_csvs/'+'NRL '+date[0]+'.csv', sep=",")

