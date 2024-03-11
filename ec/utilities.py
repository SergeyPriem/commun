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

dic = {
    'community': {
        "E": "ENGINEERING COMMUNITY",
        "U": "ІНЖЕНЕРНА СПІЛКА",
        "R": "СООБЩЕСТВО ИНЖЕНЕРОВ"
    },

    "about_us": {
        "E": "About Us",
        "U": "Про Нас",
        "R": "О Нас"
    },

    "mission": {
        "E": "We help Clients and Engineers find common interests",
        "U": "Ми допомагаємо знайти спільні інтереси Замовникам і Інженерам",
        "R": "Мы помогаем  найти общие интересы Заказчикам и Инженерам"
    },

    "mission_descr": {
        "E": "We specialize in helping customers and engineers find each other. Our team searches and connects "
             "customers looking for professional engineers with talented engineers ready to take on a variety "
             "of projects. We understand that finding the right engineer can be a difficult task for the customer, "
             "while at the same time, finding an interesting project can be a challenge for the engineer. Our goal "
             "is to simplify this process, make it more efficient and effective. We strive to create a platform "
             "where customers and engineers can easily find each other, discuss project details and collaborate "
             "successfully. If you are looking for an Engineer or ready to take on a new Project, contact us - we will "
             "help you find the perfect solution for your business.",

        "U": "Ми спеціалізуємося на тому, щоб допомагати Замовникам та Інженерам знаходити один одного. Наша команда "
             "займається пошуком та зв'язком між Замовниками, які шукають професійних Інженерів, та талановитими "
             "Інженерами, готовими взятися за різноманітні Проекти. Ми розуміємо, що пошук відповідного Інженера "
             "може бути складним завданням для Замовника, в той же час знайти цікавий Проект може бути викликом "
             "для Інженера. Наша мета – спростити цей процес, зробити його більш ефективним та результативним. "
             "Ми прагнемо створити платформу, де Замовники та Інженери можуть легко знайти один одного, обговорити "
             "деталі проекту та успішно співпрацювати. Якщо ви шукаєте Інженера або готові взяти участь у новому "
             "Проекті, зверніться до нас – ми допоможемо вам знайти ідеальне рішення для вашого бізнесу.",

        "R": "Мы специализируемся на том, чтобы помогать Заказчикам и Инженерам находить друг друга. "
             "Наша команда занимается поиском и связью между заказчиками, которые ищут профессиональных Инженеров, "
             "и талантливыми Инженерами, готовыми взяться за разнообразные проекты. Мы понимаем, что поиск подходящего "
             "Инженера может быть сложной задачей для заказчика, в то же время, найти интересный проект может быть "
             "вызовом для Инженера. Наша цель - упростить этот процесс, сделать его более эффективным и результативным. "
             "Мы стремимся создать платформу, где заказчики и Инженеры могут легко найти друг друга, обсудить детали "
             "проекта и успешно сотрудничать. Если вы ищете Инженера или готовы принять участие в новом проекте, "
             "обратитесь к нам - мы поможем вам найти идеальное решение для вашего бизнеса."
    },




    "projects": {
        "E": "Projects",
        "U": "Проекти",
        "R": "Проекты"
    },

    "engineers": {
        "E": "Engineers",
        "U": "Інженери",
        "R": "Инженеры"
    },

    "vacancy": {
        "E": "Vacancies",
        "U": "Вакансії",
        "R": "Вакансии"
    },

    "log_in": {
        "E": "Login",
        "U": "Вхід",
        "R": "Вход"
    },

    "reg": {
        "E": "Registration",
        "U": "Реєстрація",
        "R": "Регистрация"
    },

    "quit": {
        "E": "Log Out",
        "U": "Вихід",
        "R": "Выход"
    },

    'our_engs': {
        "E": "OUR ENGINEERS",
        "U": "НАШІ ІНЖЕНЕРИ",
        "R": 'НАШИ ИНЖЕНЕРЫ'
    },

    "trusted_engs": {
        "E": "Engineers you can trust!",
        "U": "Інженери, яким можна довіряти!",
        "R": 'Инженеры, которым можно доверять!'
    },

    "trusted_descr": {
        "E":
            """
            <h4>Because we:</h4>
            <ul>
            <li style="margin: 1em;">Know them personally and are confident in their professionalism</li>
            <li style="margin: 1em;">Check their experience and skills</li>
            <li style="margin: 1em;">Learn their Projects</li>
            <li style="margin: 1em;">Rely on Customers' feedback</li>
            <li style="margin: 1em;">Communicating</li>
            </ul>
            """,
        "U":
            """
            <h4>Тому що ми:</h4>
            <ul>
            <li style="margin: 1em;">Знаємо їх особисто і впевнені в їх професіоналізмі</li>
            <li style="margin: 1em;">Перевіряємо їх досвід і навички</li>
            <li style="margin: 1em;">Вивчаємо їх проекти</li>
            <li style="margin: 1em;">Спираємося на відгуки Замовників</li>
            <li style="margin: 1em;">Спілкуємось</li>
            </ul>
            """,
        "R":
            """
            <h4>Потому что мы:</h4>
            <ul>
            <li style="margin: 1em;">Знаем их лично и уверены в их профессионализме</li>
            <li style="margin: 1em;">Проверяем их опыт и навыки</li>
            <li style="margin: 1em;">Изучаем их проекты</li>
            <li style="margin: 1em;">Опираемся на отзывы Заказчиков</li>
            <li style="margin: 1em;">Общаемся</li>
            </ul>
            """
    },

    "eng_warning": {
        "E": "Only registered Clients can review Engineers. Register or Login",
        "U": "Тільки зареєстровані Замовники можуть переглядати Інженерів. Зареєструйтесь або Ввійдіть",
        "R": "Только зарегистрированные Заказчики могут просматривать Инженеров. Зарегистрируйтесь или Войдите"
    },

    "subscribe": {
        "E": "Subscribe",
        "U": "Підписатися на новини",
        "R": "Подписаться на новости"
    },

    "contact_us": {
        "E": "Contact Us",
        "U": "Зв'язатись з нами",
        "R": "Связаться с нами"
    },




}

