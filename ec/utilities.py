# -*- coding: utf-8 -*-

import re
import string
import random
import bcrypt
import time
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def valid_email(email):
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


def _send_mail(receiver: str, cc_rec: str, subj: str, html: str):
    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subj
    msg['From'] = "info@power-design.pro"
    msg['To'] = receiver
    msg['Cc'] = cc_rec

    password = "Exdiibt3#Python" #!!!

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
        return err_handler(e)
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


def random_code_alphanumeric(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def err_handler(e: Exception, func=None) -> str:
    """
    :param e: Exception
    :param func: Name of function where exception occurred
    :return: Description like : Module -> Function -> Exception Description
    """
    return f"{e.__traceback__.tb_frame.f_globals['__name__']} -> {func} -> {type(e).__name__}{getattr(e, 'args', None)}"


def hash_password(password: str) -> str:
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



