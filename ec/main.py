# -*- coding: utf-8 -*-
import datetime
import time

import bcrypt
import streamsync as ss

from models import engine, User, VisitLog
from utilities import valid_email, _send_email, random_code_alphanumeric, err_handler, hash_password
from dic import dic
from dic import error_messages as e_m
from init_states import specialities, init_user, init_reg, init_login, init_projects, init_engineers, init_vacancy, \
    specialities_R, specialities_U, specialities_E

from sqlalchemy.exc import SQLAlchemyError

# Shows in the log when the app starts
print("Hello world!")


def _get_default_user_data(message_dict):
    return {
        "first_name": None,
        "last_name": None,
        "email": None,
        "phone": None,
        "role": None,
        "login": message_dict,
        "password": None,
        "password2": None,
        "logged": False,
        "lang": "E"
    }


# def _get_user_data(state):
#     with db_session:
#         try:
#             current_user = User.get(login=state["user"]["login"])
#         except Exception as e:
#             state["message"] = err_handler(e, "_get_user_data")
#             return _get_default_user_data(None)
#
#         if current_user:
#             if bcrypt.checkpw(str(state["user"]["password"]).encode("utf-8"), current_user.h_pass.encode("utf-8")):
#
#                 state["user"]["first_name"] = current_user.first_name
#                 state["user"]["last_name"] = current_user.last_name
#                 state["user"]["email"] = current_user.email
#                 state["user"]["phone"] = current_user.phone
#                 state["user"]["role"] = current_user.role
#                 state["user"]["login"] = state["user"]["login"]
#                 state["user"]["password"] = None
#                 state["user"]["password2"] = None
#                 state["user"]["logged"] = 1
#                 state["user"]["not_logged"] = 0
#                 state["user"]["lang"] = current_user.lang
#                 state["message"] = None
#
#                 try:
#                     VisitLog(
#                         user_login=state["user"]["login"],
#                         date_time_in=datetime.datetime.now(),
#                         lang=state["lang"]
#                     )
#                 except Exception as e:
#                     state["message"] = err_handler(e, "_get_user_data")
#             else:
#                 state[
#                     "message"] = "- Wrong login or password * Невірний логін або пароль * Неправильный логин или пароль"
#         else:
#             state["message"] = "- User not found * Користувач не знайдений * Пользователь не найден"


def _get_user_data(state):
    session = Session(bind=engine)
    try:
        current_user = session.query(User).filter(User.login == state["user"]["login"]).first()

    except SQLAlchemyError as e:
        state["message"] = err_handler(e, "_get_user_data")
        return _get_default_user_data(None)

    if current_user:
        if bcrypt.checkpw(str(state["user"]["password"]).encode("utf-8"), current_user.h_pass.encode("utf-8")):

            state["user"]["first_name"] = current_user.first_name
            state["user"]["last_name"] = current_user.last_name
            state["user"]["email"] = current_user.email
            state["user"]["phone"] = current_user.phone
            state["user"]["role"] = current_user.role
            state["user"]["login"] = state["user"]["login"]
            state["user"]["password"] = None
            state["user"]["password2"] = None
            state["user"]["logged"] = 1
            state["user"]["not_logged"] = 0
            state["user"]["lang"] = current_user.lang
            state["message"] = None

            try:
                visit_log = VisitLog(
                    user_login=state["user"]["login"],
                    date_time_in=datetime.datetime.now(),
                    lang=state["lang"]
                )
                session.add(visit_log)
                session.commit()

            except SQLAlchemyError as e:
                state["message"] = err_handler(e, "_get_user_data")

            finally:
                session.close()
        else:
            state["message"] = "- Wrong login or password * Невірний логін або пароль * Неправильный логин или пароль"
    else:
        state["message"] = "- User not found * Користувач не знайдений * Пользователь не найден"


