from app import db
from datetime import datetime, timezone


class Client(db.Model):
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False) 
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    first_contact_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_contact_date = db.Column(db.DateTime)
    
    contracts = db.relationship('Contract', backref='client', lazy=True)
    
    commercial_id = db.Column(db.Integer, db.ForeignKey('collaborators.id'))
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f"<Client {self.full_name} from {self.company_name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "phone": self.phone,
            "company_name": self.company_name,
            "first_contact_date": self.first_contact_date.isoformat() if self.first_contact_date else None,
            "last_contact_date": self.last_contact_date.isoformat() if self.last_contact_date else None,
            "contracts": [contract.to_dict() for contract in self.contracts] if self.events else [],
            "commercial_id": self.commercial_id,
        }
