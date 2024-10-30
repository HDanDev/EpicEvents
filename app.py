import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


load_dotenv()

app = Flask(__name__)

username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
db_host = os.getenv('DB_HOST')
db_admin = os.getenv('DB_ADMIN')
db_admin_password = os.getenv('DB_ADMIN_PASSWORD')

app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{username}:{password}@{db_host}/{db_name}'
# app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{db_admin}:{db_admin_password}@{db_host}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from controllers import main, collaborator
from controllers.auth import auth_bp

app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == '__main__':
    app.run(debug=True)
