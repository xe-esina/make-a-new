from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_heroku import Heroku

app = Flask(__name__)
app.config.from_object(Config)
heroku = Heroku(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Войдите, чтобы открыть эту страницу."

bootstrap = Bootstrap(app)

from app import routes, forms, models