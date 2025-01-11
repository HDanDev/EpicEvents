from app import db
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()

class Collaborator(db.Model):
    __tablename__ = 'collaborators'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False) 
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)    
    contracts = db.relationship('Contract', backref='commercial', lazy=True)
    events = db.relationship('Event', backref='support', lazy=True)

    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


    def __repr__(self):
        return f"<Collaborator {self.full_name} (Role ID: {self.role_id})>"    
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "role_id": self.role_id,
        }