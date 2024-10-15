from app import db


class Collaborator(db.Model):
    __tablename__ = 'collaborators'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False) 
    email = db.Column(db.String(120), unique=True, nullable=False)

    role = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)    
    contracts = db.relationship('Contract', backref='commercial', lazy=True)
    events = db.relationship('Event', backref='support', lazy=True)

    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


    def __repr__(self):
        return f"<Collaborator {self.name} ({self.role})>"
