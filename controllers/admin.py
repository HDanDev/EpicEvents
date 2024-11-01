import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import db, app
from models.admin import Admin

def create_admin(email, password):
    with app.app_context():
        if Admin.query.filter_by(email=email).first():
            print("An admin with this email already exists.")
            return
        
        admin = Admin(email=email)
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print("Admin created successfully.")

email = input("Enter admin email: ")
password = input("Enter admin password: ")
create_admin(email, password)
