# -*- coding: utf-8 -*-

init_user = {
    "first_name": None,
    "last_name": None,
    "email": None,
    "phone": None,
    "role": None,
    "login": None,
    "password": None,
    "password2": None,
    "experience": None,
    "major": None,  # speciality
    "description": None,  # description for project or experience
    "company": None,
    "logged": 0,
    "not_logged": 1,
    "message": None,
    "engineer": 0,
    "client": 0,
    "installer": 0
}

init_reg = {
    "data_ok": 0,
    "data_error": 0,
    "data_error_message": "",
    "code_section": 0,
    "code_message": None,
    "code_ok": 0,
    "code_error": 0,
    "db_message": 0,
    "db_message_text": "",
    "code_sent": None,
    "code_entered": None
}

init_login = {
    "form": 1,
    "data_ok": 0,
    "data_error": 0,
    "data_error_message": "",
    "code": 0,
    "code_ok": 0,
    "code_error": 0,
    "db_message": 0,
    "db_message_text": ""
}

init_projects = init_engineers = init_vacancy = dict(warning=1, content=0)

specialities = {
        "el": "Electrical Part",
        "ins": "Instrumentation",
        "telecom": "Telecom",
        "plot_plan": "Plot Plan",
        "piping_linear": "Piping - linear",
        "piping_area": "Piping",
        "hvac": "HVAC",
        "wss": "Water Supply",
        "term": "Heat Engineering"
    }


specialities_E = {
        "el": "Electrical Part",
        "ins": "Instrumentation",
        "telecom": "Telecom",
        "plot_plan": "Plot Plan",
        "piping_linear": "Piping - linear",
        "piping_area": "Piping",
        "hvac": "HVAC",
        "wss": "Water Supply",
        "term": "Heat Engineering"
    }

specialities_U = {
    "el": "Електропостачання",
    "ins": "КВПіА",
    "telecom": "Зв'язок",
    "plot_plan": "Генплан",
    "piping_linear": "Лінійна частина трубопроводів",
    "piping_area": "Монтаж технолог. обладнання",
    "hvac": "ОВіК",
    "wss": "Водопостачання і Водовідведення",
    "term": "Теплопостачання"
}

specialities_R = {
    "el": "Электроснабжение",
    "ins": "КИПиА",
    "telecom": "Связь",
    "plot_plan": "Генплан",
    "piping_linear": "Линейная часть трубопроводов",
    "piping_area": "Монтаж технолог. оборудования",
    "hvac": "ОВиК",
    "wss": "Водоснабжение и Водоотведение",
    "term": "Теплоснабжение"
}
