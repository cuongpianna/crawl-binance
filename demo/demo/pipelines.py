import logging
import csv
import os
from dateutil.parser import parse as date_parse

from sqlalchemy.orm import sessionmaker
from demo.models import db_connect, create_table, Article


class CSVWriter():
    filename = None
    fp = None
    writer = None

    def __init__(self, filename):
        self.filename = filename
        file_exists = os.path.isfile(filename)
        if not file_exists:
            fieldnames = ['date', 'title', 'original_link', 'subhead', 'author', 'source', 'pic_list', 'body']
            self.fp = open(self.filename, 'a', encoding='utf8', newline='')
            self.writerRow = csv.DictWriter(self.fp, fieldnames=fieldnames)
            self.writerRow.writeheader()
        else:
            self.fp = open(self.filename, 'a', encoding='utf8', newline='')
            fieldnames = ['date', 'title', 'original_link', 'subhead', 'author', 'source', 'pic_list', 'body']
            self.writerRow = csv.DictWriter(self.fp, fieldnames=fieldnames)

        self.writer = csv.writer(self.fp, delimiter=';', quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n')

    def close(self):
        self.fp.close()

    def write(self, elems):
        self.writer.writerow(elems)

    def write_element(self, item):
        self.writerRow.writerow(
            {'date': item['date'], 'title': item['title'], 'original_link': item['original_link'],
             'subhead': item['subhead'], 'author': item['author'],
             'source': item['source'], 'pic_list': item['pic_list'], 'body': item['body']})

    def size(self):
        return os.path.getsize(self.filename)

    def fname(self):
        return self.filename


class SaveNewsPipeline(object):
    def __init__(self):
        """
        Initializes database connection and sessionmaker
        Creates tables
        """
        engine = db_connect()
        create_table(engine)
        self.Session = sessionmaker(bind=engine)
        logging.info("****SaveNewsPipeline: database connected****")

    def process_item(self, item, spider):
        """Save data in the database
        This method is called for every item pipeline component
        """
        session = self.Session()

        article = Article()
        article.original_link = item['original_link']
        article.title = item['title']
        article.date = item['date']

        news_date = date_parse(item['date'])
        filename = '{}-{}-{}.csv'.format(item['site'], news_date.month, news_date.year)

        # save article to db
        exist_article = session.query(Article).filter_by(original_link=article.original_link).first()
        if exist_article is None:
            mycsv = CSVWriter(filename)
            mycsv.write_element(item)
            try:
                session.add(article)
                session.commit()
            except:
                session.rollback()
                raise
            finally:
                session.close()

        return item
