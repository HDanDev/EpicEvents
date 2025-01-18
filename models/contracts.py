from app import db
from datetime import datetime, timezone


class Contract(db.Model):
    __tablename__ = 'contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    costing = db.Column(db.Float, nullable=False)
    remaining_due_payment = db.Column(db.Float, nullable=False)
    creation_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    signed = db.Column(db.Boolean, default=False)
    
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'), nullable=False)
    commercial_id = db.Column(db.Integer, db.ForeignKey('collaborators.id'), nullable=False)

    events = db.relationship('Event', backref='contract', lazy=True)
    
    def __repr__(self):
        return f"<Contract {self.id} for Client {self.client.full_name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "costing": self.costing,
            "remaining_due_payment": self.remaining_due_payment,
            "creation_date": self.creation_date.isoformat() if self.creation_date else None,
            "signed": self.signed,
            "client_id": self.client_id,
            "commercial_id": self.commercial_id,
            "events": [event.to_dict() for event in self.events] if self.events else [],
        }
