# -*- coding: utf-8 -*-
import datetime
import time
import bcrypt
import pandas as pd
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from dic import dic
from models import *
from utilities import _hash_password, _err_handler, _valid_email, _send_mail


def _create_user(state):
    """
    Create a new user in the database.

    This function takes the user information from the state dictionary, processes it,
    and attempts to create a new user in the database. If the user already exists,
    it handles the IntegrityError and updates the state with an appropriate message.

    Parameters:
    state (dict): The state dictionary containing user information and other application state.

    Returns:
    int: HTTP status code indicating the result of the operation.
         200 if the user was successfully created, 500 if the user already exists or due to exception.
    """
    if state["user"]["major"]:
        major = ", ".join(state["user"]["major"])
    else:
        major = "-"

    if state["reg_vis"]:
        vis = "".join(state["reg_vis"])
    else:
        vis = "unv"

    try:
        with Session(engine) as session:
            new_user = User(
                first_name=state["user"]["first_name"].strip(),
                last_name=(state["user"]["last_name"] or "-").strip(),
                email=state["user"]["email"].strip(),
                phone=state["user"]["phone"].replace(" ", "").replace("-", "").strip(),
                login=state["user"]["login"].strip(),
                role=state["user"]["role"],
                h_pass=_hash_password(state["user"]["password"].strip()),
                description=(state["user"]["description"] or "-").strip(),
                url=(state["user"]["url"] or "-").strip(),
                date_time=datetime.datetime.now(),
                experience=int(state["user"]["experience"] or 0),
                major=major,
                company=(state["user"]["company"] or "-").strip(),
                lang=state["lang"],
                visibility=vis
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
    """
    Log out the current user by updating their visit log.

    This function retrieves the most recent visit log entry for the current user,
    updates the `date_time_out` field to the current time, and commits the changes
    to the database. If no visit log entry is found, it adds a notification to the state.

    Parameters:
    state (dict): The state dictionary containing user information and other application state.

    Returns:
    None: This function updates the state dictionary directly and commits changes to the database.
    """
    with Session(bind=engine) as session:
        try:
            # Retrieve the most recent visit log entry for the current user
            visit = session.query(
                VisitLog).filter(VisitLog.user_login == state["user"]["login"]
                                 ).order_by(VisitLog.id.desc()).first()
            if visit:
                # Update the date_time_out field to the current time
                visit.date_time_out = datetime.datetime.now()
                # Commit the changes
                session.commit()
            else:
                # Add a notification if no visit log entry is found
                state.add_notification("warning", "Warning!", "User not found")
        except SQLAlchemyError as e:
            # Add a notification if an error occurs
            state.add_notification("warning", "Warning!", f"An error occurred: {e}")


def _get_all_invitations_df(state):
    with Session(bind=engine) as session:
        try:
            stmt = select(Invitation, Project, User).join(Project, Project.id == Invitation.project_id).join(
                User, User.id == Invitation.user_id)
            result = session.execute(stmt)
            invitations = result.scalars().all()
            df = pd.DataFrame([{
                "id": str(invitation.id),
                "project": invitation.project.name,
                "user": invitation.user.login,
                "initiated_by": invitation.initiated_by,
                "status": invitation.status,
                "date_time": invitation.date_time
            } for invitation in invitations])
            return df
        except SQLAlchemyError as e:
            state.add_notification("warning", "Warning!", f"An error occurred: {e}")
            return pd.DataFrame()


def _get_admin_data(state):
    """
    Retrieve data for all users with the role 'admin' and update the state with this information.

    This function queries the database to get all users with the role 'admin'. It then updates the
    state dictionary with the retrieved admin data, including their login, name, description,
    date they joined, and experience.

    Parameters:
    state (dict): The state dictionary containing user information and other application state.

    Returns:
    None: This function updates the state dictionary directly.
    """
    with Session(bind=engine) as session:
        try:
            # Query to select all users with the role 'admin'
            stuff = session.query(User).filter("admin" == User.role).all()
            # Update state with the retrieved admin data
            state["admin"] = {str(stuff[i].login): {
                "name": stuff[i].first_name,
                "description": stuff[i].description,
                "with_us_from": stuff[i].date_time.strftime('%Y-%m-%d'),
                "experience": stuff[i].experience,
            } for i in range(len(stuff))}

        except SQLAlchemyError as e:
            # Add a notification if an error occurs
            state.add_notification(f"An error occurred: {e}")


def admin_panel_section(state):
    """
    Activate the admin panel section in the application state.

    This function sets the relevant sections of the admin panel to their initial states,
    indicating that the admin panel section is active.

    Parameters:
    state (dict): The state dictionary containing user information and other application state.

    Returns:
    None: This function updates the state dictionary directly.
    """
    state["admin"]["reg_sect"] = 0
    state["admin"]["code_sect"] = 0
    state["admin"]["log_sect"] = 0
    state["admin"]["panel_sect"] = 1


def _log_admin(state):
    with Session(bind=engine) as session:
        try:
            # noinspection PyTypeChecker
            current_user = session.query(User).filter(
                User.login == state["user"]["login"],
                User.role == "admin"
            ).first()

        except SQLAlchemyError as e:
            state.add_notification(_err_handler(e, "log_admin"))
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
                    state["message"] = _err_handler(e, "_get_user_data")

                finally:
                    session.close()

                admin_panel_section(state)
            else:
                state.add_notification("warning", "Warning!", "Wrong password...")
        else:
            state.add_notification("warning", "Warning!", "Admin not found...")


def _get_new_engineers(state):
    """
    Retrieve new engineers who joined within the last 30 days and are visible to the user's role.

    This function queries the database to get all users with the role "engineer",
    who joined within the last 30 days, and whose visibility matches the user's role.
    It then updates the state with the retrieved engineers and their details.

    Parameters:
    state (dict): The state dictionary containing user information and other application state.

    Returns:
    None: This function updates the state dictionary directly.
    """
    if state["user"]["logged"]:
        l0 = state["user"]["role"][0]
        if state["new_engineers"] is not None:
            return

        with Session(bind=engine) as session:
            try:
                # Query to select new engineers who joined within the last 30 days
                stuff = session.query(User).filter(
                    User.date_time > (datetime.datetime.now() - datetime.timedelta(days=30)),
                    "engineer" == User.role, User.visibility.contains(l0)
                ).all()
                # Update state with the retrieved engineers
                state["new_engineers"] = {str(stuff[i].login): {
                    "login": stuff[i].login,
                    "name": stuff[i].first_name,
                    "description": stuff[i].description,
                    "with_us_from": stuff[i].date_time.strftime('%Y-%m-%d'),
                    "experience": stuff[i].experience,
                } for i in range(len(stuff))}

            except SQLAlchemyError as e:
                state.add_notification(f"An error occurred: {e}")
    else:
        state.add_notification("warning", "Warning!", dic["not_logged_in"][state['lang']])


def _get_new_installers(state):
    if state["user"]["logged"]:
        l0 = state["user"]["role"][0]
        if state["new_installers"] is not None:
            return
        with Session(bind=engine) as session:
            try:
                stuff = session.query(User).filter(
                    User.date_time > (datetime.datetime.now() - datetime.timedelta(days=30)),
                    'installer' == User.role, User.visibility.contains(l0)
                ).all()
                state["new_installers"] = {str(stuff[i].login): {
                    "login": stuff[i].login,
                    "name": stuff[i].first_name,
                    "description": stuff[i].description,
                    "with_us_from": stuff[i].date_time.strftime('%Y-%m-%d'),
                    "experience": stuff[i].experience,
                } for i in range(len(stuff))}

            except SQLAlchemyError as e:
                state.add_notification(f"An error occurred: {e}")
    else:
        state.add_notification("warning", "Warning!", dic["not_logged_in"][state['lang']])


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


def fill_user_data(state, user):
    state["user"]["first_name"] = user.first_name
    state["user"]["last_name"] = user.last_name
    state["user"]["email"] = user.email
    state["user"]["phone"] = user.phone
    state["user"]["role"] = user.role


def _get_user_data(state):
    with Session(bind=engine) as session:
        try:
            current_user = session.query(User).filter(User.login == state["user"]["login"]).first()

        except SQLAlchemyError as e:
            state["message"] = _err_handler(e, "_get_user_data")
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
                    state["message"] = _err_handler(e, "_get_user_data")
                    session.rollback()

            else:
                state["message"] = "- " + dic["wrong_password"][state["lang"]]
        else:
            state["message"] = "- " + dic["user_not_found"][state["lang"]]


# def _get_my_invitations(state):
#     time1 = time.time()
#
#     if not state['user']['login']:
#         state.add_notification("warning", "Warning!", dic["not_logged_in"][state['lang']])
#         return
#     with Session(bind=engine) as session:
#         try:
#             # Query all invitations for the given user along with the project owner's login and email
#             user_id = session.query(User.id).filter(User.login == state['user']['login']).first()[0]
#             invitations = session.query(Invitation, User.login, User.email).join(
#                 Project, Project.id == Invitation.project_id).join(
#                 User, User.id == Project.owner).filter(Invitation.user_id == user_id).all()
#
#             if not invitations:
#                 state.add_notification("info", "Info", "You have no invitations")
#                 return
#
#             # Initialize an empty dictionary
#             invitations_info = {}
#
#             # Iterate over each invitation
#             for invitation, proj_owner_login, proj_owner_email in invitations:
#                 # Add the invitation info to the dictionary
#                 invitations_info[str(invitation.id)] = {
#                     "project": invitation.projects.name,
#                     "proj_owner": proj_owner_login,
#                     "proj_owner_email": proj_owner_email,  # add the project owner's email
#                     "description": invitation.projects.description,
#                     'comments': invitation.projects.comments,
#                     "initiated_by": invitation.initiated_by,
#                     "last_action_by": invitation.last_action_by.capitalize() if invitation.last_action_by else None,
#                     "last_action_dt": invitation.last_action_dt.strftime('%Y-%m-%d %H:%M'),
#                     'date_time': invitation.date_time.strftime('%Y-%m-%d %H:%M'),  # format the date and time
#                     "status": invitation.status,
#                     "created": invitation.project.created.strftime('%Y-%m-%d'),
#                     "message": "555"
#                 }
#             state['my_invitations'] = invitations_info
#             state['invitations_quantity'] = len(invitations_info) or 0
#
#             state['no_invitations'] = 1 if len(invitations_info) == 0 else 0
#
#             time2 = time.time()
#             print(f"function took {round((time2 - time1) * 1000.0, 2)} ms")
#         except SQLAlchemyError as e:
#             # Log the error and return a user-friendly message
#             print(f"An error occurred: {e}")
#             state.add_notification("error", "Error!", "An unexpected error occurred. Please try again later.")


def _accept_invitation(state, context):
    if not state['user']['login']:
        state.add_notification("warning", "Warning!", dic["not_logged_in"][state['lang']])
        return
    with Session(bind=engine) as session:
        try:
            # Get the invitation to accept
            invitation = session.query(Invitation).filter(Invitation.id == context['itemId']).first()

            # Update the invitation status to 'accepted'
            if invitation.status.endswith('Accepted'):
                state.add_notification("warning", "Warning!", "You have already accepted this invitation")
                return
            invitation.status += (f"\n{state['user']['login']} "
                                  f"({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}): Accepted")

            # Update the last action by and last action date-time
            invitation.last_action_by = state['user']['role']
            invitation.last_action_dt = datetime.datetime.now()

            # Commit the changes to the database
            session.commit()

            # Notify the user that the invitation was accepted
            state.add_notification("info", "Info", "The invitation was accepted successfully")
            _get_my_invitations(state)
        except SQLAlchemyError as e:
            # Log the error and return a user-friendly message
            print(f"An error occurred: {e}")
            state.add_notification("error", "Error!", "An unexpected error occurred. Please try again later.")


def _decline_invitation(state, context):
    if not state['user']['login']:
        state.add_notification("warning", "Warning!", dic["not_logged_in"][state['lang']])
        return
    with Session(bind=engine) as session:
        try:
            # Get the invitation to decline
            invitation = session.query(Invitation).filter(Invitation.id == context['itemId']).first()

            # Update the invitation status to 'declined'
            if invitation.status.endswith('declined'):
                state.add_notification("warning", "Warning!", "You have already declined this invitation")
                return
            invitation.status += (f"\n{state['user']['login']} "
                                  f"({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}): Declined")

            # Update the last action by and last action date-time
            invitation.last_action_by = state['user']['role']
            invitation.last_action_dt = datetime.datetime.now()

            # Commit the changes to the database
            session.commit()

            # Notify the user that the invitation was declined
            state.add_notification("info", "Info", "The invitation was declined successfully")
            _get_my_invitations(state)
        except SQLAlchemyError as e:
            # Log the error and return a user-friendly message
            print(f"An error occurred: {e}")
            state.add_notification("error", "Error!", "An unexpected error occurred. Please try again later.")


def _get_actual_own_projects(state):  # ui
    if not state["user"]["logged"]:
        state.add_notification("warning", "Warning!", dic["not_logged_in"][state['lang']])
        return
    with Session(bind=engine) as session:
        try:
            stmt = select(User).where(User.login == state["user"]["login"])
            result = session.execute(stmt)
            current_user = result.scalars().first()

            stmt = select(Project).where(
                current_user.id == Project.owner,
                "current" == Project.status
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
                "created": cur_projects[i].created.strftime('%Y-%m-%d')
            } for i in range(len(cur_projects))}

        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


