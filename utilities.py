# -*- coding: utf-8 -*-
import os
import re
import string
import random
import bcrypt
import time
import smtplib
from dic import error_messages as e_m
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

load_dotenv()


def _valid_email(email):
    """
    Validates an email address using a regular expression.

    Args:
        email (str): The email address to validate.

    Returns:
        bool: True if the email is valid, False otherwise.
    """

    if not email:
        return False

    regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.fullmatch(regex, email))


def _send_mail(receiver: str, cc_rec: str, subj: str, html: str) -> None | str | int:
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subj
    msg['From'] = "info@power-design.pro"
    msg['To'] = receiver
    msg['Cc'] = cc_rec

    password = os.getenv('EMAIL_SECRET')

    # Record the MIME types of both parts - text/plain and text/html.
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    msg.attach(part2)

    # Send the message via local SMTP server.
    s = smtplib.SMTP_SSL('smtp.titan.email', 465)

    try:
        s.login(msg['From'], password)
        # sendmail function takes 3 arguments: sender's address, recipient's address
        # and message to send - here it is sent as one string.
        s.sendmail(msg['From'], [receiver, cc_rec], msg.as_string())
        return 200
    except Exception as e:
        s.quit()
        return _err_handler(e)

    finally:
        s.quit()


def _send_email(state):
    if state["user"]["role"] == "admin":
        html = (f"<h2>New admin is registering with code: {state['reg']['code_sent']}</h2>"
                f"<p>First name: {state['user']['first_name']}</p>"
                f"<p>Last name: {state['user']['last_name']}</p>"
                f"<p>Login: {state['user']['login']}</p>"
                f"<p>Email: {state['user']['email']}</p>")

        subject = f"Confirmation code for SITE ADMIN of power-design.pro"

        reply = _send_mail(receiver="s.priemshiy@gmail.com", html=html, subj=subject, cc_rec="p.s@email.ua")

    else:

        html = (f"<h2>Your confirmation code is: {state['reg']['code_sent']}</h2>"
                f"If you got this email by mistake, delete it...")

        subject = f"Confirmation code for site power-design.pro"

        reply = _send_mail(receiver=state["user"]["email"], html=html, subj=subject, cc_rec="s.priemshiy@gmail.com")

    if reply == 200:
        return {
            "status": 200,
            "message": "Email sent successfully"
        }
    else:
        return {
            "status": 500,
            "message": "Something went wrong while  sending email"
        }


def _random_code_alphanumeric(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def _err_handler(e: Exception, func=None) -> str:
    """
    :param e: Exception
    :param func: Name of function where exception occurred
    :return: Description like : Module -> Function -> Exception Description
    """
    return f"{e.__traceback__.tb_frame.f_globals['__name__']} -> {func} -> {type(e).__name__}{getattr(e, 'args', None)}"


def _hash_password(password: str) -> str:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode()


def timing(f):
    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        print(
            "{:s} function took {:.3f} ms".format(f.__name__, (time2 - time1) * 1000.0)
        )
        return ret

    return wrap


def _validate_phone_number(input_string):
    pattern = re.compile(r'^\+\d{11,12}$')
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

    if not _valid_email(state["user"]['email']):
        troubles.append(e_m["short_mail"])

    if state["user"]['phone']:
        state["user"]['phone'] = state["user"]['phone'].replace(" ", "").replace("-", "").strip()
        if not _validate_phone_number(state["user"]['phone']):
            troubles.append(e_m["wrong_phone"])
    else:
        troubles.append(e_m["empty_phone"])

    if state["user"]['login']:
        if state["user"]['login'].isdigit():
            troubles.append(e_m["only_digits"])
        if len(state["user"]['login']) < 3:
            troubles.append(e_m["short_login"])
    else:
        troubles.append(e_m["empty_login"])

    if state["user"]['password'] is None:
        troubles.append(e_m["empty_password"])

    if state["user"]['password'] != state["user"]['password2']:
        troubles.append(e_m["different_passwords"])

    return troubles