def log_user(state):
    _get_user_data(state)

    if state["user"]["logged"]:

        state["lang"] = state["user"]["lang"]

        if state["user"]["role"] == 'client':
            state.set_page('engineers')
            state["engineers"]["content"] = 1
            state["engineers"]["warning"] = 0
            state["projects"]["content"] = 0
            state["projects"]["warning"] = 1
            state["vacancy"]["content"] = 0
            state["vacancy"]["warning"] = 1

        if state["user"]["role"] == 'engineer':
            state.set_page('projects')
            state["engineers"]["content"] = 0
            state["engineers"]["warning"] = 1
            state["projects"]["content"] = 1
            state["projects"]["warning"] = 0
            state["vacancy"]["content"] = 1
            state["vacancy"]["warning"] = 0

        if state["user"]["role"] == 'installer':
            state.set_page('projects')
            state["engineers"]["content"] = 1
            state["engineers"]["warning"] = 0
            state["projects"]["content"] = 1
            state["projects"]["warning"] = 0
            state["vacancy"]["content"] = 1
            state["vacancy"]["warning"] = 0
    else:
        state.set_page('wrong_login')
        state["engineers"]["content"] = 0
        state["engineers"]["warning"] = 1
        state["projects"]["content"] = 0
        state["projects"]["warning"] = 1
        state["vacancy"]["content"] = 0
        state["vacancy"]["warning"] = 1


# def _add_user_to_db(state):
#     if state["user"]["engineer"]:
#         major = ", ".join(state["user"]["major"])
#     else:
#         major = "-"
#
#     try:
#         with db_session:
#             User(
#                 first_name=state["user"]["first_name"],
#                 last_name=state["user"]["last_name"] or "-",
#                 email=state["user"]["email"],
#                 phone=state["user"]["phone"],
#                 login=state["user"]["login"],
#                 role=state["user"]["role"],
#                 h_pass=hash_password(state["user"]["password"]),
#                 description=state["user"]["description"] or "-",
#                 url='-',
#                 date_time=datetime.datetime.now(),
#                 experience=int(state["user"]["experience"] or 0),
#                 major=major,
#                 company=state["user"]["company"] or "-",
#                 lang=state["lang"]
#             )
#
#             RegLog(
#                 user_login=state["user"]["login"],
#                 date_time_reg=datetime.datetime.now()
#             )
#
#         state["reg"]["db_message_text"] = '+ Вы добавлены в базу данных'
#
#         return 200
#
#     except TransactionIntegrityError:
#         state["reg"]["db_message_text"] = f'- Пользователь с таким логином уже есть в базе данных. Измените логин'
#         return 500


from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


def _add_user_to_db(state):
    if state["user"]["engineer"]:
        major = ", ".join(state["user"]["major"])
    else:
        major = "-"

    try:
        with Session(engine) as session:
            new_user = User(
                first_name=state["user"]["first_name"],
                last_name=state["user"]["last_name"] or "-",
                email=state["user"]["email"],
                phone=state["user"]["phone"],
                login=state["user"]["login"],
                role=state["user"]["role"],
                h_pass=hash_password(state["user"]["password"]),
                description=state["user"]["description"] or "-",
                url='-',
                date_time=datetime.datetime.now(),
                experience=int(state["user"]["experience"] or 0),
                major=major,
                company=state["user"]["company"] or "-",
                lang=state["lang"]
            )
            session.add(new_user)
            session.commit()

        state["reg"]["db_message_text"] = '+ Вы добавлены в базу данных'
        return 200
    except IntegrityError:
        state["reg"]["db_message_text"] = f'- Пользователь с таким логином уже есть в базе данных. Измените логин'
        return 500
    finally:
        session.close()


def validate_email_by_code(state):
    if state['reg']['code_sent'] == state['reg']['code_entered']:

        state["reg"]["code_message"] = "+ Код подтвержден"

        state["reg"]["code_section"] = 0
        state["user"]["client"] = 0
        state["user"]["engineer"] = 0
        state["user"]["installer"] = 0
        state["reg"]['code_error'] = 0
        state["reg"]['code_ok'] = 1
        state["reg"]['db_message'] = 1

        if _add_user_to_db(state) == 200:
            state["reg"]['form'] = 0
            state["reg"]['data_ok'] = 0
            time.sleep(2)
            state.set_page("login")
    else:
        state["reg"]['code_error'] = 1
        state["reg"]['code_ok'] = 0
        state["reg"]["code_section"] = 1
        state["reg"]["code_message"] = "- Код ошибочный. Попробуйте еще раз"


def send_confirmation_code(state):
    state['reg']['code_sent'] = random_code_alphanumeric(6)

    print(f"Code sent: {state['reg']['code_sent']}")

    reply = _send_email(state)
    if reply['status'] == 200:
        state["reg"]["code_section"] = 1
    else:
        state["reg"]["code_section"] = 0