def _add_user_message(state):
    if not _valid_email(state["user_message"]["email"]):
        state.add_notification('error', 'Error', "Wrong e-mail. Try again")
        return

    if len(state["user_message"]["message"]) < 10:
        state.add_notification('error', 'Error', "Message is too short. Try again")
        return

    if len(state["user_message"]["first_name"]) < 1:
        state.add_notification('error', 'Error', "First name is too short. Try again")
        return

    if len(state["user_message"]["last_name"]) < 1:
        state.add_notification('error', 'Error', "Last name is too short. Try again")
        return

    if len(state["user_message"]["message"]) > 1000:
        state.add_notification('error', 'Error', "Message is too long. Try again")
        return

    with Session(engine) as session:
        try:
            message = Message(
                first_name=state["user_message"]["first_name"],
                last_name=state["user_message"]["last_name"],
                email=state["user_message"]["email"],
                message=state["user_message"]["message"],
                date_time=datetime.datetime.now()
            )
            session.add(message)
            session.commit()

            reply = _send_mail("info@power-design.pro",
                               "s.priemshiy@gmail.com",
                               "New Message from Site Visitor",
                               f"""
                                <html>
                                    <body>
                                        <h1>Hello!</h1>
                                        <p>
                                        You have got a message from site visitor {state["user_message"]["first_name"]} 
                                        {state["user_message"]["last_name"]} ({state["user_message"]["email"]})
                                        with the following content:
                                        </p>
                                        <h2>
                                            {state["user_message"]["message"]}
                                        </h2>
                                        <p>
                                            by {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
                                        </p>
                                    </body>
                                </html>""")
            if reply == 200:
                state.add_notification("info", "Info!", f"Thank you for your message. "
                                                        f"The administration will be notified")
                state.set_page("about")
            else:
                state.add_notification("warning", "Warning!", "Invitation was not sent...")

            state["user_message"]["first_name"] = None
            state["user_message"]["last_name"] = None
            state["user_message"]["email"] = None
            state["user_message"]["message"] = None
            state.set_page("about")
        except Exception as e:
            state.add_notification('warning', 'Warning', _err_handler(e, 'add_user_message'))


