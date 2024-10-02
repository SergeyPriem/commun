# *-* coding: utf-8 *-*


main_menu = {
    # "_active": 0,

    "about": {
        "E": "About",
        "U": "Про нас",
        "R": "О нас",
        "fun": "go_page"
    },
    "projects": {
        "E": "Projects",
        "U": "Проекти",
        "R": "Проекты",
        "fun": "go_page",
    },
    "engineers": {
        "E": "Engineers",
        "U": "Інженери",
        "R": "Инженеры",
        "fun": "go_page"
    },

    "announcements": {
        "E": "Announcement",
        "U": "Оголошення",
        "R": "Объявление",
        "fun": "go_page"
    },

    "vacancies": {
        "E": "Vacancies",
        "U": "Вакансії",
        "R": "Вакансии",
        "fun": "go_page"
    },

}

eng_menu = {
    # "_active": None,

    "my_prospects": {
        "E": "My Prospects",
        "U": "Мої Перспективи",
        "R": "Мои Перспективы",
        "fun": "_create_prospects_menu",
        "reset": ["my_projects_menu"]
    },

    "my_projects": {
        "E": "My Projects",
        "U": "Мої Проекти",
        "R": "Мои Проекты",
        "fun": "_create_projects_menu",
        "reset": ["my_prospects_menu"]
    },
}

my_prospects_menu = {

    "my_invitations": {
        "E": "My Invitations",
        "U": "Мої Запрошення",
        "R": "Мои Приглашения",
        "fun": None
    },

    "my_proposals": {
        "E": "My Proposals",
        "U": "Мої Пропозиції",
        "R": "Мои Предложения",
        "fun": None
    },

    "my_messages": {
        "E": "My Messages",
        "U": "Мої Повідомлення",
        "R": "Мои Сообщения",
        "fun": None
    },

    "my_cv_requests": {
        "E": "CV Requests",
        "U": "Запити на Резюме",
        "R": "Запросы на Резюме",
        "fun": None
    },

}

my_projects_menu = {

    "my_current_projects": {
        "E": "My Current Projects",
        "U": "Мої Поточні Проекти",
        "R": "Мои Текущие Проекты",
        "fun": None,
    },

    "my_declined_projects": {
        "E": "My Declined Projects",
        "U": "Мої Відхилені Проекти",
        "R": "Мои Отклоненные Проекты",
        "fun": None,
    },

    "my_finished_projects": {
        "E": "My Finished Projects",
        "U": "Мої Завершені Проекти",
        "R": "Мои Завершенные Проекты",
        "fun": None,
    },

    "my_deleted_projects": {
        "E": "My Deleted Projects",
        "U": "Мої Видалені Проекти",
        "R": "Мои Удаленные Проекты",
        "fun": None,
    },

}

client_menu = {
    "my_messages": {
        "E": "My Messages",
        "U": "Мої Повідомлення",
        "R": "Мои Сообщения",
        "fun": "get_my_messages",
        "reset": None,
    },

    "new_engines": {
        "E": "New Engines",
        "U": "Нові інженери",
        "R": "Новые Инженеры",
        "fun": "_create_new_engineers_menu",
        "reset": None
    },
    "new_installers": {
        "E": "New Installers",
        "U": "Нові Монтажники",
        "R": "Новые Монтажники",
        "fun": "_create_new_installers_menu",
        "reset": None
    },

    "all_engineers": {
        "E": "All Engineers",
        "U": "Всі інженери",
        "R": "Все Инженеры",
        "fun": "_create_all_engineers_menu",
        "reset": None
    },

    "all_installers": {
        "E": "All Installers",
        "U": "Всі Монтажники",
        "R": "Все Монтажники",
        "fun": "_create_all_installers_menu",
        "reset": None
    },

    "actual_projects": {
        "E": "Actual Projects",
        "U": "Актуальні Проекти",
        "R": "Актуальные Проекты",
        "fun": "get_actual_own_projects",
        "reset": None
    },

    "finished_projects": {
        "E": "Finished Projects",
        "U": "Завершені Проекти",
        "R": "Завершенные Проекты",
        "fun": "_create_finished_projects_menu",
        "reset": None
    },

    "add_project": {
        "E": "Add Project",
        "U": "Додати Проект",
        "R": "Добавить Проект",
        "fun": "_create_add_project_menu",
        "reset": None
    },

    "edit_account": {
        "E": "Edit Account",
        "U": "Редагувати Акаунт",
        "R": "Редактировать Аккаунт",
        "fun": None,
        "reset": None,
    },

    "help": {
        "E": "Help",
        "U": "Допомога",
        "R": "Помощь",
        "fun": None,
        "reset": None
    },
}