def validate_reg_data(state):
    """Check registration data and change states"""
    troubles = []

    if state["user"]['first_name']:
        if len(state["user"]['first_name']) <= 1:
            troubles.append(e_m["first_name"])
    else:
        troubles.append(e_m["first_name_2"])

    if not valid_email(state["user"]['email']):
        troubles.append(e_m["short_mail"])

    if state["user"]['phone']:
        if len(state["user"]['phone']) < 10:
            troubles.append(e_m["wrong_phone"])
    else:
        troubles.append(e_m["empty_phone"])

    if state["user"]['login']:
        if len(state["user"]['login']) < 3:
            troubles.append(e_m["short_login"])
    else:
        troubles.append(e_m["empty_login"])

    if state["user"]['password'] is None:
        troubles.append(e_m["empty_password"])

    if state["user"]['password'] != state["user"]['password2']:
        troubles.append(e_m["different_passwords"])

    if state["user"]['engineer']:
        if not state["user"]['major']:
            troubles.append(e_m["empty_speciality"])

    if not state["user"]['client']:
        if state["user"]['experience']:
            if state["user"]['experience'] < 1 or state["user"]['experience'] > 80:
                troubles.append(e_m["wrong_experience"])
        else:
            troubles.append(e_m["empty_experience"])

        if state["user"]['description']:
            if len(state["user"]['description']) < 10:
                troubles.append(e_m["short_description"])
        else:
            troubles.append(e_m["empty_description"])

    if len(troubles) > 0:
        # troubles_text = ", ".join(troubles)

        troubles_text = [t[state["lang"]] for t in troubles]

        state["reg"]["data_error"] = 1
        state["reg"]["data_error_message"] = ", ".join(troubles_text)
    else:
        state["reg"]["data_error"] = 0
        state["reg"]["data_error_message"] = None
        state["reg"]["data_ok"] = 1
        state["reg"]["form"] = 0

        state["user"]["client"] = 0
        state["user"]["engineer"] = 0
        state["user"]["installer"] = 0

        send_confirmation_code(state)


def show_client_form(state):
    state["user"]["client"] = 1
    state["user"]["engineer"] = 0
    state["user"]["installer"] = 0
    state["user"]["role"] = "client"

    state["reg"]["data_error"] = 0
    state["reg"]["code_ok"] = 0
    state["reg"]["data_ok"] = 0


def show_engineer_form(state):
    state["user"]["client"] = 0
    state["user"]["engineer"] = 1
    state["user"]["installer"] = 0
    state["user"]["role"] = "engineer"
    state["reg"]["data_error"] = 0
    state["reg"]["code_ok"] = 0
    state["reg"]["data_ok"] = 0


def show_installer_form(state):
    state["user"]["client"] = 0
    state["user"]["engineer"] = 0
    state["user"]["installer"] = 1
    state["user"]["role"] = "installer"
    state["reg"]["data_error"] = 0
    state["reg"]["code_ok"] = 0
    state["reg"]["data_ok"] = 0


def _log_out_user(state):
    with Session(bind=engine) as session:
        try:
            visit = session.query(
                VisitLog).filter(VisitLog.user_login == state["user"]["login"]
                                 ).order_by(VisitLog.id.desc()).first()
            if visit:
                visit.date_time_out = datetime.datetime.now()
                # Commit the changes
                session.commit()
            else:
                print("User not found")
        except SQLAlchemyError as e:
            print(f"An error occurred: {e}")


def quit_fun(state):
    """
    change states to initial conditions
    :param state:
    :return: None
    """
    _log_out_user(state)
    state["reg"] = init_reg
    state["login"] = init_login
    state["user"] = init_user
    state["projects"] = init_projects
    state["engineers"] = init_engineers
    state["vacancy"] = init_vacancy
    state["specs"] = specialities

    # state["message"] = None
    state.set_page('about')


def switch_to_rus(state):
    state["lang"] = "R"
    state["specs"] = specialities_R


def switch_to_eng(state):
    state["lang"] = "E"
    state["specs"] = specialities_E


def switch_to_ukr(state):
    state["lang"] = "U"
    state["specs"] = specialities_U


initial_state = ss.init_state({

    "message": None,
    "lang": "E",
    "dic": dic,

    "reg": init_reg,
    "login": init_login,
    "user": init_user,
    "projects": init_projects,
    "engineers": init_engineers,
    "vacancy": init_vacancy,
    "specs": specialities_E
})

initial_state.import_stylesheet("theme", "/static/custom.css?18")
