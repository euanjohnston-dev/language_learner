## Deutsch Welle

import requests
from bs4 import BeautifulSoup
import numpy as np
from datetime import datetime
import re
import pandas as pd

def get_news():
    # url definition
    url = "https://www.dw.com/de/themen/s-9077"

    # Request
    r1 = requests.get(url)
    r1.status_code

    # We'll save in coverpage the cover page content
    coverpage = r1.content

    # Soup creation
    soup1 = BeautifulSoup(coverpage, 'html5lib')

    # News identification
    coverpage_news = soup1.find_all('div', class_='news')


    number_of_articles = 10

    # Empty lists for content, links and titles
    news_contents = []
    introduction = []
    list_links = []
    list_titles = []


    for n in np.arange(0, number_of_articles):
        # Getting the link of the article
        link = url + coverpage_news[n].find('a')['href']
        list_links.append(link)
        # Getting the title
        title = coverpage_news[n].find('h2').get_text()
        list_titles.append(title)
        # Reading the content (it is divided in paragraphs)
        article = requests.get(link)
        article_content = article.content
        soup_article = BeautifulSoup(article_content, 'html5lib')

        intro = list(soup_article.find('p', class_="intro"))
        for element in intro:
            introduction.append(element.strip())
        try:
            body = soup_article.find('div', class_="longText").findAll('p')
        except:
            body = []


        list_paragraphs = []
        #print(body)
        if len(body) > 1:
            for p in np.arange(0, len(body)):
                paragraph = body[p].get_text()
                list_paragraphs.append(paragraph)
                final_article = " ".join(list_paragraphs)
            final_article = re.sub("\\xa0", "", final_article)
            news_contents.append(final_article)
        else:
            news_contents.append('')

    add_data(list_titles, news_contents,introduction)

def add_data(list_titles,news_contents,introduction):
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d')

    source = []
    date = []

    i = len(list_titles)

    while i > len(source):
        source.append('Deutsche_Welle')
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

    df.to_csv('scrape_csvs/'+'DW '+date[0]+'.csv', sep=",")





