import string
import random
from app import app, db
from passlib.apps import custom_app_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)


class Urls(db.Model):
    url_id_ = db.Column("id_", db.Integer, primary_key=True, autoincrement=True)
    long = db.Column("long", db.String(), nullable=False)
    short = db.Column("short", db.String(7), nullable=False, unique=True)
    visited_count = db.Column(db.Integer, nullable=False, default=0)
    add_time = db.Column("add_time", db.String(), nullable=False)
    add_date = db.Column("add_date", db.String(), nullable=False)
    shortened_url = db.ColumnProperty('http://127.0.0.1:5000/' + short)

    @staticmethod
    def shorten_url():
        letters = string.ascii_lowercase + string.ascii_uppercase + string.digits

        while True:
            rand_letters = random.choices(letters, k=7)
            rand_letters = "".join(rand_letters)
            short_url = Urls.query.filter_by(short=rand_letters).first()
            if not short_url:
                return rand_letters

    def increment_visited_count(self):
        self.visited_count += 1
        db.session.commit()


class Roles(db.Model):
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    label = db.Column(db.String(255), nullable=False)
    role = db.relationship('Users', backref='role', lazy='dynamic')


class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), default=1)

    def hash_password(self, password):
        self.password_hash = custom_app_context.encrypt(password)

    def verify_password(self, password):
        return custom_app_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=1600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)

        return s.dumps({'id': self.user_id})

    def subscribe_to_premium(self):
        self.role_id = 2
        db.session.commit()

    def is_subscribed(self):
        if self.role_id == 2:
            return True

        return False

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None

        user = Users.query.get(data['id'])

        return user
