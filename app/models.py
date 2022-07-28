import jwt
from datetime import datetime
from time import time
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask_login import UserMixin
from hashlib import md5
from app import db, login


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


'''
Вспомогательная таблица followers для хранения связей между пользователями
'''
followers = db.Table('followers',
                     db.Column('follower_id', db.Integer,
                               db.ForeignKey('user.id')),
                     db.Column('followed_id', db.Integer,
                               db.ForeignKey('user.id'))
                     )


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic'
    )

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        '''Сгенерировать и установить хэш пароля пользователя'''
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        '''Проверить соответствие хеша паролю'''
        return check_password_hash(self.password_hash, password)

    def avatar(self, size: int = 32):
        '''Генерация ссылки на Gravatar пользователя
        :param int size: размер аватара в пикселях'''
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user):
        '''Подписаться на пользователя user'''
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        '''Отписаться от пользователя user'''
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        '''Проверить находится ли пользователь user в подписках'''
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        '''Найти все посты из подписок пользователя и его собственные'''
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

    def get_reset_password_token(self, expires_in: int = 600):
        '''
        Сгенерировать JWT для восстановления пароля пользователя.
        Стандартный срок действия токена — 10 минут
        :param int expires_in: срок действия JWT в секундах
        '''
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token: str):
        '''
        Метод принимает строку с JWT в качестве параметра
        и возвращает пользователя из базы, либо None если такого
        пользователя не существует.
        :param str token: строка JWT
        :rtype: объект User или None
        '''
        try:
            id = jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    language = db.Column(db.String(5))

    def __repr__(self):
        return f'<Post {self.body}>'
