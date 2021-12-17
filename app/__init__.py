from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

app.secret_key = 'xyz123df'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///urls.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from app import routes
from app.api import routes
