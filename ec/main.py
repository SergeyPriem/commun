# -*- coding: utf-8 -*-
import streamsync as ss

from utilities import valid_email, send_email, random_code_alphanumeric

# Shows in the log when the app starts
print("Hello world!")


# Its name starts with _, so this function won't be exposed

def _get_user_data(state):
    hashed_pass_now = "1234567890"
    hashed_pass_db = "1234567890"

    if hashed_pass_now == hashed_pass_db:
        return {
            "current": True,  # new or current
            "first_name": "FN",
            "last_name": "LN",
            "email": "None",
            "phone": "None",
            "role": "None",
            "login": state["user"]["login"],
            "password": None,
            "password2": None,
            "logged": True
        }
    else:
        return {
            "current": False,  # new or current
            "first_name": None,
            "last_name": None,
            "email": None,
            "phone": None,
            "role": None,
            "login": "Login not Exists in DB",
            "password": None,
            "password2": None,
            "logged": False
        }


def log_user(state):
    state["user"] = _get_user_data(state)

    if state["user"]["logged"]:
        state["logged"] = 1
        state["not_logged"] = 0

        if state["user"]["role"] == 'c':
            state.set_page('engineers')
            state["eng_content"] = 1
            state["projects_content"] = 0

        elif state["user"]["role"] == 'e':
            state.set_page('projects')
            state["projects_content"] = 1
            state["eng_content"] = 0

        else:
            state.set_page('about')
    else:
        state["logged"] = 0
        state["not_logged"] = 1


def add_user_to_db(state):
    ...
    return {
        'status': 200,
        'message': 'User Added'
    }


def validate_email_by_code(state):
    code_sent = state['reg_code']
    code_sent = "12345"
    code_entered = "12345"
    if code_sent == code_entered:
        state['reg_code_error'] = 0
        state['reg_code_ok'] = 1
        reply = add_user_to_db(state)
        if reply['status'] == 200:
            state['reg_code_ok'] = 1
            state['reg_form'] = 0
            state['reg_data_ok'] = 0
    else:
        state['reg_code_error'] = 1
        state['reg_code_ok'] = 0


def send_confirmation_code(state):
    state['reg_code'] = random_code_alphanumeric(6)
    reply = send_email(state)
    if reply['status'] == 200:
        state["reg_code"] = True
    else:
        state["reg_code"] = False


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

    if state["user"]['role'] == 'engineer':
        if not state["user"]['major']:
            troubles.append("Выберите специальность из списка")

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
        state["reg_data_error"] = 1
        state["reg_data_error_message"] = troubles_text
    else:
        state["reg_data_error"] = 0
        state["reg_data_error_message"] = None
        state["reg_data_ok"] = 1


def show_engineer_form(state):
    # state["role_selector"] = 0
    state["eng_form"] = 1
    state["client_form"] = 0
    state["inst_form"] = 0
    state["user"]['role'] = "engineer"


def show_installer_form(state):
    state["eng_form"] = 0
    state["client_form"] = 0
    state["inst_form"] = 1
    state["user"]['role'] = "installer"


def show_client_form(state):
    state["client_form"] = 1
    state["eng_form"] = 0
    state["inst_form"] = 0
    state["user"]['role'] = "client"


def quit_fun(state):
    """
    change states to initial conditions
    :param state:
    :return: None
    """
    state['user'] = {
        "current": False,  # new or current
        "first_name": None,
        "last_name": None,
        "email": None,
        "phone": None,
        "role": None,
        "login": None,
        "password": None,
        "password2": None,
        "logged": False
    }

    state["message"] = None

    state["status_message"] = None
    state["show_user_logged"] = False
    state["show_user_not_logged"] = False
    state["show_login_form"] = False
    state['show_login_button'] = True
    state['show_registration_button'] = True
    state['show_quit_button'] = False

    state["logged"] = False
    state["not_logged"] = True


initial_state = ss.init_state({

    "message": None,

    "not_logged": 1,
    "logged": 0,
    "reg_form": 1,
    "reg_data_ok": 0,
    "reg_data_error": 0,
    "reg_data_error_message": "",
    "reg_code": 0,
    "reg_code_ok": 0,
    "reg_code_error": 0,
    "reg_ok": 0,
    "login_form": 1,
    "login_data_error": 0,
    "login_not_in_db": 0,
    "projects_intro": 1,
    "projects_warning": 1,
    "projects_content": 0,
    "eng_warning": 1,
    "eng_content": 0,
    "vacancy_warning": 1,
    "vacancy_content": 0,
    "role_selector": 1,
    "eng_form": 0,
    "client_form": 0,
    "inst_form": 0,

    "user": {
        "current": False,  # new or current
        "first_name": None,
        "last_name": None,
        "email": None,
        "phone": None,
        "role": None,
        "login": None,
        "password": None,
        "password2": None,
        "experience": None,
        "major": None,  # speciality
        "description": None,  # description for project or experience
        "company": None,
        "logged": 0
    },

    "specs": {
        "el": "Электроснабжение",
        "ins": "КИПиА",
        "telecom": "Связь",
        "plot_plan": "Генплан",
        "piping_linear": "Линейная часть трубопроводов",
        "piping_area": "Монтаж технолог. оборудования",
        "hvac": "ОВиК",
        "wss": "Водоснабжение и Водоотведение",
        "term": "Теплоснабжение"
    }

})

initial_state.import_stylesheet("theme", "/static/custom.css?7")
