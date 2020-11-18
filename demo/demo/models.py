from sqlalchemy import create_engine, Column
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import (
    Integer, String, Date, DateTime, Float, Boolean, Text, BigInteger)
from scrapy.utils.project import get_project_settings
import os

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))


def create_table(engine):
    Base.metadata.create_all(engine)


class Article(Base):
    __tablename__ = "article"
    id = Column(Integer, primary_key=True)
    title = Column('title', Text())
    date = Column('date', Text())
    original_link = Column('original_link', Text())