def _delete_subscription(state):
    with Session(engine) as session:
        try:
            unsubscribed = session.query(Subscription).filter(Subscription.email == state["subscription"]["email"])

            if not unsubscribed:
                state.add_notification("warning", "Warning!", "You are not subscribed")
                return

            unsubscribed.delete()
            session.commit()
            state.add_notification('info', 'Info', "You are unsubscribed")
            state["subscription"]["email"] = None
            state.set_page("about")
        except Exception as e:
            state.add_notification('warning', 'Warning', _err_handler(e, 'delete_subscription'))


def _get_new_projects(state):
    print("GET NEW PROJECTS")
    if not state["user"]["logged"]:
        state.add_notification("warning", "Warning!", dic["not_logged_in"][state['lang']])
        return
    with Session(bind=engine) as session:
        try:
            thirty_days_ago = datetime.datetime.now() - datetime.timedelta(days=30)

            cur_projects = session.query(Project, User).join(User, User.id == Project.owner).filter(
                Project.created > thirty_days_ago,
                "current" == Project.status,
                Project.visibility.contains(state["user"]["role"][0])
            ).all()

            proj_len = len(cur_projects)

            if proj_len:
                state['new_proj_quantity'] = proj_len

                state["new_current_projects"] = {
                    str(project.id): {
                        "name": project.name,
                        "owner": user.login,
                        "description": project.description,
                        "status": project.status,
                        "comments": project.comments,
                        "required_specialists": project.required_specialists,
                        "assigned_engineers": project.assigned_engineers,
                        "created": project.created.strftime('%Y-%m-%d'),
                    } for project, user in cur_projects
                }

                state["new_current_projects_view"] = {
                    "content": True,
                    "message": False
                }
            else:
                state['new_proj_quantity'] = 0
                state["new_current_projects_view"] = {
                    "content": False,
                    "message": dic['no_current_proj'][state["lang"]]
                }

        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


