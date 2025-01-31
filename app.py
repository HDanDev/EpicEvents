import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import TestConfig, Config

load_dotenv()

app = Flask(__name__)
env = os.getenv('FLASK_ENV', 'development')

if env == 'testing':
    app.config.from_object(TestConfig)
else:
    app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from controllers import main, client, collaborator, contract, event 
from controllers.auth import auth_bp

app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == '__main__':
    app.run(debug=True)
