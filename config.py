import os

username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
db_host = os.getenv('DB_HOST')
db_admin = os.getenv('DB_ADMIN')
db_admin_password = os.getenv('DB_ADMIN_PASSWORD')

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f'mysql+mysqlconnector://{username}:{password}@{db_host}/{db_name}'

class TestConfig(Config):
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True
