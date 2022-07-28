from threading import Thread
from flask import render_template, current_app
from flask_babel import _
from flask_mail import Message
from app import mail
from app.models import User


def send_async_email(app, msg:Message):
    '''Асинхронная отправка письма'''
    with app.app_context():
        mail.send(msg)


def send_email(
    subject:str,
    sender:str,
    recipients:list,
    text_body:str,
    html_body:str,
    ):
    '''Простая отправка письма'''
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app,msg)).start()


def send_password_reset_email(user:User):
    token = user.get_reset_password_token()
    send_email(_('[Microblog] Reset Your Password'),
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))