def _get_current_projects(state):
    """
    Retrieve all current projects that are visible to the user's role.

    This function queries the database to get all projects with the status "current" and
    visibility that matches the user's role. It then updates the state with the retrieved
    projects and their details.

    Parameters:
    state (dict): The state dictionary containing user information and other application state.

    Returns:
    None: This function updates the state dictionary directly.
    """
    if not state["user"]["logged"]:
        state.add_notification("warning", "Warning!", dic["not_logged_in"][state['lang']])
        return
    with Session(bind=engine) as session:
        try:
            # Query to select all current projects visible to the user's role

            cur_projects = session.query(Project, User).join(User, User.id == Project.owner) \
                .filter(
                "current" == Project.status,
                Project.visibility.contains(state["user"]["role"][0])
            ).all()

            if cur_projects:
                # Update state with the retrieved projects
                state["actual_proj_quantity"] = len(cur_projects)
                state["all_current_projects"] = {
                    str(project.id): {
                        "name": project.name,
                        "owner": user.login,
                        "description": project.description,
                        "status": project.status,
                        "comments": project.comments,
                        "required_specialists": project.required_specialists,
                        "assigned_engineers": project.assigned_engineers,
                        "created": project.created.strftime('%Y-%m-%d'),
                    } for project, user in cur_projects
                }
                state["all_current_projects_message"] = False
            else:
                state["actual_proj_quantity"] = 0
                state["all_current_projects_message"] = dic['no_new_proj'][state["lang"]]

        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


def _get_my_current_projects(state):
    """
    Retrieve the current projects owned by the user and update the state with this information.
    :param state:
    :return:
    """
    if not state["user"]["logged"]:
        state.add_notification("warning", "Warning!", dic["not_logged_in"][state['lang']])
        return
    with Session(bind=engine) as session:
        try:
            stmt = select(User).where(User.login == state["user"]["login"])
            result = session.execute(stmt)
            current_user = result.scalars().first()

            stmt = select(Project).where(
                current_user.id == Project.owner,
                "current" == Project.status
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
                "created": cur_projects[i].created.strftime('%Y-%m-%d')
            } for i in range(len(cur_projects))}

        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


