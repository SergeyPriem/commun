# -*- coding: utf-8 -*-
import datetime
import time

import bcrypt
import streamsync as ss
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from models import engine, User, VisitLog, Projects
from utilities import valid_email, _send_email, random_code_alphanumeric, err_handler, hash_password
from dic import dic
from dic import error_messages as e_m
from init_states import specialities, init_user, init_reg, init_login, init_projects, init_engineers, init_vacancy, \
    specialities_R, specialities_U, specialities_E, init_new_project

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
            state["message"] = "- " + dic["wrong_password"][state["lang"]]
    else:
        state["message"] = "- " + dic["user_not_found"][state["lang"]]


def log_user(state):
    _get_user_data(state)

    if state["user"]["logged"]:

        state["lang"] = state["user"]["lang"]

        if state["user"]["role"] == 'client':
            state.set_page('client_page')
            state["engineers"]["content"] = 1
            state["engineers"]["warning"] = 0
            state["projects"]["content"] = 0
            state["projects"]["warning"] = 1
            state["vacancy"]["content"] = 0
            state["vacancy"]["warning"] = 1

        if state["user"]["role"] == 'engineer':
            state.set_page('engineer_page')
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


def _add_user_to_db(state):
    if state["user"]["major"]:
        major = ", ".join(state["user"]["major"])
    else:
        major = "-"

    try:
        with Session(engine) as session:
            new_user = User(
                first_name=state["user"]["first_name"].strip(),
                last_name=state["user"]["last_name"].strip() or "-",
                email=state["user"]["email"].strip(),
                phone=state["user"]["phone"].strip(),
                login=state["user"]["login"].strip(),
                role=state["user"]["role"].strip(),
                h_pass=hash_password(state["user"]["password"].strip()),
                description=(state["user"]["description"] or "-").strip(),
                url=state["user"]["url"].strip() or "-",
                date_time=datetime.datetime.now(),
                experience=int(state["user"]["experience"] or 0),
                major=major,
                company=(state["user"]["company"] or "-").strip(),
                lang=state["lang"]
            )
            session.add(new_user)
            session.commit()

        state["reg"]["db_message_text"] = dic["user_added"][state["lang"]]
        return 200
    except IntegrityError:
        state["reg"]["db_message_text"] = dic["user_exists"][state["lang"]]
        return 500
    finally:
        session.close()


def validate_email_by_code(state):
    if state['reg']['code_sent'] == state['reg']['code_entered']:

        state["reg"]["code_message"] = "+ " + dic["code_confirmed"][state["lang"]]

        if _add_user_to_db(state) == 200:
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
    state['reg']['code_sent'] = random_code_alphanumeric(6)

    reply = _send_email(state)
    if reply['status'] == 200:
        state["reg"]["code_section"] = 1
    else:
        state["reg"]["code_section"] = 0


