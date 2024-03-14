# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import MetaData, create_engine
from sqlalchemy.ext.declarative import declarative_base

metadata_obj = MetaData()

engine = create_engine("sqlite:///db.sqlite3")
Base = declarative_base()


class User(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50))
    login = Column(String(100), unique=True, nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(15), nullable=False)
    role = Column(String(20), nullable=False)
    h_pass = Column(String(60), nullable=False)
    description = Column(String(1000))
    url = Column(String(100))
    record = Column(Integer)
    date_time = Column(DateTime, nullable=False)
    experience = Column(Integer)
    major = Column(String(200))
    company = Column(String(100))
    lang = Column(String(2), nullable=False)


class VisitLog(Base):
    __tablename__ = 'VisitLog'

    id = Column(Integer, primary_key=True)
    user_login = Column(String(100), nullable=False)
    date_time_in = Column(DateTime, nullable=False)
    date_time_out = Column(DateTime)
    lang = Column(String(2), nullable=False)


metadata_obj.create_all(engine)
