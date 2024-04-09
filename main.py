# -*- coding: utf-8 -*-
import datetime
import re
import time

import bcrypt
import pandas as pd
import streamsync as ss
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from dic import dic
from dic import error_messages as e_m
from init_states import specialities, init_user, init_reg, init_login, init_projects, init_engineers, init_vacancy, \
    specialities_R, specialities_U, specialities_E, init_new_project
from models import engine, User, VisitLog, Projects
from utilities import hash_password, err_handler
from utilities import valid_email, _send_email, random_code_alphanumeric

print(f"You are using the main.py file from {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}")


def get_table_as_dataframe(state):
    df = pd.read_sql_table(state["db_table_name"], engine)
    if state["db_table_name"] == "Projects":
        df["created"] = pd.to_datetime(df["created"], unit='ms')
        df["created"] = df["created"].dt.strftime('%Y-%m-%d %H:%M:%S')
        state["db_table"] = df
        return
    if "h_pass" in df.columns:
        df = df.drop(columns=["h_pass"])

        # df['your_column'] = pd.to_datetime(df['your_column'], unit='s')

        df["date_time"] = pd.to_datetime(df["date_time"], unit='ms')
        df["date_time"] = df["date_time"].dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        df["date_time_in"] = pd.to_datetime(df["date_time_in"], unit='ms')
        df["date_time_in"] = df["date_time_in"].dt.strftime('%Y-%m-%d %H:%M:%S')
        df["date_time_out"] = pd.to_datetime(df["date_time_out"], unit='ms')
        df["date_time_out"] = df["date_time_out"].dt.strftime('%Y-%m-%d %H:%M:%S')

    state["db_table"] = df


