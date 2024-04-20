# -*- coding: utf-8 -*-
import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from dotenv import load_dotenv
import os

load_dotenv()  # Загрузка переменных из .env файла

# api_key = os.getenv('API_KEY')  # Получение значения переменной
db_url = os.getenv('DB_URL')

# engine = create_engine("sqlite:///db.sqlite3")
engine = create_engine(db_url, pool_size=5, max_overflow=20, pool_recycle=3600)
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
    invitations = relationship("Invitation", back_populates="user")


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
    invitations = relationship("Invitation", back_populates="project")


class Invitation(Base):
    __tablename__ = 'Invitation'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('Projects.id'),
                        nullable=False)  # Assuming the project table is named 'project'
    user_id = Column(Integer, ForeignKey('User.id'), nullable=False)  # Assuming the user table is named 'user'
    initiated_by = Column(Enum('engineer', 'client', 'installer'))
    status = Column(String(200)) # 0 for "Pending > ", 1 for "Accepted > ", 2 for "Declined > ", 3 "Waiting for response > ", 4 for "Cancelled > "
    date_time = Column(DateTime, nullable=False)
    last_action_dt = Column(DateTime, nullable=False)
    last_action_by = Column(Enum('engineer', 'client', 'installer'))
    # Relationships
    project = relationship('Projects', back_populates='invitations')
    user = relationship('User', back_populates='invitations')


class Subscription(Base):
    __tablename__ = 'Subscription'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    email = Column(String(100), nullable=False)
    date_time = Column(DateTime, nullable=False)

class Messages(Base):
    __tablename__ = 'Messages'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    email = Column(String(100), nullable=False)
    message = Column(String(1000), nullable=False)
    date_time = Column(DateTime, nullable=False)


class VisitLog(Base):
    __tablename__ = 'VisitLog'

    id = Column(Integer, primary_key=True)
    user_login = Column(String(100), nullable=False)
    date_time_in = Column(DateTime, nullable=False)
    date_time_out = Column(DateTime)
    lang = Column(String(2), nullable=False)


Base.metadata.create_all(engine)