def validate_reg_data(state):
    """Check registration data and change states"""
    troubles = []
    lang = state["lang"]
    if state["user"]['first_name']:
        if len(state["user"]['first_name']) <= 1:
            troubles.append(e_m["first_name"])
            # state.add_notification(type="warning", title="Warning!", message=e_m["first_name"][lang])

    else:
        troubles.append(e_m["first_name_2"])
        # state.add_notification(type="warning", title="Warning!", message=e_m["first_name_2"][lang])

    if not valid_email(state["user"]['email']):
        troubles.append(e_m["short_mail"])
        # state.add_notification(type="warning", title="Warning!", message=e_m["short_mail"][lang])

    if state["user"]['phone']:
        if len(state["user"]['phone']) < 10:
            troubles.append(e_m["wrong_phone"])
            # state.add_notification(type="warning", title="Warning!", message=e_m["wrong_phone"][lang])
    else:
        troubles.append(e_m["empty_phone"])
        # state.add_notification(type="warning", title="Warning!", message=e_m["empty_phone"][lang])
    if state["user"]['login']:
        if len(state["user"]['login']) < 3:
            troubles.append(e_m["short_login"])
            # state.add_notification(type="warning", title="Warning!", message=e_m["short_login"][lang])
    else:
        troubles.append(e_m["empty_login"])
        # state.add_notification(type="warning", title="Warning!", message=e_m["empty_login"][lang])
    if state["user"]['password'] is None:
        troubles.append(e_m["empty_password"])
        # state.add_notification(type="warning", title="Warning!", message=e_m["empty_password"][lang])

    if state["user"]['password'] != state["user"]['password2']:
        troubles.append(e_m["different_passwords"])
        # state.add_notification(type="warning", title="Warning!", message=e_m["different_passwords"][lang])

    if state["user"]['engineer']:
        if not state["user"]['major']:
            troubles.append(e_m["empty_speciality"])
            # state.add_notification(type="warning", title="Warning!", message=e_m["empty_speciality"][lang])

    if not state["user"]['client']:
        if state["user"]['experience']:
            if state["user"]['experience'] < 1 or state["user"]['experience'] > 80:
                troubles.append(e_m["wrong_experience"])
                # state.add_notification(type="warning", title="Warning!", message=e_m["wrong_experience"][lang])
        else:
            troubles.append(e_m["empty_experience"])
            # state.add_notification(type="warning", title="Warning!", message=e_m["empty_experience"][lang])

        if state["user"]['description']:
            if len(state["user"]['description']) < 10:
                troubles.append(e_m["short_description"])
                # state.add_notification(type="warning", title="Warning!", message=e_m["short_description"][lang])
        else:
            troubles.append(e_m["empty_description"])
            # state.add_notification(type="warning", title="Warning!", message=e_m["empty_description"][lang])

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
                state.add_notification("User not found")
        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


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


def _get_engineers(state, spec):
    with Session(bind=engine) as session:
        try:
            stuff = session.query(User).filter(User.major.contains(spec)).all()
            state[spec] = {stuff[i].login: {
                "name": stuff[i].first_name,
                "description": stuff[i].description,
                "with_us_from": stuff[i].date_time.strftime('%d-%m-%Y'),
                "experience": stuff[i].experience,
            } for i in range(len(stuff))}

        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


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


def connect_w_engineer(state, context):
    state["selected_engineers"] += [context["itemId"]]
    state["selected_engineers"] = list(set(state["selected_engineers"]))


def create_project(state):
    # Assuming you have the same 'Projects' class and 'Base' as in your previous code
    state_name = state["new_project"]["name"] or False
    state_description = state["new_project"]["description"] or False
    state_comments = state["new_project"]["comments"] or False
    state_required_specialists = state["new_project"]["required_specialists"]
    state_required_specialists = ", ".join(state_required_specialists) if state_required_specialists else "-"
    state_assigned_engineers = "-"
    if all([state_name, state_description, state_comments, state_required_specialists]):
        with Session(bind=engine) as session:
            try:
                new_project = Projects(
                    name=state_name.strip(),
                    owner=state["user"]["login"],
                    description=state_description.strip(),
                    comments=state_comments.strip(),
                    required_specialists=state_required_specialists,
                    assigned_engineers=state_assigned_engineers
                )
                session.add(new_project)
                session.commit()
            except SQLAlchemyError as e:
                state.add_notification(f"An error occurred: {e}")
    else:
        state.add_notification("warning", "Warning!", "Some fields are empty.")


def get_new_engineers(state):
    with Session(bind=engine) as session:
        try:
            stuff = session.query(User).filter(
                User.date_time > (datetime.datetime.now() - datetime.timedelta(days=30)),
                User.role == "engineer"
            ).all()
            state["new_engineers"] = {stuff[i].login: {
                "name": stuff[i].first_name,
                "description": stuff[i].description,
                "with_us_from": stuff[i].date_time.strftime('%d-%m-%Y'),
                "experience": stuff[i].experience,
            } for i in range(len(stuff))}

        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


initial_state = ss.init_state(
    {
        "message": None,
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

        "el": None,
        "ins": None,
        "low_cur": None,
        "plot_plan": None,
        "piping_linear": None,
        "piping_area": None,
        "hvac": None,
        "wss": None,
        "term": None,
        "civil": None,
        "selected_engineers": [],
        "new_engineers": None,
        "trusted_engineers": None,
        "viewed_engineers": None,
    }
)

initial_state.import_stylesheet("theme", "/static/custom.css?40")
