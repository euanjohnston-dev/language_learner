#!/usr/bin/python3
from random import randint

num = randint(1, 5)
from googletrans import Translator
import mysql.connector
import tkinter as tk
import textwrap
from datetime import datetime
import nltk
from HanTa import HanoverTagger as ht
from itertools import chain
import DW_news_scraper as DW
import Nachrichtenleicht_news_scraper as NL

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Arsenal-49"
)

mycursor = mydb.cursor()


class Window():
    def __init__(self, master):
        self.frame = tk.Frame(master)
        self.text = tk.StringVar()
        self.text.set('Click next text to begin your reading')
        self.ranNumLabel = tk.Label(self.frame, textvariable=self.text)
        self.ranNumLabel.grid(row=0)

        # download latest news
        self.download_news_button = tk.Button(self.frame, text='Download todays news', command=self.download_todays_news)
        self.download_news_button.grid(row=6)
        self.frame.grid()



        # percentage of known nouns
        self.text_1 = tk.StringVar()
        self.text_1.set('')
        self.ranNumLabel = tk.Label(self.frame, textvariable=self.text_1)
        self.ranNumLabel.grid(row=1)

        # percentage of previously seen but unknown nouns (checked previously)
        self.text_2 = tk.StringVar()
        self.text_2.set('')
        self.ranNumLabel = tk.Label(self.frame, textvariable=self.text_2)
        self.ranNumLabel.grid(row=2)

        # percentage of unseen nouns
        self.text_3 = tk.StringVar()
        self.text_3.set('')
        self.ranNumLabel = tk.Label(self.frame, textvariable=self.text_3)
        self.ranNumLabel.grid(row=3)

        # Number of pages
        self.text_4 = tk.StringVar()
        self.text_4.set('')
        self.ranNumLabel = tk.Label(self.frame, textvariable=self.text_4)
        self.ranNumLabel.grid(row=4)

        # next button
        self.next_text_button = tk.Button(self.frame, text='Next text', command=self.create_next_page_button)
        self.next_text_button.grid(row=5)
        self.frame.grid()

        # translation object
        self.translation_label = tk.StringVar()
        self.translation_label.set('')
        self.translation_label_1 = tk.Label(self.frame, textvariable=self.translation_label)
        self.translation_label_1.grid(row=50)

        self.buttonList_object = []
        self.button_list = []
        self.vars = []
        self.translationList = []
        # known words
        self.save_to_db_known = []
        # unkown words
        self.save_to_db_unknown = []
        # all words from shown text
        self.new_list = []
        # declare global variable
        self.number_of_iterating_pages = 0


    # code incorporating import of scrape scripts for NL and DW.

    def download_todays_news(self):
        if self.download_news_button.winfo_exists() == 1:
            self.download_news_button.destroy()

        def copy_legacy_news():

            mycursor.execute('''INSERT INTO new_schema.news_articles_old
                            SELECT *
                            FROM new_schema.news_articles''')
            mydb.commit()
            print('y')

        def clear_news_table():

            mycursor.execute('''DELETE FROM new_schema.news_articles''')
            mydb.commit()

        def fetch_latest_news_date():
            mycursor.execute("""SELECT date_
                                FROM new_schema.news_articles
                                limit 1;""")
            records = mycursor.fetchall()
            for row in records:
                x = row[0]
            now = datetime.now()

            if str(x) == str(now.strftime('%Y-%m-%d')):
                print('already downloaded')
            else:
                copy_legacy_news()
                clear_news_table()
                DW.get_news()
                NL.get_news()

        fetch_latest_news_date()

    def create_next_page_button(self):
        if self.download_news_button.winfo_exists() == 1:
            self.download_news_button.destroy()

        self.next_text_button_1 = tk.Button(self.frame, text='next page', command=self.initiate)
        self.next_text_button_1.grid(row=6)
        self.frame.grid()
        self.initiate()

    def initiate(self):
        self.translation_label.set('')
        if len(self.save_to_db_known) == 0 and len(self.save_to_db_unknown) == 0 and len(self.new_list) >= 1:
            self.save_to_db_known = self.new_list
            self.add_data()

        elif len(self.save_to_db_known) > 0 or len(self.save_to_db_unknown) > 0:
            self.add_data()
        else:
            self.remove_data_from_temp_table()

    def add_data(self):
        known = self.save_to_db_known
        unknown = self.save_to_db_unknown

        now = datetime.now()
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')

        for x in known:
            mycursor.execute('INSERT INTO new_schema.add_data (nouns,success,date_time) VALUES (%s,1,%s);',
                             (x, formatted_date))
        mydb.commit()

        for y in unknown:
            mycursor.execute('INSERT INTO new_schema.add_data (nouns,success,date_time) VALUES (%s,0,%s);',
                             (y, formatted_date))
        mydb.commit()

        #mycursor.close()
        #mydb.close()
        self.wipe_tables()

    def wipe_tables(self):
        self.save_to_db_known = []
        self.save_to_db_unknown = []
        self.new_list = []
        self.button_list = []
        self.remove_data_from_temp_table()

    def remove_data_from_temp_table(self):

        mycursor.execute('DELETE FROM new_schema.temp_table;')
        mydb.commit()



        if self.number_of_iterating_pages == 0:
            self.retrieve_text()
        else:
            self.number_of_iterating_pages += 1
            self.text_4.set("Page number: " + str(self.number_of_iterating_pages) + " of " + str(self.declare_text_pages))
            self.next_page()



    def next_page(self):
        if self.declare_text_pages  >= self.number_of_iterating_pages:
            str1 = " "
            str1 = str1.join(self.text_partition[self.number_of_iterating_pages-1])
            wrap_text = ('\n'.join(textwrap.wrap(str1, 180, break_long_words=False)))
            self.text.set(wrap_text)
            text = str1
            if self.declare_text_pages == self.number_of_iterating_pages:
                self.next_text_button_1.grid_remove()
                self.frame.grid()
                self.next_text_button = tk.Button(self.frame, text='Next text', command=self.create_next_page_button)
                self.next_text_button.grid(row=6)
                self.frame.grid()
                self.number_of_iterating_pages = 0
                self.declare_text_pages = 1
            self.input_text_to_temp(text)


        # limit line legnth of texts
    def retrieve_text(self):

        for i in range(len(self.translationList)):
            self.translationList[i].destroy()
        self.translationList = []



        # retrieval of random text
        mycursor.execute("SELECT news_article FROM new_schema.news_articles ORDER BY RAND() LIMIT 1;")
        records = mycursor.fetchall()
        for row in records:
            x = row[0]

        self.limit_text(x)

    def limit_text(self,x):

        result = x.split()
        n = 50
        self.text_partition = [result[i:i + n] for i in range(0, len(result), n)]
        self.declare_text_pages = len(self.text_partition)

        str1 = " "
        self.number_of_iterating_pages += 1

        self.text_4.set("Page number: " + str(self.number_of_iterating_pages) + " of " + str(self.declare_text_pages))


        str1 = str1.join(self.text_partition[self.number_of_iterating_pages-1])



        if self.declare_text_pages > 1:
            self.next_text_button.grid_remove()
            self.frame.grid()

        # limit line legnth of texts
        wrap_text = ('\n'.join(textwrap.wrap(str1, 180, break_long_words=False)))

        self.text.set(wrap_text)
        text = str1
        self.input_text_to_temp(text)

    def input_text_to_temp(self, text):

        # inputting of data into the temporary table of all words contained within the
        # text for purposes of analysis against banked words.

        # Remove issue of line break
        text = text.replace('\n', ' ')

        # Remove double spacing
        text = text.replace('  ', ' ')

        tagger = ht.HanoverTagger('morphmodel_ger.pgz')

        sentences = nltk.sent_tokenize(text, language='german')
        final_list = []

        i = 0
        while i < (len(sentences)):
            tokenized_sent = nltk.tokenize.word_tokenize(sentences[i], language='german')
            final_list.append(tokenized_sent)
            i += 1

        x = list(chain.from_iterable(final_list))
        tags = tagger.tag_sent(x)

        nouns_from_sent = [lemma for (word, lemma, pos) in tags if pos == "NN"]


        self.new_list = nouns_from_sent


        for x in self.new_list:
            mycursor.execute('INSERT INTO new_schema.temp_table (word) VALUES (%s);', (x,))
        mydb.commit()

        self.percentage_success_fetch()

    def percentage_success_fetch(self):

        # Fetch the percentage of known Nouns in the above chosen text


        mycursor.execute("""with tab_a as (select sum(success) as success
                         FROM new_schema.temp_table a
                         inner join (SELECT nouns, success
                         FROM new_schema.add_data
                         WHERE id IN (SELECT MAX(id) FROM  new_schema.add_data  GROUP BY nouns)) b on a.word = b.nouns)
                         select success / count_rows
                         from tab_a
                         CROSS JOIN (select count(*) as count_rows
                         from new_schema.temp_table) b""")

        records_1 = mycursor.fetchall()

        if str(records_1[0]) == "(None,)":
            percentage_1 = "Percentage Known: 0%"
        else:
            for row in records_1:
                percentage_1 = ("latest guess known: " + str("{:.0%}".format(row[0])))

        self.text_1.set(percentage_1)

        self.percentage_failure_fetch()

    def percentage_failure_fetch(self):

        # Fetch the percentage of previously unknown Nouns in the above chosen text

        mycursor.execute("""with tab_a as (with tab_b as (select case when success = 0 then 1 else 0 end as Failure
                         FROM new_schema.temp_table a
                         inner join (SELECT nouns, success
                         FROM new_schema.add_data
                         WHERE id IN (SELECT MAX(id) FROM  new_schema.add_data  GROUP BY nouns)) b on a.word = b.nouns)
                         select sum(failure) as failure
                         from tab_b)
                         select failure / count_rows
                         from tab_a
                         CROSS JOIN (select
                         count(*) as count_rows
                         from new_schema.temp_table) b """)

        records_2 = mycursor.fetchall()

        if str(records_2[0]) == "(None,)":
            percentage_2 = "Percentage unknown: 0%"
        else:
            for row in records_2:
                percentage_2 = ("latest guess unknown: " + str("{:.0%}".format(row[0])))

        self.text_2.set(percentage_2)

        self.percentage_unknown_fetch()

    def percentage_unknown_fetch(self):

        # Fetch the percentage of known Nouns in the above chosen text


        mycursor.execute("""with tab_a as (select count(*) as previously_seen
                            FROM new_schema.temp_table a
                            inner join (SELECT nouns
                            FROM new_schema.add_data
                            WHERE id IN (SELECT MAX(id) FROM  new_schema.add_data  GROUP BY nouns)) b on a.word = b.nouns)
                            select 1 - previously_seen/count_rows
                            from tab_a
                            CROSS JOIN (select count(*) as count_rows
                            from new_schema.temp_table) b """)

        records_3 = mycursor.fetchall()

        if str(records_3[0]) == "(None,)":
            percentage_3 = "Percentage unseen: 100%"
        else:
            for row in records_3:
                percentage_3 = ("Percentage unseen: " + str("{:.0%}".format(row[0])))

        self.text_3.set(percentage_3)

        self.clean_buttons()

    def clean_buttons(self):

        # Remove all previous checkbutton lists
        for i in range(len(self.buttonList_object)):
            self.buttonList_object[i].destroy()
        self.buttonList_object = []

        # remove duplicate values appearing within the list
        self.new_list = list(dict.fromkeys(self.new_list))

        # All words for which we don't what to appear as buttons because we have shown that they are known words
        self.total_banked = []

        mycursor.execute("""with b as (with a as (SELECT nouns, success
                            FROM
                               (SELECT
                                     nouns,
                                     success,
                                     ROW_NUMBER() OVER (PARTITION BY nouns ORDER BY date_time desc) AS RowCount
                                 FROM
                                    new_schema.add_data
                                ) AS data
                            WHERE
                                data.RowCount <= 3)
                                select nouns,sum(success) as count_latest_success
                                from a
                                group by 1)
                                select Nouns
                                from b
                                where
                                count_latest_success = 3 """)

        self.total_banked = [i[0] for i in mycursor.fetchall()]

        # define the button list as all those values that have yet to be added
        self.button_list = [x for x in self.new_list if x not in self.total_banked]
        self.button_list = sorted(self.button_list)
        self.define_buttons()

    def define_buttons(self):

        for x in range(len(self.button_list)):
            var = tk.IntVar()
            self.chk = tk.Checkbutton(self.frame, text=self.button_list[x], variable=var,
                                      command=lambda x=x: self.check_button_press(x))
            self.buttonList_object.append(self.chk)
            self.vars.append(var)
            self.chk.grid(row=x + 7)

    def check_button_press(self, x):

        # runs on button press

        # delete all items from translation to enable new translation to be seen
        for i in range(len(self.translationList)):
            self.translationList[i].destroy()
        self.translationList = []

        # Fetch translations with google API
        translator = Translator()
        translated = translator.translate(self.button_list[x], src='de', dest='en')
        translation = str(f'{translated.origin} -> {translated.text}')

        # Setting of translation label
        self.translation_label = tk.StringVar()
        self.translation_label_1 = tk.Label(self.frame, textvariable=self.translation_label)
        self.translationList.append(self.translation_label_1)
        self.translation_label.set('')
        self.translation_label.set(translation)
        self.translation_label_1.grid(row=50)

        # Unknown is taken from the shortened button list

        if self.button_list[x] not in self.save_to_db_unknown:
            self.save_to_db_unknown.append(self.button_list[x])
        # Known is taken from the longer list including removed nouns

        self.save_to_db_known = [item for item in self.new_list if item not in self.save_to_db_unknown]


def main():
    root = tk.Tk(className='German text')
    app = Window(root)
    root.mainloop()


if __name__ == '__main__':
    main()