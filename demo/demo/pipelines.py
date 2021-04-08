import logging
import csv
import os
from dateutil.parser import parse as date_parse

from sqlalchemy.orm import sessionmaker
from demo.models import db_connect, create_table, Article
import pymongo
from scrapy.exceptions import DropItem


from demo.settings import MONGODB_SERVER, MONGODB_PORT, MONGODB_COLLECTION, MONGODB_COLLECTION_CATE, MONGODB_DB


class CSVWriter():
    filename = None
    fp = None
    writer = None

    def __init__(self, filename):
        self.filename = filename
        file_exists = os.path.isfile(filename)
        if not file_exists:
            fieldnames = ['date', 'title', 'original_link', 'subhead', 'author', 'source', 'print', 'pic_list', 'body']
            self.fp = open(self.filename, 'a', encoding='utf8', newline='')
            self.writerRow = csv.DictWriter(self.fp, fieldnames=fieldnames)
            self.writerRow.writeheader()
        else:
            self.fp = open(self.filename, 'a', encoding='utf8', newline='')
            fieldnames = ['date', 'title', 'original_link', 'subhead', 'author', 'source', 'print', 'pic_list', 'body']
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
             'source': item['source'], 'print': item['print'], 'pic_list': item['pic_list'], 'body': item['body']})

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


class MongoDBPipeline(object):

    def __init__(self):
        connection = pymongo.MongoClient(
            MONGODB_SERVER,
            MONGODB_PORT
        )
        db = connection[MONGODB_DB]
        self.film = db[MONGODB_COLLECTION]
        self.cates = db[MONGODB_COLLECTION_CATE]

    def process_item(self, item, spider):
        categories_id = []
        if item['cates']:
            for cate in item['cates']:
                cate_old = self.cates.find_one({'name': cate}, {})
                if cate_old:
                    categories_id.append(cate_old['_id'])
                else:
                    obj_id = self.cates.insert({'name': cate})
                    categories_id.append(str(obj_id))
        item['categories_id'] = categories_id

        film = self.film.find_one({'name': item['name']})
        if not film:
            self.film.insert(dict(item))
        else:
            pass

        return item
