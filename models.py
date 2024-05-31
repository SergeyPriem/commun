# -*- coding: utf-8 -*-

import os

from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

load_dotenv()  # Загрузка переменных из .env файла

db_url = os.getenv('DB_URL')

# engine = create_engine("sqlite:///db.sqlite3")
engine = create_engine(db_url, pool_size=5, max_overflow=20, pool_recycle=3600)
Base = declarative_base()


class HiddenUser(Base):
    __tablename__ = 'hidden_users'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    hidden_user_id = Column(Integer, ForeignKey('users.id'))
    date_time = Column(DateTime, nullable=False)

    # Updated Relationships
    rel_user = relationship("User", foreign_keys=[user_id], back_populates="rel_hidden_users")
    rel_hidden_user = relationship("User", foreign_keys=[hidden_user_id], back_populates="rel_hidden_by_users")


class Invitation(Base):
    __tablename__ = 'invitations'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    proposed_by = Column(Integer, ForeignKey('users.id'), nullable=False)
    status = Column(Enum('pending', 'accepted', 'declined', 'cancelled', 'deleted'))
    date_time = Column(DateTime, nullable=False)
    last_action_dt = Column(DateTime, nullable=False)
    last_action_by = Column(Integer, ForeignKey('users.id'), nullable=False)

    # Relationships
    rel_project = relationship('Project', back_populates="rel_invitations")
    rel_user = relationship('User', back_populates="rel_invitations", foreign_keys=[user_id])
    rel_proposed_by = relationship('User', back_populates="rel_proposed_invitations", foreign_keys=[proposed_by])
    rel_last_action_by = relationship('User', back_populates="rel_last_action_invitations",
                                      foreign_keys=[last_action_by])


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
    rel_sent_cvs = relationship("CV", back_populates="rel_sender", foreign_keys="[CV.sender_id]")
    rel_received_cvs = relationship("CV", back_populates="rel_receiver", foreign_keys="[CV.receiver_id]")
    rel_sent_messages = relationship("Message", back_populates="rel_sender", foreign_keys="[Message.sender_id]")
    rel_received_messages = relationship("Message", back_populates="rel_receiver", foreign_keys="[Message.receiver_id]")
    rel_hidden_users = relationship("HiddenUser", foreign_keys=[HiddenUser.user_id], back_populates="rel_user")
    rel_hidden_by_users = relationship("HiddenUser", foreign_keys=[HiddenUser.hidden_user_id],
                                       back_populates="rel_hidden_user")
    rel_hidden_projects = relationship("HiddenProject", back_populates="rel_user")
    rel_invitations = relationship("Invitation", back_populates="rel_user", foreign_keys=[Invitation.user_id])
    rel_proposed_invitations = relationship("Invitation", back_populates="rel_proposed_by",
                                            foreign_keys="[Invitation.proposed_by]")
    rel_last_action_invitations = relationship("Invitation", back_populates="rel_last_action_by",
                                               foreign_keys="[Invitation.last_action_by]")


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
    rel_hidden_by_users = relationship("HiddenProject", back_populates="rel_project")
    rel_messages = relationship("Message", back_populates="rel_project")  # Added this line


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    sender_id = Column(Integer, ForeignKey('users.id'))
    receiver_id = Column(Integer, ForeignKey('users.id'))
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    message_text = Column(String(1000), nullable=False)
    dialog_id = Column(Integer, nullable=False)
    message_dt = Column(DateTime, nullable=False)
    read_dt = Column(DateTime, nullable=True)

    # relationships
    rel_sender = relationship("User", back_populates="rel_sent_messages", foreign_keys=[sender_id])
    rel_receiver = relationship("User", back_populates="rel_received_messages", foreign_keys=[receiver_id])
    rel_project = relationship("Project", back_populates="rel_messages")  # Changed this line


class HiddenProject(Base):
    __tablename__ = 'hidden_projects'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # Correct reference to the 'users' table
    project_id = Column(Integer, ForeignKey('projects.id'))  # Correct reference to the 'projects' table
    date_time = Column(DateTime, nullable=False)

    # Fixed Relationships using back_populates for clarity and explicitness
    rel_user = relationship("User", back_populates="rel_hidden_projects")
    rel_project = relationship("Project", back_populates="rel_hidden_by_users")


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
