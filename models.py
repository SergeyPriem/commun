# -*- coding: utf-8 -*-

import os

from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

load_dotenv()  # Загрузка переменных из .env файла

# api_key = os.getenv('API_KEY')  # Получение значения переменной
db_url = os.getenv('DB_URL')

# engine = create_engine("sqlite:///db.sqlite3")
engine = create_engine(db_url, pool_size=5, max_overflow=20, pool_recycle=3600)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

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
    visibility = Column(String(4), nullable=False, default='cei')

    # Existing relationships
    rel_projects = relationship("Project", back_populates="rel_owner")
    rel_invitations = relationship("Invitation", back_populates="rel_user")
    rel_sent_cvs = relationship("CV", back_populates="rel_sender", foreign_keys="[CV.sender_id]")
    rel_received_cvs = relationship("CV", back_populates="rel_receiver", foreign_keys="[CV.receiver_id]")
    sent_messages = relationship("Message", back_populates="sender", foreign_keys="[Message.sender_id]")
    received_messages = relationship("Message", back_populates="receiver", foreign_keys="[Message.receiver_id]")

    # Relationships for HiddenUser
    hidden_users = relationship("HiddenUser", foreign_keys="[HiddenUser.user_id]", back_populates="user")
    hidden_by_users = relationship("HiddenUser", foreign_keys="[HiddenUser.hidden_user_id]",
                                   back_populates="hidden_user")
    hidden_projects = relationship("HiddenProject", back_populates="user")


class Project(Base):
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    owner = Column(Integer, ForeignKey('users.id'))  # Correct reference to the 'users' table
    description = Column(String(1000))
    status = Column(String(10))
    comments = Column(String(200))
    created = Column(DateTime, nullable=False)
    status_changed = Column(DateTime)
    required_specialists = Column(String(200))
    assigned_engineers = Column(String(200))
    visibility = Column(String(4), nullable=False, default='cei')

    # Relationships
    rel_owner = relationship("User", back_populates="rel_projects")
    rel_invitations = relationship("Invitation", back_populates="rel_project")
    hidden_by_users = relationship("HiddenProject", back_populates="project")

class HiddenProject(Base):
    __tablename__ = 'hidden_projects'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # Correct reference to the 'users' table
    project_id = Column(Integer, ForeignKey('projects.id'))  # Correct reference to the 'projects' table
    date_time = Column(DateTime, nullable=False)

    # Fixed Relationships using back_populates for clarity and explicitness
    user = relationship("User", back_populates="hidden_projects")
    project = relationship("Project", back_populates="hidden_by_users")



class HiddenUser(Base):
    __tablename__ = 'hidden_users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    hidden_user_id = Column(Integer, ForeignKey('users.id'))
    date_time = Column(DateTime, nullable=False)

    # Updated Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="hidden_users")
    hidden_user = relationship("User", foreign_keys=[hidden_user_id], back_populates="hidden_by_users")


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'))
    receiver_id = Column(Integer, ForeignKey('users.id'))
    message_text = Column(String)
    message_dt = Column(DateTime, nullable=False)
    read_dt = Column(DateTime, nullable=True)

    # Updated relationships with back_populates
    sender = relationship("User", back_populates="sent_messages", foreign_keys=[sender_id])
    receiver = relationship("User", back_populates="received_messages", foreign_keys=[receiver_id])


class CV(Base):
    __tablename__ = 'cvs'

    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    receiver_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    request_dt = Column(DateTime, nullable=False)
    status = Column(String(50), nullable=True)
    status_dt = Column(DateTime, nullable=True)

    # Relationships
    rel_sender = relationship('User', back_populates="rel_sent_cvs", foreign_keys=[sender_id])
    rel_receiver = relationship('User', back_populates="rel_received_cvs", foreign_keys=[receiver_id])


class Invitation(Base):
    __tablename__ = 'invitations'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    initiated_by = Column(Enum('engineer', 'client', 'installer'))
    status = Column(String(16000))
    date_time = Column(DateTime, nullable=False)
    last_action_dt = Column(DateTime, nullable=False)
    last_action_by = Column(Enum('engineer', 'client', 'installer'))

    # Relationships
    rel_project = relationship('Project', back_populates="rel_invitations")
    rel_user = relationship('User', back_populates="rel_invitations")


class Subscription(Base):
    __tablename__ = 'subscriptions'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    email = Column(String(100), nullable=False)
    date_time = Column(DateTime, nullable=False)


class VisitLog(Base):
    __tablename__ = 'visit_logs'

    id = Column(Integer, primary_key=True)
    user_login = Column(String(100), nullable=False)
    date_time_in = Column(DateTime, nullable=False)
    date_time_out = Column(DateTime)
    lang = Column(String(2), nullable=False)


Base.metadata.create_all(engine)
