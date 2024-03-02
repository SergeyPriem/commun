import streamsync as ss
import re

# This is a placeholder to get you started or refresh your memory.
# Delete it or adapt it as necessary.
# Documentation is available at https://streamsync.cloud

# Shows in the log when the app starts
print("Hello world!")


# Its name starts with _, so this function won't be exposed
def _update_message(state):
    is_even = state["counter"] % 2 == 0
    message = ("+Even" if is_even else "-Odd")
    state["message"] = message


def decrement(state):
    state["counter"] -= 1
    _update_message(state)


def increment(state):
    state["counter"] += 1
    # Shows in the log when the event handler is run
    print(f"The counter has been incremented.")
    _update_message(state)


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


def send_confirmation_code(state):
    ...
    return "Confirm your email by entering received code"


def register_user(state):
    troubles = []
    if not valid_email(state["user"]['email']):
        troubles.append("Wrong email address")
    try:
        if len(state["user"]['first_name']) <= 1:
            troubles.append("Wrong first name")
    except:
        troubles.append("Wrong first name")

    try:
        if len(state["user"]['phone']) < 10:
            troubles.append("Wrong phone number")
    except:
        troubles.append("Wrong phone number")

    if state["user"]['role'] is None:
        troubles.append("Role is not selected")

    if state["user"]['password'] is None:
        troubles.append("Wrong password")

    if state["user"]['password'] != state["user"]['password2']:
        troubles.append("Passwords not matching")

    if len(troubles) > 0:
        troubles_text = "\n".join(troubles)
        state["email_confirmation"]["show"] = True
        state["email_confirmation"]["message"] = troubles_text
    else:
        state["user"]['status'] = "new"
        state["email_confirmation"]["show"] = True
        state["email_confirmation"]["message"] = send_confirmation_code(state)


# Initialise the state

# "_my_private_element" won't be serialised or sent to the frontend,
# because it starts with an underscore

initial_state = ss.init_state({
    "my_app": {
        "title": "My App"
    },
    "_my_private_element": 1337,
    "message": None,

    "email_confirmation": {
        "show": False,
        "message": None
    },

    "counter": 26,
    "user": {
        "status": None,  # new or current
        "first_name": None,
        "last_name": None,
        "email": None,
        "phone": None,
        "role": None,
        "login": None,
        "password": None,
        "password2": None,
        "logged": False,
        'service_page': None
    },

})

initial_state.import_stylesheet("theme", "/static/custom.css?6")

_update_message(initial_state)