def _get_all_finished_projects(state):
    if not state["user"]["logged"]:
        state.add_notification("warning", "Warning!", dic["not_logged_in"][state['lang']])
        return
    with Session(bind=engine) as session:
        try:
            stmt = (
                select(Project, User).where(
                    "finished" == Project.status).join(User, User.login == state["user"]["login"])
            )
            result = session.execute(stmt)
            fin_projects = result.scalars().all()

            if fin_projects:
                state["all_finished_projects"] = {
                    str(project.id): {
                        "name": project.name,
                        "owner": project.owner.login,
                        "description": project.description,
                        "status": project.status,
                        "comments": project.comments,
                        "required_specialists": project.required_specialists,
                        "assigned_engineers": project.assigned_engineers,
                        "created": project.created.strftime('%Y-%m-%d'),
                    } for project in fin_projects
                }
                state["all_finished_projects_message"] = False

            else:
                state["all_finished_projects"] = None
                state["all_finished_projects_message"] = dic['no_finished_proj'][state["lang"]]

        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


def _create_project(state):
    state_name = state["new_project"]["name"] or False
    state_description = state["new_project"]["description"] or False
    state_comments = state["new_project"]["comments"] or False
    state_required_specialists = state["new_project"]["required_specialists"]
    state_required_specialists = ", ".join(state_required_specialists) if state_required_specialists else "-"
    state_assigned_engineers = "-"
    if all([state_name, state_description, state_comments, state_required_specialists]):
        with Session(bind=engine) as session:
            try:
                stmt = select(User).where(User.login == state["user"]["login"])
                result = session.execute(stmt)
                current_user = result.scalars().first()

                # Check if a project with the same name and description already exists
                existing_project = session.query(Project).filter(
                    Project.name == state_name.strip(),
                    Project.description == state_description.strip(),
                    current_user.id == Project.owner
                ).first()

                if existing_project:
                    state.add_notification("warning", "Warning!", state["dic"]["proj_exists"][state["lang"]])
                    return

                new_project = Project(
                    name=state_name.strip(),
                    owner=current_user.id,
                    description=state_description.strip(),
                    status="current",
                    comments=state_comments.strip(),
                    created=datetime.datetime.now(),
                    required_specialists=state_required_specialists,
                    assigned_engineers=state_assigned_engineers,
                    visibility="".join(state["proj_vis"]) or "unv"
                )
                session.add(new_project)
                session.commit()
                state["add_project"]["show_message"] = 1
                state["add_project"]["show_section"] = 0
                state.add_notification("success", "Info!", state["dic"]["proj_created"][state["lang"]])
            except SQLAlchemyError as e:
                state.add_notification("warning", "Warning!", f"An error occurred: {e}")
    else:
        state.add_notification("warning", "Warning!", "Some fields are empty.")

    if state["add_project"]["show_message"]:
        time.sleep(2)
        state["add_project"]["show_message"] = 0
        state["add_project"]["show_section"] = 1
        state.set_page("client_page")


def _invite(state):
    if not state["user"]["logged"]:
        state.add_notification("warning", "Warning!", dic["not_logged_in"][state['lang']])
        return
    if not state["selected_proj_to_add_eng"]:
        state.add_notification("warning", "Warning!", dic["no_proj_selected"][state["lang"]])
        return
    with Session(bind=engine) as session:
        try:
            invited = session.query(User).filter(User.login == state["selected_eng_for_proj"]).first()
            inviting = session.query(User).filter(User.login == state["user"]["login"]).first()
            project = session.query(Project).filter(Project.id == state['selected_proj_to_add_eng']).first()

            # Check if an invitation with the same project_id, user_id, and proposed_by already exists
            existing_invitation = session.query(Invitation).filter(
                Invitation.project_id == state['selected_proj_to_add_eng'],
                Invitation.user_id == invited.id,
                Invitation.proposed_by == inviting.id,
                Invitation.status == 'pending'
            ).first()

            if existing_invitation:
                # If the invitation already exists, create a warning message and return
                state.add_notification("warning", "Warning!", dic["inv_exists"][state["lang"]])
                return

            # Create a new Invitation object
            new_invitation = Invitation(
                project_id=state['selected_proj_to_add_eng'],
                user_id=invited.id,
                proposed_by=inviting.id,
                status='pending',
                date_time=datetime.datetime.now(),
                last_action_dt=datetime.datetime.now(),
                last_action_by=inviting.id
            )

            # Add the new Invitation object to the session
            session.add(new_invitation)

            # Commit the session to save the changes to the database
            session.commit()

            # Send the invitation email and handle the response
            reply = _send_mail(invited.email,
                               "info@power-design.pro",
                               f"You have been invited to a project by {state['user']['role']} via Power-Design.Pro",
                               f"""
                               <b>Hello, {invited.login}!</b> <br><br>
                               You have been invited &#128077<br><br>
                               Project: {project.name}<br>
                               Invited by: {state['user']['role']} {state['user']['login']}.<br><br>
                               Check your account.
                               <br><br>
                               <b>Power Design Pro Team</b>""")
            if reply == 200:
                state.add_notification("info", "Info!", f"Invitation to user {invited.login} sent successfully")
                state["selected_proj_to_add_eng"] = None
                state["selected_eng_for_proj"] = None
                state.set_page("client_page")
            else:
                state.add_notification("warning", "Warning!", "Invitation was not sent...")
        except Exception as e:
            session.rollback()
            state.add_notification("warning", "Warning!", f"An error occurred: {e}")


