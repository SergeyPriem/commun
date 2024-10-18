# -*- coding: utf-8 -*-

import writer as wf
from assets.help import he
from db_actions import *
from dic import dic
from dic import error_messages as e_m
from fw import ss_dic
from init_states import *
from logging_config import LOGGING_CONFIG
from menus import eng_menu, my_prospects_menu, main_menu, my_projects_menu, client_menu
from utilities import _send_email, _random_code_alphanumeric, _basic_data_validation

logging.config.dictConfig(LOGGING_CONFIG)

# Now you can use logging as usual
logger = logging.getLogger(__name__)

logger.debug(f"You are using the main.py file from {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def go_page(state, context):
    state.set_page(context.get('itemId', 'page_not_found'))


def _create_prospects_menu(state, context):
    state["my_prospects_menu"] = _create_menu("my_prospects_menu", my_prospects_menu, None)


def _create_projects_menu(state, context):
    state["my_projects_menu"] = _create_menu("my_projects_menu", my_projects_menu, None)


def create_client_menu(state, context):
    state["client_menu"] = _create_menu("client_menu", client_menu, None)


def _execute_menu_function(state, context):
    function = context.get('item').get("fun")

    if function:
        try:
            globals()[function](state, context)
        except Exception as e:
            logger.error(f"Error: {e}")
            state.add_notification('error', "Error", "Something went wrong...")


def _create_menu(menu_name: str, menu: dict, init_index=None) -> dict:
    return {
        key: {
            "fun": item.pop('fun', None),
            "reset": item.pop("reset", None),
            "text": item,
            "css": "underlined-text" if i == init_index else None,
            "menu_name": menu_name
        } for i, (key, item) in enumerate(menu.items())
    }


def reset_menu_css(state, reset_list: list):
    if reset_list:
        if isinstance(reset_list, str):
            reset_list = [reset_list]

        for reset_menu in reset_list:
            if state[reset_menu] is not None:
                for key in state[reset_menu].items():
                    state[reset_menu][key[0]]["css"] = None
            # else:
            #     logger.error(f"Menu {reset_menu} is None")


def update_menu_css(state, menu_name: str, context: dict):
    for key in state[menu_name].items():
        state[menu_name][key[0]]["css"] = None

    state[menu_name][context['itemId']]["css"] = "underlined-text"


def change_menu(state, context):
    menu_name = context['item']['menu_name']
    reset_list = context['item']['reset']

    reset_menu_css(state, reset_list)
    update_menu_css(state, menu_name, context)
    _execute_menu_function(state, context)


class PCol:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def get_table_as_dataframe(state):
    db_get_table_as_dataframe(state)


def get_actual_own_projects(state, context):
    db_get_my_current_projects(state)


def get_actual_own_projects_dict(state):
    db_get_my_current_projects(state)
    state["current_own_projects_dict"] = {
        str(key): value["name"]
        for key, value in state["current_own_projects"].items()}


def invite(state):
    db_invite(state)


def get_my_invitations(state):
    db_get_my_invitations(state)


def offer_service(state, context):
    db_offer_service(state, context)


def get_finished_own_projects(state):
    ...


def get_cancelled_own_projects(state):
    ...


def get_suspended_own_projects(state):
    ...


def get_new_current_projects(state):
    db_get_new_projects(state)


def get_all_current_projects(state):
    db_get_current_projects(state)


def get_all_finished_projects(state):
    db_get_all_finished_projects(state)


def create_project(state):
    db_create_project(state)


def log_admin(state):
    db_log_admin(state)


def get_new_engineers(state):
    db_get_new_engineers(state)


def get_new_installers(state):
    db_get_new_installers(state)


def log_user(state):
    db_get_user_data(state)

    role_pages = {
        'client': 'client_page',
        'engineer': 'engineer_page',
        'installer': 'projects',
        'admin': 'projects'
    }

    content_states = {
        'client': (1, 0, ),
        'engineer': (0, 1, ),
        'installer': (1, 1, ),
        'admin': (1, 1, )
    }

    if state["user"]["logged"]:
        logger.info(f"{PCol.OKGREEN}{state['user']['role']} {state['user']['login']} | in: {datetime.datetime.now()}!")
        role = state["user"]["role"]
        if role == 'admin':
            state.add_notification("warning", "Warning!", "Wrong role...")
            quit_fun(state)
            state.set_page("about")
        else:
            state["lang"] = state["user"]["lang"]
            state.set_page(role_pages[role])
            state["engineers"]["content"], state["projects"]["content"] = content_states[role]
            if role == 'engineer':
                db_prepare_eng_page(state)
            if role in ('engineer', 'installer'):
                state['eng_menu'] = _create_menu("eng_menu", eng_menu, None)
                state["vacancies"]["content"] = 1
    else:
        state.set_page('wrong_login')
        state["engineers"]["content"] = state["projects"]["content"] = 0


def validate_email_by_code(state):
    if state['reg']['code_sent'] == state['reg']['code_entered']:

        state["reg"]["code_message"] = "+ " + dic["code_confirmed"][state["lang"]]

        if db_create_user(state) == 200:
            state["reg"]['form'] = 0
            state["reg"]['data_ok'] = 0
            time.sleep(2)
            state.set_page("login")

        state["reg"]["code_section"] = 0
        state["reg"]['code_ok'] = 1
    else:
        state["reg"]['code_ok'] = 0
        state["reg"]["code_section"] = 1
        state["reg"]["code_message"] = "- " + dic["wrong_code"][state["lang"]]


def send_confirmation_code(state):
    state['reg']['code_sent'] = _random_code_alphanumeric(6)

    reply = _send_email(state)
    state["reg"]["code_section"] = 1 if reply['status'] == 200 else 0


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
        state["reg"]["data_error_message"] = ", ".join(troubles_text)
    else:
        state["reg"]["data_error_message"] = ""
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
    state["reg"]["code_ok"] = 0
    state["reg"]["data_ok"] = 0


def show_engineer_form(state):
    state["user"]["client"] = 0
    state["user"]["engineer"] = 1
    state["user"]["installer"] = 0
    state["user"]["role"] = "engineer"
    state["reg"]["code_ok"] = 0
    state["reg"]["data_ok"] = 0


def show_installer_form(state):
    state["user"]["client"] = 0
    state["user"]["engineer"] = 0
    state["user"]["installer"] = 1
    state["user"]["role"] = "installer"
    state["reg"]["code_ok"] = 0
    state["reg"]["data_ok"] = 0


def quit_fun(state):
    """
    change states to initial conditions
    :param state:
    :return: None
    """
    db_log_out_user(state)
    state["reg"] = init_reg
    state["login"] = init_login
    state["user"] = init_user
    state["projects"] = init_projects
    state["engineers"] = init_engineers
    state["vacancies"] = init_vacancies
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
    db_get_engineers(state, "el")


def prepare_ins(state):
    db_get_engineers(state, "ins")


def prepare_plot_plan(state):
    db_get_engineers(state, "plot_plan")


def prepare_low_cur(state):
    db_get_engineers(state, "low_cur")


def prepare_piping_linear(state):
    db_get_engineers(state, "piping_linear")


def prepare_piping_area(state):
    db_get_engineers(state, "piping_area")


def prepare_hvac(state):
    db_get_engineers(state, "hvac")


def prepare_wss(state):
    db_get_engineers(state, "wss")


def prepare_ar(state):
    db_get_engineers(state, "ar")


def get_all_engineers(state):
    db_get_all_engineers(state)


def get_all_installers(state):
    db_get_all_installers(state)


def show_my_invitations(state):
    db_get_my_invitations(state)
    state['invitations_section'] = 1
    state['proposals_section'] = 0
    state['current_projects_section'] = 0
    state['declined_projects_section'] = 0
    state['finished_projects_section'] = 0


def show_my_current_projects(state):
    # _get_my_current_projects(state)
    state['invitations_section'] = 0
    state['proposals_section'] = 0
    state['current_projects_section'] = 1
    state['declined_projects_section'] = 0
    state['finished_projects_section'] = 0


def show_my_finished_projects(state):
    # _get_my_finished_projects(state)
    state['invitations_section'] = 0
    state['proposals_section'] = 0
    state['current_projects_section'] = 0
    state['declined_projects_section'] = 0
    state['finished_projects_section'] = 1


def show_my_proposals(state):
    # _get_my_proposals(state)
    state['invitations_section'] = 0
    state['proposals_section'] = 1
    state['current_projects_section'] = 0
    state['declined_projects_section'] = 0
    state['finished_projects_section'] = 0


def show_my_declined_projects(state):
    # _get_my_declined_projects(state)
    state['invitations_section'] = 0
    state['proposals_section'] = 0
    state['current_projects_section'] = 0
    state['declined_projects_section'] = 1
    state['finished_projects_section'] = 0


def request_cv(state, context):
    db_request_cv(state, context)


def connect_w_engineer(state, context):
    logger.info(f"Connecting with engineer: {context['item']}")
    # state["selected_engineers"] += [context["itemId"]]
    # state["selected_engineers"] = list(set(state["selected_engineers"]))


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


def delete_project(state, context):
    db_delete_project(state, context)


def finalise_project(state, context):
    db_finalise_project(state, context)


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
        db_create_user(state)
        admin_log_section(state)


def validate_admin_login(state):
    get_table_as_dataframe(state)
    admin_panel_section(state)


def add_to_subscription(state):
    db_add_to_subscription(state)


def request_for_invitation(state, context):
    state['current_invitation'] = context['item']
    state['current_invitation_id'] = context['itemId']
    state.set_page("request_to_client")


def send_request(state):
    db_send_request(state)


def decline_invitation(state, context):
    db_decline_invitation(state, context)


def show_code_window(state):
    state["subscription"]["code_window"] = 1


def compare_unsubscription_codes(state):
    if state["unsubscribe_code"] == state["subscription"]["code_sent"]:
        state["got_unsubscribe_code"] = 1
    else:
        state["got_unsubscribe_code"] = 0


def delete_subscription(state):
    db_delete_subscription(state)


def show_unsubscribe_window(state):
    state["unsubscribe"]["section"] = 1
    state["subscribe"]["section"] = 0


def show_subscribe_window(state):
    state["unsubscribe"]["section"] = 0
    state["subscribe"]["section"] = 1


def add_guest_message(state):
    db_add_guest_message(state)


def resume_project(state, context):
    db_resume_project(state, context)


def handle_hash_change(state, payload):
    route_vars = payload.get("route_vars")
    if route_vars:
        state.add_notification('info', 'Route vars', route_vars['country'])
        state['country'] = route_vars['country']


def show_help(state):
    state["help_section"] = 1


def hide_help(state):
    state["help_section"] = 0


def switch_to_own_page(state):
    match state["user"]["role"]:
        case "client":
            get_my_messages(state, context=None)
            state.set_page("client_page")
        case "engineer":
            state.set_page("engineer_page")
        case "installer":
            state.set_page("installer_page")


def show_my_relations(state):
    # _get_my_invitations(state)
    ...
    state["my_prospects"] = 1
    state["my_projects"] = 0


def apply_client_proposal(state, context):
    db_apply_client_proposal(state, context)
    db_get_my_invitations(state)


def decline_client_proposal(state, context):
    db_decline_client_proposal(state, context)
    db_get_my_invitations(state)


def prepare_message_context(state, context):
    state["proj_message_context"] = context
    logger.info(f"Message context: {context}")
    change_modal_visibility(state)


def prepare_reply_context(state, context):
    state["proj_message_context"] = context
    logger.info(f"Reply context: {context}")
    change_modal_visibility(state)


def change_modal_visibility(state):
    state["modal_vis"] = not state["modal_vis"]
    state["proj_message"] = None


def add_message(state):
    db_add_message(state)
    change_modal_visibility(state)


def reply_to_message(state, context):
    db_reply_to_message(state)
    change_modal_visibility(state)


def get_my_messages(state, context):
    db_get_my_messages_new(state)
    db_get_my_messages_read(state)


def update_read_date(state, context):
    db_update_read_date(state, context)
    db_get_my_messages_new(state)
    db_get_my_messages_read(state)


def mark_as_unread(state, context):
    db_mark_as_unread(state, context)
    db_get_my_messages_new(state)
    db_get_my_messages_read(state)


def get_screen_size(state):
    state.call_frontend_function("js_scripts", "screen_size", [])
    # state.call_frontend_function("js_scripts", "sendCustomEvent", [])
    # state["screen"]["width"] = screen_size[0]
    # state["screen"]["height"] = screen_size[1]

    # print(f"Screen size: {screen_size}")


def screen_size(state, payload):
    print(f"My event{payload}")


def hide_cookie(state):
    state["cookie_visible"] = False


initial_state = wf.init_state(
    {
        "header": "tbag25a2ixxatzmw",
        "footer": "t06410yhnc7u920g",

        "lang": "E",
        "dic": dic,
        "reg": init_reg,
        "login": init_login,
        "user": init_user,
        "projects": init_projects,
        "engineers": init_engineers,
        "vacancies": init_vacancies,
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
        "fd": ss_dic,

        "help": he,
        # "help_section": 0,

        "reg_vis": ["c", "e", "i"],
        "proj_vis": ["c", "e", "i"],

        "message_switch": 0,
        "proj_message": None,
        "proj_message_context": None,

        "modal_vis": False,

        "eng_menu": None,

        "my_prospects_menu": None,
        "my_projects_menu": None,

        'main_menu': _create_menu("main_menu", main_menu, 0),

        "cookie_visible": True,

        "user_message": {
            "first_name": "",
            "last_name": "",
            "email": "",
            "message": "",
            "timestamps": [],
            "counter": 0
        },

    })

initial_state.import_stylesheet("theme", "/static/custom.css?163")

logger.info("MAIN executed successfully!")
