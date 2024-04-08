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
    "ar": {"E": "Architecture", "U": "Архітектура", "R": "Архитектура"},
    "el": {"E": "Electrical", "U": "Електрика", "R": "Электрика"},
    "ins": {"E": "Instrumentation", "U": "КВПіА", "R": "КИПиА"},
    "low_cur": {"E": "Telecom, F&G", "U": "Зв'язок, пож.безпека", "R": "Связь, пож.безопасность"},
    "plot_plan": {"E": "Plot Plan", "U": "Генплан", "R": "Генплан"},
    "piping_linear": {"E": "Piping-linear", "U": "Магістральні Трубопроводи", "R": "Магистральные Трубопроводы"},
    "piping_area": {"E": "Piping", "U": "Монтаж технолог. обладнання", "R": "Монтаж технолог. оборудования"},
    "hvac": {"E": "HVAC", "U": "ОВіК", "R": "ОВиК"},
    "wss": {"E": "Water Supply", "U": "Водопостачання і Водовідведення", "R": "Водоснабжение и Водоотведение"},
    "term": {"E": "Heat Engineering", "U": "Теплопостачання", "R": "Теплоснабжение"},
    "civil": {"E": "Civil Part", "U": "Будівельна частина", "R": "Строительная часть"}
}


init_new_project = { # new_project
    "name": None,
    "description": None,
    "comments": None,
    "required_specialists": None,
    "assigned_engineers": None
}