def _get_my_invitations(state):
    if not state["user"]["logged"]:
        state.add_notification("warning", "Warning!", dic["not_logged_in"][state['lang']])
        return
    with Session(bind=engine) as session:
        try:
            current_user = session.query(User).filter(User.login == state["user"]["login"]).first()

            my_invitations = session.query(Invitation, Project).join(
                Project, Project.id == Invitation.project_id
            ).filter(
                current_user.id == Invitation.user_id
            ).all()

            if not my_invitations:
                state["my_invitations"] = None
                state["no_invitations_message"] = 1
                return

            state["no_invitations_message"] = 0

            state["my_invitations"] = {str(invitation.id): {
                "project": project.name,
                "description": project.description,
                "status": invitation.status,
                "comments": project.comments,
                "required_specialists": project.required_specialists,
                "assigned_engineers": project.assigned_engineers,
                "created": project.created.strftime('%Y-%m-%d'),
                "owner": session.query(User).get(project.owner).login,
                "proposed_by": session.query(User).get(invitation.proposed_by).login,
            } for invitation, project in my_invitations}

        except SQLAlchemyError as e:
            print(f"An error occurred: {e}, {datetime.datetime.now()}")


def _get_my_proposals(state):
    if not state["user"]["logged"]:
        state.add_notification("warning", "Warning!", dic["not_logged_in"][state['lang']])
        return
    with Session(bind=engine) as session:
        try:
            current_user = session.query(User).filter(User.login == state["user"]["login"]).first()

            my_proposals = session.query(Invitation, Project).join(
                Project, Project.id == Invitation.project_id
            ).filter(
                current_user.id == Invitation.user_id
            ).all()

            if not my_proposals:
                state["my_proposals"] = None
                state["no_proposals_message"] = 1
                return

            state["no_proposals_message"] = 0
            state["my_proposals"] = {str(proposal.id): {
                "project": project.name,
                "description": project.description,
                "status": proposal.status,
                "comments": project.comments,
                "required_specialists": project.required_specialists,
                "assigned_engineers": project.assigned_engineers,
                "created": project.created.strftime('%Y-%m-%d'),
                "owner": session.query(User).get(project.owner).login,
            } for proposal, project in my_proposals}
        except SQLAlchemyError as e:
            print(f"An error occurred: {e}, {datetime.datetime.now()}")


def _apply_client_proposal(state, context):
    if not state["user"]["logged"]:
        state.add_notification("warning", "Warning!", dic["not_logged_in"][state['lang']])
        return
    with Session(bind=engine) as session:
        try:
            proposal = session.query(Invitation).filter(Invitation.id == context['itemId']).first()
            project = session.query(Project).filter(Project.id == proposal.project_id).first()
            project.assigned_engineers = state["user"]["login"]
            proposal.status = "accepted"
            session.commit()
            state.add_notification("info", "Info", "You have accepted the proposal")
            _get_my_proposals(state)
        except SQLAlchemyError as e:
            print(f"An error occurred: {e}, {datetime.datetime.now()}")
            state.add_notification("error", "Error!", "An unexpected error occurred. Please try again later.")


def _decline_client_proposal(state, context):
    if not state["user"]["logged"]:
        state.add_notification("warning", "Warning!", dic["not_logged_in"][state['lang']])
        return
    with Session(bind=engine) as session:
        try:
            proposal = session.query(Invitation).filter(Invitation.id == context['itemId']).first()
            proposal.status = "declined"
            session.commit()
            state.add_notification("info", "Info", "You have declined the proposal")
            _get_my_proposals(state)
        except SQLAlchemyError as e:
            print(f"An error occurred: {e}, {datetime.datetime.now()}")
            state.add_notification("error", "Error!", "An unexpected error occurred. Please try again later.")

def _get_engineers(state, spec):
    with Session(bind=engine) as session:
        try:
            stuff = session.query(User).filter(User.major.contains(spec)).all()
            state[spec] = {str(stuff[i].login): {
                "login": stuff[i].login,
                "name": stuff[i].first_name,
                "description": stuff[i].description,
                "with_us_from": stuff[i].date_time.strftime('%Y-%m-%d'),
                "experience": stuff[i].experience,
            } for i in range(len(stuff))}

        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


def _get_all_engineers(state):
    l0 = state["user"]["role"][0]
    with Session(bind=engine) as session:
        try:
            # Assuming User.visibility is a string and contains roles as single characters
            stuff = session.query(User).filter("engineer" == User.role, User.visibility.contains(l0)).all()
            state["all_engineers"] = {str(stuff[i].login): {
                "login": stuff[i].login,
                "name": stuff[i].first_name,
                "description": stuff[i].description,
                "with_us_from": stuff[i].date_time.strftime('%Y-%m-%d'),
                "experience": stuff[i].experience,
            } for i in range(len(stuff))}

        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


