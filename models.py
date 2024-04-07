# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from dotenv import load_dotenv
import os

load_dotenv()  # Загрузка переменных из .env файла

# api_key = os.getenv('API_KEY')  # Получение значения переменной
db_url = os.getenv('DB_URL')

# engine = create_engine("sqlite:///db.sqlite3")
engine = create_engine(db_url,pool_size=5, max_overflow=20)
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

    # Relationship to access the projects owned by a user
    projects = relationship("Projects", backref="user")


class Projects(Base):
    __tablename__ = 'Projects'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    owner = Column(Integer, ForeignKey('User.id'))  # owner is now a foreign key
    description = Column(String(1000))
    status = Column(String(10))
    comments = Column(String(200))
    created = Column(DateTime, nullable=False)
    status_changed = Column(DateTime)
    required_specialists = Column(String(200))
    assigned_engineers = Column(String(200))


class VisitLog(Base):
    __tablename__ = 'VisitLog'

    id = Column(Integer, primary_key=True)
    user_login = Column(String(100), nullable=False)
    date_time_in = Column(DateTime, nullable=False)
    date_time_out = Column(DateTime)
    lang = Column(String(2), nullable=False)


Base.metadata.create_all(engine)
