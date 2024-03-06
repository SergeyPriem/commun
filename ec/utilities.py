# -*- coding: utf-8 -*-

import re
import string
import random

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
    code = state['reg_code']
    return {
        "status": 200,
        "message": "Email sent successfully"
    }


def random_code_alphanumeric(length):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))