def _get_all_installers(state):
    l0 = state["user"]["role"][0]
    with Session(bind=engine) as session:
        try:
            stuff = session.query(User).filter("installer" == User.role, User.visibility.contains(l0)).all()
            state["all_installers"] = {str(stuff[i].login): {
                "login": stuff[i].login,
                "name": stuff[i].first_name,
                "description": stuff[i].description,
                "with_us_from": stuff[i].date_time.strftime('%Y-%m-%d'),
                "experience": stuff[i].experience,
            } for i in range(len(stuff))}

        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


def _prepare_eng_page(state):
    state['current_invitation'] = None
    state['current_invitation_id'] = None
    state['current_invitation_message'] = None
    _get_my_invitations(state)
    _get_current_projects(state)
    _get_new_projects(state)
    state.set_page("engineer_page")


def _send_request(state):
    with Session(bind=engine) as session:
        try:
            # Get the invitation to wait
            invitation = session.query(Invitation).filter(Invitation.id == state['current_invitation_id']).first()

            final_status = invitation.status + (
                f"\n{state['user']['login']} ({datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}): "
                f"{state['current_invitation_message']}")

            if len(final_status) > 16000:
                state.add_notification("warning",
                                       "Warning!",
                                       "Your messages history is too long. Please, proceed with email communication "
                                       "or ask the admin to clean your previous history by e-mail: "
                                       "info@power-design.pro")
                return
            else:
                invitation.status = final_status

            invitation.last_action_by = state['user']['role']
            invitation.last_action_dt = datetime.datetime.now()

            session.commit()

            _prepare_eng_page(state)

            state.add_notification("info", "Info", "The request was sent successfully")
        except SQLAlchemyError as e:
            # Log the error and return a user-friendly message
            print(f"An error occurred: {e}")
            state.add_notification("error", "Error!", "An unexpected error occurred. Please try again later.")


def _add_to_subscription(state):
    if not _valid_email(state["subscription"]["email"]):
        state.add_notification('error', 'Error', "Wrong e-mail. Try again")
        return

    with Session(engine) as session:
        result = session.query(Subscription.email).filter(Subscription.email == state["subscription"]["email"]).first()
        if result:
            state.add_notification('warning', 'Warning', "You are already subscribed")
            return
        try:
            subscriber = Subscription(
                first_name=state["subscription"]["first_name"] or None,
                last_name=state["subscription"]["last_name"] or None,
                email=state["subscription"]["email"],
                date_time=datetime.datetime.now()
            )
            session.add(subscriber)
            session.commit()
            state.add_notification('info', 'Info', "You are subscribed")
            state["subscription"]["first_name"] = None
            state["subscription"]["last_name"] = None
            state["subscription"]["email"] = None
            state.set_page("about")
        except Exception as e:
            state.add_notification('warning', 'Warning', _err_handler(e, 'add_to_subscription'))


def _offer_service(state, context):
    with Session(bind=engine) as session:
        try:
            user = session.query(User).filter(User.login == state["user"]["login"]).first()
            project = session.query(Project).filter(Project.id == context['itemId']).first()

            # Check if an invitation already exists for this user and project
            existing_invitation = session.query(Invitation).filter(
                user.id == Invitation.user_id,
                project.id == Invitation.project_id
            ).first()

            if existing_invitation:
                state.add_notification('warning', dic['warning'][state['lang']], dic['connected'][state['lang']])
                return

            # Create a new Invitation object
            new_invitation = Invitation(
                project_id=project.id,
                user_id=user.id,
                initiated_by='engineer',
                status='\nPending',
                date_time=datetime.datetime.now(),
                last_action_dt=datetime.datetime.now(),
                last_action_by='engineer'
            )

            # Add the new Invitation object to the session
            session.add(new_invitation)

            # Commit the session to save the changes to the database
            session.commit()
            owner_email = session.query(User.email).filter(project.owner == User.id).first()[0]

            html_content = (
                f"<p>You have got a cooperation proposal from engineer {user.login} for the project {project.name}. "
                f"Check your account.</p><hr>"
                f"<p>Ви отримали пропозицію співпраці від інженера {user.login} для проекту {project.name}. "
                f"Перевірте свій аккаунт.</p><hr>"
                f"<p>Вы получили предложение о сотрудничестве от инженера {user.login} для проекта {project.name}. "
                f"Проверьте свой аккаунт.</p>"
            )

            subject = (f"Cooperation proposal from engineer {user.login} for the project {project.name} |\n "
                       f"Пропозиція співпраці від інженера {user.login} для проекту {project.name} |\n "
                       f"Предложение о сотрудничестве от инженера {user.login} для проекта {project.name}.\n")

            reply = _send_mail(str(owner_email),
                               's.priemshiy@gmail.com',
                               subject,
                               html_content)
            if reply == 200:
                state.add_notification(
                    'info', 'Info',
                    f"{dic['proposal_sent_1'][state['lang']]} {project.name} {dic['proposal_sent_2'][state['lang']]}")

        except Exception as e:
            session.rollback()
            state.add_notification("warning", "Warning!", f"An error occurred: {e}")


