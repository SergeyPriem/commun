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
    "url": None,
    "message": None,
    "engineer": 0,
    "client": 0,
    "installer": 0,
    "lang": "E"
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
        "low_cur": "Telecom",
        "plot_plan": "Plot Plan",
        "piping_linear": "Piping - linear",
        "piping_area": "Piping",
        "hvac": "HVAC",
        "wss": "Water Supply",
        "term": "Heat Engineering",
        "civil": "Civil Part"
    }


specialities_E = {
        "ar": "Architecture",
        "el": "Electrical",
        "ins": "Instrumentation",
        "low_cur": "Telecom, F&G",
        "plot_plan": "Plot Plan",
        "piping_linear": "Piping-linear",
        "piping_area": "Piping",
        "hvac": "HVAC",
        "wss": "Water Supply",
        "term": "Heat Engineering",
        "civil": "Civil Part"
    }

specialities_U = {
    "ar": "Архітектура",
    "el": "Електрика",
    "ins": "КВПіА",
    "low_cur": "Зв'язок, пож.безпека",
    "plot_plan": "Генплан",
    "piping_linear": "Магістральні Трубопроводи",
    "piping_area": "Монтаж технолог. обладнання",
    "hvac": "ОВіК",
    "wss": "Водопостачання і Водовідведення",
    "term": "Теплопостачання",
    "civil": "Будівельна частина"
}

specialities_R = {
    "ar": "Архитектура",
    "el": "Электрика",
    "ins": "КИПиА",
    "low_cur": "Связь, пож.безопасность",
    "plot_plan": "Генплан",
    "piping_linear": "Магистральные Трубопроводы",
    "piping_area": "Монтаж технолог. оборудования",
    "hvac": "ОВиК",
    "wss": "Водоснабжение и Водоотведение",
    "term": "Теплоснабжение",
    "civil": "Строительная часть"
}

init_new_project = { # new_project
    "name": None,
    "description": None,
    "comments": None,
    "required_specialists": None,
    "assigned_engineers": None
}