def _create_new_user(state):
    if state["user"]["major"]:
        major = ", ".join(state["user"]["major"])
    else:
        major = "-"

    try:
        with Session(engine) as session:
            new_user = User(
                first_name=state["user"]["first_name"].strip(),
                last_name=(state["user"]["last_name"] or "-").strip(),
                email=state["user"]["email"].strip(),
                phone=state["user"]["phone"].replace(" ", "").replace("-", "").strip(),
                login=state["user"]["login"].strip(),
                role=state["user"]["role"],
                h_pass=hash_password(state["user"]["password"].strip()),
                description=(state["user"]["description"] or "-").strip(),
                url=(state["user"]["url"] or "-").strip(),
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
                state.add_notification("warning", "Warning!", "User not found")
        except SQLAlchemyError as e:
            state.add_notification("warning", "Warning!", f"An error occurred: {e}")


def get_actual_own_projects(state):
    if not state["user"]["logged"]:
        state.add_notification("warning", "Warning!", "You are not logged in...")
        return
    with Session(bind=engine) as session:
        try:
            stmt = select(User).where(User.login == state["user"]["login"])
            result = session.execute(stmt)
            current_user = result.scalars().first()

            stmt = select(Projects).where(
                Projects.owner == current_user.id,
                Projects.status == "current"
            )
            result = session.execute(stmt)
            cur_projects = result.scalars().all()

            state["current_own_projects"] = {str(cur_projects[i].id): {
                "name": cur_projects[i].name,
                "description": cur_projects[i].description,
                "status": cur_projects[i].status,
                "comments": cur_projects[i].comments,
                "required_specialists": cur_projects[i].required_specialists,
                "assigned_engineers": cur_projects[i].assigned_engineers,
                "created": cur_projects[i].created.strftime('%d-%m-%Y')
            } for i in range(len(cur_projects))}

        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


def get_actual_own_projects_dict(state):
    get_actual_own_projects(state)
    state["current_own_projects_dict"] = {
        str(key): value["name"]
        for key, value in state["current_own_projects"].items()}


def get_finished_own_projects(state):
    ...


def get_cancelled_own_projects(state):
    ...


def get_suspended_own_projects(state):
    ...


def get_new_current_projects(state):
    if not state["user"]["logged"]:
        state.add_notification("warning", "Warning!", "You are not logged in...")
        return
    with Session(bind=engine) as session:
        try:
            stmt = (
                select(Projects, User)
                .where(
                    Projects.status == "current",
                    Projects.created > (datetime.datetime.now() - datetime.timedelta(days=30))
                )
                .join(User, User.id == Projects.owner)
            )
            result = session.execute(stmt)
            cur_projects = result.scalars().all()

            if cur_projects:

                state["new_current_projects"] = {
                    str(project.id): {
                        "name": project.name,
                        "owner": project.user.login,
                        "description": project.description,
                        "status": project.status,
                        "comments": project.comments,
                        "required_specialists": project.required_specialists,
                        "assigned_engineers": project.assigned_engineers,
                        "created": project.created.strftime('%d-%m-%Y'),

                    } for project in cur_projects
                }
                state["new_current_projects_view"] = {
                    "content": True,
                    "message": False
                }
            else:
                state["new_current_projects_view"] = {
                    "content": False,
                    "message": dic['no_current_proj'][state["lang"]]
                }

        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


def get_all_current_projects(state):
    if not state["user"]["logged"]:
        state.add_notification("warning", "Warning!", "You are not logged in...")
        return
    with Session(bind=engine) as session:
        try:
            stmt = (
                select(Projects, User).where(Projects.status == "current").join(User, User.id == Projects.owner)
            )
            result = session.execute(stmt)
            cur_projects = result.scalars().all()

            if cur_projects:

                state["all_current_projects"] = {
                    str(project.id): {
                        "name": project.name,
                        "owner": project.user.login,
                        "description": project.description,
                        "status": project.status,
                        "comments": project.comments,
                        "required_specialists": project.required_specialists,
                        "assigned_engineers": project.assigned_engineers,
                        "created": project.created.strftime('%d-%m-%Y'),
                    } for project in cur_projects
                }
                state["all_current_projects_message"] = False
            else:
                state["all_current_projects_message"] = dic['no_new_proj'][state["lang"]]

        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


def get_all_finished_projects(state):
    if not state["user"]["logged"]:
        state.add_notification("warning", "Warning!", "You are not logged in...")
        return
    with Session(bind=engine) as session:
        try:
            stmt = (
                select(Projects, User).where(Projects.status == "finished").join(User, User.id == Projects.owner)
            )
            result = session.execute(stmt)
            fin_projects = result.scalars().all()

            if fin_projects:
                state["all_finished_projects"] = {
                    str(project.id): {
                        "name": project.name,
                        "owner": project.user.login,
                        "description": project.description,
                        "status": project.status,
                        "comments": project.comments,
                        "required_specialists": project.required_specialists,
                        "assigned_engineers": project.assigned_engineers,
                        "created": project.created.strftime('%d-%m-%Y'),
                    } for project in fin_projects
                }
                state["all_finished_projects_message"] = False

            else:
                state["all_finished_projects_message"] = dic['no_finished_proj'][state["lang"]]

        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


def create_project(state):
    state_name = state["new_project"]["name"] or False
    state_description = state["new_project"]["description"] or False
    state_comments = state["new_project"]["comments"] or False
    state_required_specialists = state["new_project"]["required_specialists"]
    state_required_specialists = ", ".join(state_required_specialists) if state_required_specialists else "-"
    state_assigned_engineers = "-"
    if all([state_name, state_description, state_comments, state_required_specialists]):
        with Session(bind=engine) as session:
            try:
                # current_user = session.query(User).filter(User.login == state["user"]["login"]).first()
                stmt = select(User).where(User.login == state["user"]["login"])
                result = session.execute(stmt)
                current_user = result.scalars().first()
                new_project = Projects(
                    name=state_name.strip(),
                    owner=current_user.id,
                    description=state_description.strip(),
                    status="current",  # "finished", "cancelled", "suspended"
                    comments=state_comments.strip(),
                    created=datetime.datetime.now(),
                    required_specialists=state_required_specialists,
                    assigned_engineers=state_assigned_engineers
                )
                session.add(new_project)
                session.commit()
                state["add_project"]["show_message"] = 1
                state["add_project"]["show_section"] = 0
            except SQLAlchemyError as e:
                state.add_notification("warning", "Warning!", f"An error occurred: {e}")
    else:
        state.add_notification("warning", "Warning!", "Some fields are empty.")

    if state["add_project"]["show_message"]:
        time.sleep(2)
        state["add_project"]["show_message"] = 0
        state["add_project"]["show_section"] = 1
        state.set_page("client_page")


def _get_admin_data(state):
    with Session(bind=engine) as session:
        try:
            stuff = session.query(User).filter(User.role == "admin").all()
            state["admin"] = {stuff[i].login: {
                "name": stuff[i].first_name,
                "description": stuff[i].description,
                "with_us_from": stuff[i].date_time.strftime('%d-%m-%Y'),
                "experience": stuff[i].experience,
            } for i in range(len(stuff))}

        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


def fill_user_data(state, user):
    state["user"]["first_name"] = user.first_name
    state["user"]["last_name"] = user.last_name
    state["user"]["email"] = user.email
    state["user"]["phone"] = user.phone
    state["user"]["role"] = user.role


def log_admin(state):
    with Session(bind=engine) as session:
        try:
            current_user = session.query(User).filter(
                User.login == state["user"]["login"],
                User.role == "admin"
            ).first()

        except SQLAlchemyError as e:
            state.add_notification(err_handler(e, "log_admin"))
            return

        if current_user:
            if bcrypt.checkpw(str(state["user"]["password"]).encode("utf-8"), current_user.h_pass.encode("utf-8")):

                fill_user_data(state, current_user)

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

                admin_panel_section(state)
            else:
                state.add_notification("warning", "Warning!", "Wrong password...")
        else:
            state.add_notification("warning", "Warning!", "Admin not found...")


def get_new_engineers(state):
    if state["user"]["logged"]:
        if state["new_engineers"] is not None:
            return

        with Session(bind=engine) as session:
            try:
                stuff = session.query(User).filter(
                    User.date_time > (datetime.datetime.now() - datetime.timedelta(days=30)),
                    User.role == "engineer"
                ).all()
                state["new_engineers"] = {stuff[i].login: {
                    "login": stuff[i].login,
                    "name": stuff[i].first_name,
                    "description": stuff[i].description,
                    "with_us_from": stuff[i].date_time.strftime('%d-%m-%Y'),
                    "experience": stuff[i].experience,
                } for i in range(len(stuff))}

            except SQLAlchemyError as e:
                state.add_notification(f"An error occurred: {e}")
    else:
        state.add_notification("warning", "Warning!", "You are not logged in...")


def get_new_installers(state):
    if state["user"]["logged"]:
        if state["new_installers"] is not None:
            return
        with Session(bind=engine) as session:
            try:
                stuff = session.query(User).filter(
                    User.date_time > (datetime.datetime.now() - datetime.timedelta(days=30)),
                    User.role == "installer"
                ).all()
                state["new_installers"] = {stuff[i].login: {
                    "login": stuff[i].login,
                    "name": stuff[i].first_name,
                    "description": stuff[i].description,
                    "with_us_from": stuff[i].date_time.strftime('%d-%m-%Y'),
                    "experience": stuff[i].experience,
                } for i in range(len(stuff))}

            except SQLAlchemyError as e:
                state.add_notification(f"An error occurred: {e}")
    else:
        state.add_notification("warning", "Warning!", "You are not logged in...")


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

            fill_user_data(state, current_user)

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

    if state["user"]["role"] == 'admin':
        state.add_notification("warning", "Warning!", "Wrong role...")

        quit_fun(state)
        state.set_page("about")

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

        if state["user"]["role"] == 'admin':
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
    state['reg']['code_sent'] = random_code_alphanumeric(6)

    reply = _send_email(state)
    if reply['status'] == 200:
        state["reg"]["code_section"] = 1
    else:
        state["reg"]["code_section"] = 0


def _validate_phone_number(input_string):
    pattern = re.compile(r'^\+\d{12}$')
    if pattern.match(input_string):
        return True
    return False


def _basic_data_validation(state):
    troubles = []

    if state["user"]['first_name']:
        if len(state["user"]['first_name']) <= 1:
            troubles.append(e_m["first_name"])
    else:
        troubles.append(e_m["first_name_2"])

    if not valid_email(state["user"]['email']):
        troubles.append(e_m["short_mail"])

    if state["user"]['phone']:
        state["user"]['phone'] = state["user"]['phone'].replace(" ", "").replace("-", "").strip()
        if not _validate_phone_number(state["user"]['phone']):
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

    return troubles


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


def _get_engineers(state, spec):
    with Session(bind=engine) as session:
        try:
            stuff = session.query(User).filter(User.major.contains(spec)).all()
            state[spec] = {stuff[i].login: {
                "login": stuff[i].login,
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


def prepare_ar(state):
    _get_engineers(state, "ar")


def get_all_engineers(state):
    with Session(bind=engine) as session:
        try:
            stuff = session.query(User).filter(User.role == "engineer").all()
            state["all_engineers"] = {stuff[i].login: {
                "login": stuff[i].login,
                "name": stuff[i].first_name,
                "description": stuff[i].description,
                "with_us_from": stuff[i].date_time.strftime('%d-%m-%Y'),
                "experience": stuff[i].experience,
            } for i in range(len(stuff))}

        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


def get_all_installers(state):
    with Session(bind=engine) as session:
        try:
            stuff = session.query(User).filter(User.role == "installer").all()
            state["all_installers"] = {stuff[i].login: {
                "login": stuff[i].login,
                "name": stuff[i].first_name,
                "description": stuff[i].description,
                "with_us_from": stuff[i].date_time.strftime('%d-%m-%Y'),
                "experience": stuff[i].experience,
            } for i in range(len(stuff))}

        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


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
    print(f"context['itemId']={context["itemId"]} at {datetime.datetime.now()}")
    state["selected_eng_for_proj"] = str(context["itemId"])
    state.set_page("invite_to_project")


def admin_log_section(state):
    state["admin"]["reg_sect"] = 0
    state["admin"]["code_sect"] = 0
    state["admin"]["log_sect"] = 1
    state["admin"]["panel_sect"] = 0


def admin_panel_section(state):
    state["admin"]["reg_sect"] = 0
    state["admin"]["code_sect"] = 0
    state["admin"]["log_sect"] = 0
    state["admin"]["panel_sect"] = 1


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
    ...
    get_table_as_dataframe(state)
    admin_panel_section(state)


initial_state = ss.init_state(
    {
        "message": None,
        "lang": "E",
        "dic": dic,

        "db_table": None,
        "db_table_name": None,

        "reg": init_reg,
        "login": init_login,
        "user": init_user,
        "projects": init_projects,
        "engineers": init_engineers,
        "vacancy": init_vacancy,
        "specs": specialities_E,
        "new_project": init_new_project,

        "ar": None,  # "Architecture",
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
        "new_installers": None,
        "trusted_engineers": None,
        "viewed_engineers": None,

        "admin": {
            "reg_sect": 0,
            "code_sect": 0,
            "log_sect": 0,
            "panel_sect": 0
        },

        "add_project": {
            "show_section": 1,
            "show_message": 0,
        },

        "current_own_projects": {
            "name": None,
            "description": None,
            "status": None,
            "comments": None,
            "required_specialists": None,
            "assigned_engineers": None,
            "created": None
        },

        "new_current_projects": None,
        "all_current_projects": None,
        "all_finished_projects": None,
        "all_engineers": None,
        "all_installers": None,

        "new_current_projects_message": None,
        "all_current_projects_message": None,
        "all_finished_projects_message": None,
        "all_engineers_message": None,
        "all_installers_message": None,
        "current_own_projects_dict": None,
        "selected_proj_to_add_eng": None,
        "selected_eng_for_proj": None,
    }
)

initial_state.import_stylesheet("theme", "/static/custom.css?50")

print("Code executed successfully!")