def _get_table_as_dataframe(state):
    if state["db_table_name"] == "Invitation":
        df = _get_all_invitations_df(state)
        try:
            df["date_time"] = pd.to_datetime(df["date_time"], unit='ms')
            df["date_time"] = df["date_time"].dt.strftime('%Y-%m-%d %H:%M:%S')
        except KeyError:
            state.add_notification("warning", "Warning!", "Wrong key...")
        state["db_table"] = df
        return

    df = pd.read_sql_table(state["db_table_name"], engine)
    if state["db_table_name"] == "Projects":
        df["created"] = pd.to_datetime(df["created"], unit='ms')
        df["created"] = df["created"].dt.strftime('%Y-%m-%d %H:%M:%S')
        state["db_table"] = df
        return

    if state["db_table_name"] == "Subscription":
        df["date_time"] = pd.to_datetime(df["date_time"], unit='ms')
        df["date_time"] = df["date_time"].dt.strftime('%Y-%m-%d %H:%M:%S')
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


def _request_cv(state, context):
    if not state['user']['login']:
        state.add_notification('warning', "Warning", dic["not_logged_in"][state['lang']])
        return
    with Session(bind=engine) as session:
        try:
            user_login = context["itemId"]
            user = session.query(User).filter(User.login == user_login).first()

            client_login = state['user']['login']
            client = session.query(User).filter(User.login == client_login).first()

            message_en = (f"Client <strong>{client_login}"
                          f"</strong> asks You to provide the CV to his e-mail: {client.email}")
            message_uk = (f"Замовник <strong>{client_login}"
                          f"</strong> просить Вас надати резюме на його e-mail: {client.email}")
            message_ru = (f"Заказчик <strong>{client_login}"
                          f"</strong> просит Вас предоставить резюме на его e-mail: {client.email}")

            html_content = (
                f"<br>"
                f"<p>{message_en}</p><hr>"
                f"<p>{message_uk}</p><hr>"
                f"<p>{message_ru}</p>"
                f"<br>"
                f"<p>Best Regards, Administration</p>"
            )

            reply = _send_mail(user.email,
                               "s.priemshiy@gmail.com",
                               "Request forQ CV from Client | Запит резюме від Замовника | Запрос резюме от Заказчика",
                               html_content)
            if reply == 200:
                state.add_notification("info", "Info!", f"{dic['req_of_cv'][state['lang']]}{user.login}")
                state["selected_proj_to_add_eng"] = None
                state["selected_eng_for_proj"] = None
                state.set_page("client_page")
            else:
                state.add_notification("warning", "Warning!", dic["request_not_sent"][state["lang"]])
        except Exception as e:

            state.add_notification("warning", "Warning!", f"An error occurred: {e}")


def _delete_project(state, context):
    with Session(bind=engine) as session:
        try:
            project = session.query(Project).filter(Project.id == context["itemId"]).first()
            project.status = "deleted"
            project.visibility = "unv"
            project.status_changed = datetime.datetime.now()
            session.commit()
            _get_all_finished_projects(state)
            state.add_notification("info", "Info!", "Project deleted")
        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


def _finalise_project(state, context):
    with Session(bind=engine) as session:
        try:
            project = session.query(Project).filter(Project.id == context["itemId"]).first()
            project.status = "finished"
            project.visibility = "unv"
            project.status_changed = datetime.datetime.now()
            session.commit()
            _get_actual_own_projects(state)
            state.add_notification("info", "Info!", "Project closed")
        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


def _resume_project(state, context):
    with Session(bind=engine) as session:
        try:
            project = session.query(Project).filter(Project.id == context["itemId"]).first()
            project.status = "current"
            project.visibility = "cei"
            project.status_changed = datetime.datetime.now()
            session.commit()
            _get_all_finished_projects(state)
            state.add_notification("info", "Info!", "Project resumed")
        except SQLAlchemyError as e:
            state.add_notification(f"An error occurred: {e}")


def _add_message(state):
    if not state["user"]["logged"]:
        state.add_notification("warning", "Warning!", dic["not_logged_in"][state['lang']])
        return

    if len(state["proj_message"]) > 1000:
        state.add_notification("warning", "Warning!", "Message is too long. Try again")
        return

    context = state["proj_message_context"]

    if state["message_switch"]:
        receiver_login = context["item"]["proposed_by"]
    else:
        receiver_login = context["item"]["owner"]

    with Session(bind=engine) as session:
        try:
            # Query the database for the sender and receiver
            sender = session.query(User).filter(User.login == state["user"]["login"]).first()
            receiver = session.query(User).filter(User.login == receiver_login).first()
            # my_invitations: item.owner; item.proposed_by

            # If both the sender and receiver are found, create the message
            if sender and receiver:
                new_message = Message(
                    sender_id=sender.id,
                    receiver_id=receiver.id,
                    message_text=state["proj_message"],
                    message_dt=datetime.datetime.now()
                )

                # Add the new Message object to the session
                session.add(new_message)

                # Commit the session to save the changes to the database
                session.commit()
                state.set_page("engineer_page")
                print(f"Message from {state['sender_login']} to {state['receiver_login']} added successfully")
            else:
                print("Sender or receiver not found")

        except Exception as e:
            print(f"An error occurred: {e}")