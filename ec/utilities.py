# -*- coding: utf-8 -*-

import re
import string
import random
import bcrypt
import time


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


def send_email(state):
    email = state["user"]["email"]
    code = state['reg']['code']

    return {
        "status": 200,
        "message": "Email sent successfully"
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



