# -*- coding: utf-8 -*-
import datetime
import time

import bcrypt
import streamsync as ss
from pony.orm import *
from utilities import valid_email, _send_email, random_code_alphanumeric, err_handler, hash_password, dic
from init_states import specialities, init_user, init_reg, init_login, init_projects, init_engineers, init_vacancy
from models import User

# Shows in the log when the app starts
print("Hello world!")


def open_streamsync_website(state):
    state.open_url("https://streamsync.cloud")


def _get_default_user_data(message):
    return {
        "first_name": None,
        "last_name": None,
        "email": None,
        "phone": None,
        "role": None,
        "login": message,
        "password": None,
        "password2": None,
        "logged": False
    }


def _get_user_data(state):
    try:
        with db_session:
            current_user = User.get(login=state["user"]["login"])
            print("line 34")
    except Exception as e:
        state["message"] = err_handler(e, "_get_user_data")
        return _get_default_user_data(None)

    if current_user:

        if bcrypt.checkpw(str(state["user"]["password"]).encode("utf-8"), current_user.h_pass.encode("utf-8")):
            return {
                "first_name": current_user.first_name,
                "last_name": current_user.last_name,
                "email": current_user.email,
                "phone": current_user.phone,
                "role": current_user.role,
                "login": state["user"]["login"],
                "password": None,
                "password2": None,
                "logged": True
            }
        else:
            return _get_default_user_data("- Неверный логин или пароль")
    else:
        print('Пользователь не найден')
        return _get_default_user_data("- Пользователь не найден")


def log_user(state):
    state["user"] = _get_user_data(state)

    if state["user"]["logged"]:

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


def add_user_to_db(state):
    if state["user"]["engineer"]:
        major = ", ".join(state["user"]["major"])
    else:
        major = "-"

    try:
        with db_session:
            User(
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
                company=state["user"]["company"] or "-"
            )

        state["reg"]["db_message_text"] = '+ Вы добавлены в базу данных'
        return 200

    except TransactionIntegrityError:
        state["reg"]["db_message_text"] = f'- Пользователь с таким логином уже есть в базе данных. Измените логин'
        return 500


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

        if add_user_to_db(state) == 200:
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
    """
    Check registration data and change states
    :param state:
    :return:
    """
    troubles = []

    if state["user"]['first_name']:
        if len(state["user"]['first_name']) <= 1:
            troubles.append("Введите имя длиннее двух символов")
    else:
        troubles.append("Введите имя")

    if not valid_email(state["user"]['email']):
        troubles.append("Введите корректный email")

    if state["user"]['phone']:
        if len(state["user"]['phone']) < 10:
            troubles.append("Введите корректный номер телефона")
    else:
        troubles.append("Введите номер телефона")

    if state["user"]['login']:
        if len(state["user"]['login']) < 3:
            troubles.append("Введите логин не менее 3 символов")
    else:
        troubles.append("Введите логин")

    if state["user"]['password'] is None:
        troubles.append("Введите пароль")

    if state["user"]['password'] != state["user"]['password2']:
        troubles.append("Пароли не совпадают")

    if state["user"]['engineer']:
        if not state["user"]['major']:
            troubles.append("Выберите специальность из списка")

    if not state["user"]['client']:
        if state["user"]['experience']:
            if state["user"]['experience'] < 1 or state["user"]['experience'] > 80:
                troubles.append("Введите корректный опыт работы")
        else:
            troubles.append("Введите опыт работы")

        if state["user"]['description']:
            if len(state["user"]['description']) < 10:
                troubles.append("Введите описание навыков более детально")
        else:
            troubles.append("Введите описание навыков")

    if len(troubles) > 0:
        troubles_text = ", ".join(troubles)
        state["reg"]["data_error"] = 1
        state["reg"]["data_error_message"] = troubles_text
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


def quit_fun(state):
    """
    change states to initial conditions
    :param state:
    :return: None
    """
    state["reg"] = init_reg
    state["login"] = init_login
    state["user"] = init_user
    state["projects"] = init_projects
    state["engineers"] = init_engineers
    state["vacancy"] = init_vacancy
    state["specs"] = specialities

    state["message"] = None


def switch_to_rus(state):
    state["lang"] = "R"


def switch_to_eng(state):
    state["lang"] = "E"


def switch_to_ukr(state):
    state["lang"] = "U"


initial_state = ss.init_state({

    "message": None,
    "lang": "R",
    "dic": dic,

    "reg": init_reg,
    "login": init_login,
    "user": init_user,
    "projects": init_projects,
    "engineers": init_engineers,
    "vacancy": init_vacancy,
    "specs": specialities
})

initial_state.import_stylesheet("theme", "/static/custom.css?8")
