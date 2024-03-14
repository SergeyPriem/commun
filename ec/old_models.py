# # -*- coding: utf-8 -*-
#
# from datetime import datetime
# from pony.orm import *
#
# db = Database()
#
#
# class User(db.Entity):
#     id = PrimaryKey(int, auto=True)
#     first_name = Required(str, 50)
#     last_name = Optional(str, 50)
#     login = Required(str, 100, unique=True)
#     email = Required(str, 100)
#     phone = Required(str, 15)
#     role = Required(str, 20)
#     h_pass = Required(str, 60)
#     description = Optional(str, 1000)
#     url = Optional(str, 100)
#     record = Optional('Record')
#     date_time = Required(datetime)
#     experience = Optional(int, size=8)
#     major = Optional(str, 200)
#     company = Optional(str, 100)
#     lang = Required(str, 2)
#
#
# class RegLog(db.Entity):
#     id = PrimaryKey(int, auto=True)
#     user_login = Required(str, 100)
#     date_time_reg = Required(datetime)
#
#
# class VisitLog(db.Entity):
#     id = PrimaryKey(int, auto=True)
#     user_login = Required(str, 100)
#     date_time_in = Required(datetime)
#     date_time_out = Optional(datetime)
#     lang = Required(str, 2)
#
#
# class Project(db.Entity):
#     id = PrimaryKey(int, auto=True)
#     name = Optional(str, 250)
#     description = Optional(str, 1000)
#     files_link = Required(str, 255)
#     price = Optional(str, 1000)
#     note = Optional(str, 500)
#     designer = Optional(int, size=32)
#     record = Optional('Record')
#     date_time = Required(datetime)
#
#
# class Record(db.Entity):
#     id = PrimaryKey(int, auto=True)
#     project = Required(Project)
#     User = Required(User)
#     client_report = Optional(str, 1000)
#     performer_report = Optional(str, 1000)
#     executed_part = Optional(str, 1000)
#     date_time = Optional(str)
#
#
# db.bind(provider='sqlite', filename='database', create_db=True, timeout=5.0)
#
# db.generate_mapping(create_tables=True)
