# -*- coding: utf-8 -*-
import datetime
import time

import streamsync as ss

from db_actions import _create_new_user, _log_admin, _get_new_engineers, _get_new_installers, _get_user_data, \
    _log_out_user, admin_panel_section, _decline_invitation, _get_actual_own_projects, \
    _add_user_message, _delete_subscription, _get_new_current_projects, \
    _get_all_current_projects, _get_all_finished_projects, _create_project, _add_invitation_by_client, _get_engineers, \
    _get_all_engineers, _get_all_installers, _send_request, _prepare_eng_page, _add_to_subscription, _offer_service, \
    _get_table_as_dataframe
from dic import dic
from dic import error_messages as e_m
from fw import ss_dic
from init_states import specialities, init_user, init_reg, init_login, init_projects, init_engineers, init_vacancy, \
    specialities_R, specialities_U, specialities_E, init_new_project
from utilities import _send_email, _random_code_alphanumeric, _basic_data_validation

print(f"You are using the main.py file from {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def get_table_as_dataframe(state):
    _get_table_as_dataframe(state)


def get_actual_own_projects(state):
    _get_actual_own_projects(state)


def get_actual_own_projects_dict(state):
    _get_actual_own_projects(state)
    state["current_own_projects_dict"] = {
        str(key): value["name"]
        for key, value in state["current_own_projects"].items()}


def add_invitation_by_client(state):
    _add_invitation_by_client(state)


def offer_service(state, context):
    _offer_service(state, context)


def get_finished_own_projects(state):
    ...


def get_cancelled_own_projects(state):
    ...


def get_suspended_own_projects(state):
    ...


def get_new_current_projects(state):
    _get_new_current_projects(state)


def get_all_current_projects(state):
    _get_all_current_projects(state)


def get_all_finished_projects(state):
    _get_all_finished_projects(state)


def create_project(state):
    _create_project(state)


def log_admin(state):
    _log_admin(state)


def get_new_engineers(state):
    _get_new_engineers(state)


def get_new_installers(state):
    _get_new_installers(state)


def log_user(state):
    _get_user_data(state)

    role_pages = {
        'client': 'client_page',
        'engineer': 'engineer_page',
        'installer': 'projects',
        'admin': 'projects'
    }

    content_states = {
        'client': (1, 0, 0, 1),
        'engineer': (0, 1, 1, 0),
        'installer': (1, 0, 1, 0),
        'admin': (1, 0, 1, 0)
    }

    if state["user"]["logged"]:
        print(f"User {state['user']['login']} with role {state['user']['role']} "
              f"is logged in {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}!")
        role = state["user"]["role"]
        if role == 'admin':
            state.add_notification("warning", "Warning!", "Wrong role...")
            quit_fun(state)
            state.set_page("about")
        else:
            state["lang"] = state["user"]["lang"]
            state.set_page(role_pages[role])
            state["engineers"]["content"], state["engineers"]["warning"], state["projects"]["content"], \
                state["projects"]["warning"] = content_states[role]
            if role == 'engineer':
                _prepare_eng_page(state)
            if role in ('engineer', 'installer'):
                state["vacancy"]["content"] = 1
                state["vacancy"]["warning"] = 0
    else:
        state.set_page('wrong_login')
        state["engineers"]["content"] = state["engineers"]["warning"] = state["projects"]["content"] = \
            state["projects"]["warning"] = 0


def validate_email_by_code(state):
    if state['reg']['code_sent'] == state['reg']['code_entered']:

        state["reg"]["code_message"] = "+ " + dic["code_confirmed"][state["lang"]]

        if _create_new_user(state) == 200:
            state["reg"]['form'] = 0
            state["reg"]['data_ok'] = 0
            time.sleep(2)
            state.set_page("login")

        state["reg"]["code_section"] = 0
        state["reg"]['code_error'] = 0
        state["reg"]['code_ok'] = 1
        state["reg"]['db_message'] = 1

    else:
        state["reg"]['code_error'] = 1
        state["reg"]['code_ok'] = 0
        state["reg"]["code_section"] = 1
        state["reg"]["code_message"] = "- " + dic["wrong_code"][state["lang"]]


def send_confirmation_code(state):
    state['reg']['code_sent'] = _random_code_alphanumeric(6)

    reply = _send_email(state)
    if reply['status'] == 200:
        state["reg"]["code_section"] = 1
    else:
        state["reg"]["code_section"] = 0


def validate_reg_data(state):
    """Check registration data and change states"""
    lang = state["lang"]

    troubles = _basic_data_validation(state)

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

        troubles_text = [t[lang] for t in troubles]
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


def prepare_el(state):
    _get_engineers(state, "el")


def prepare_ins(state):
    _get_engineers(state, "ins")


def prepare_plot_plan(state):
    _get_engineers(state, "plot_plan")


def prepare_low_cur(state):
    _get_engineers(state, "low_cur")


def prepare_piping_linear(state):
    _get_engineers(state, "piping_linear")


def prepare_piping_area(state):
    _get_engineers(state, "piping_area")


def prepare_hvac(state):
    _get_engineers(state, "hvac")


def prepare_wss(state):
    _get_engineers(state, "wss")


def prepare_ar(state):
    _get_engineers(state, "ar")


def get_all_engineers(state):
    _get_all_engineers(state)


def get_all_installers(state):
    _get_all_installers(state)


def connect_w_engineer(state, context):
    state["selected_engineers"] += [context["itemId"]]
    state["selected_engineers"] = list(set(state["selected_engineers"]))


def admin_reg_section(state):
    state["user"]["role"] = "admin"
    state["admin"]["reg_sect"] = 1
    state["admin"]["code_sect"] = 0
    state["admin"]["log_sect"] = 0
    state["admin"]["panel_sect"] = 0


def admin_code_section(state):
    state["admin"]["reg_sect"] = 0
    state["admin"]["code_sect"] = 1
    state["admin"]["log_sect"] = 0
    state["admin"]["panel_sect"] = 0


def close_project(state, context):
    state.add_notification("info", "Context!", context["itemId"])
    # with Session(bind=engine) as session:
    #     try:
    #         project = session.query(Projects).filter(Projects.id == context["itemId"]).first()
    #         project.status = "finished"
    #         session.commit()
    #
    #     except SQLAlchemyError as e:
    #         state.add_notification(f"An error occurred: {e}")


def set_selected_engineer(state, context):
    get_actual_own_projects_dict(state)
    state["selected_eng_for_proj"] = str(context["itemId"])

    state.set_page("invite_to_project")


def admin_log_section(state):
    state["admin"]["reg_sect"] = 0
    state["admin"]["code_sect"] = 0
    state["admin"]["log_sect"] = 1
    state["admin"]["panel_sect"] = 0


def validate_admin_data(state):
    lang = state["lang"]
    troubles = _basic_data_validation(state)

    if len(troubles) > 0:
        troubles_text = [t[lang] for t in troubles]
        state.add_notification("warning", "Warning!", ", ".join(troubles_text))

    else:
        send_confirmation_code(state)
        admin_code_section(state)


def validate_admin_code(state):
    if state['reg']['code_sent'] == state['reg']['code_entered']:
        _create_new_user(state)
        admin_log_section(state)


def validate_admin_login(state):
    get_table_as_dataframe(state)
    admin_panel_section(state)


def add_to_subscription(state):
    _add_to_subscription(state)


def request_for_invitation(state, context):
    state['current_invitation'] = context['item']
    state['current_invitation_id'] = context['itemId']
    state.set_page("request_to_client")


def send_request(state):
    _send_request(state)


def decline_invitation(state, context):
    _decline_invitation(state, context)


def show_code_window(state):
    state["subscription"]["code_window"] = 1


def compare_unsubscription_codes(state):
    if state["unsubscribe_code"] == state["subscription"]["code_sent"]:
        state["got_unsubscribe_code"] = 1
    else:
        state["got_unsubscribe_code"] = 0


def delete_subscription(state):
    _delete_subscription(state)


def show_unsubscribe_window(state):
    state["unsubscribe"]["section"] = 1
    state["subscribe"]["section"] = 0


def show_subscribe_window(state):
    state["unsubscribe"]["section"] = 0
    state["subscribe"]["section"] = 1


def add_user_message(state):
    _add_user_message(state)


def handle_hash_change(state, payload):
    route_vars = payload.get("route_vars")
    if route_vars:
        state.add_notification('info', 'Route vars', route_vars['country'])
        state['country'] = route_vars['country']


initial_state = ss.init_state(
    {
        "lang": "E",
        "dic": dic,
        "reg": init_reg,
        "login": init_login,
        "user": init_user,
        "projects": init_projects,
        "engineers": init_engineers,
        "vacancy": init_vacancy,
        "specs": specialities_E,
        "new_project": init_new_project,

        "add_project": {
            "show_section": 1,
            "show_message": 0,
        },

        "subscribe": {
            "section": 1,
            "first_name": None,
            "last_name": None,
            "email": None,
            "code_window": 0,
            'code_sent': None,
        },

        "unsubscribe": {
            'section': 0,
            'email': None,
            "code_sent": None,
            "code_entered": None,
            "code_window": 0,
        },

        "show_hidden_eng": False,
        "show_hidden_ins": False,

        "admin": {
            "reg_sect": 0,
            "code_sect": 0,
            "log_sect": 0,
            "panel_sect": 0
        },

        # "my_invitations": None,
        # "user_message": {
        #    "first_name": None,
        #    "last_name": None,
        #    "email": None,
        #    "message": None
        # },
        # "unsubscribe_code": None,
        # "got_unsubscribe_code": None,
        # "current_invitation_id": None,
        # "current_invitation": None,
        # "current_invitation_message": None,
        # "invitations_quantity": None,
        # "new_proj_quantity": None,
        # 'actual_proj_quantity': None,
        # "current_own_projects": {
        #    "name": None,
        #    "description": None,
        #    "status": None,
        #    "comments": None,
        #    "required_specialists": None,
        #    "assigned_engineers": None,
        #    "created": None
        # },
        # "new_current_projects": None,
        # "all_current_projects": None,
        # "all_finished_projects": None,
        # "all_engineers": None,
        # "all_installers": None,
        #
        # "new_current_projects_message": None,
        # "all_current_projects_message": None,
        # "all_finished_projects_message": None,
        # "all_engineers_message": None,
        # "all_installers_message": None,
        # "current_own_projects_dict": None,
        # "selected_proj_to_add_eng": None,
        # "selected_eng_for_proj": None,
        # "user_invitation_status": None,
        # "fd": ss_dic,
        # "ar": None,  # "Architecture",
        # "el": None,
        # "ins": None,
        # "low_cur": None,
        # "plot_plan": None,
        # "piping_linear": None,
        # "piping_area": None,
        # "hvac": None,
        # "wss": None,
        # "term": None,
        # "civil": None,
        # "selected_engineers": [],
        # "new_engineers": None,
        # "new_installers": None,
        # "trusted_engineers": None,
        # "viewed_engineers": None,

    })

initial_state.import_stylesheet("theme", "/static/custom.css?55")

print("Code executed successfully!")
