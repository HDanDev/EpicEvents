from app import db


class Event(db.Model):
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(255), nullable=False)
    attendees = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text)
    
    contract_id = db.Column(db.Integer, db.ForeignKey('contracts.id'), nullable=False)
    support_id = db.Column(db.Integer, db.ForeignKey('collaborators.id'))
    
    def __repr__(self):
        return f"<Event {self.name} for {self.contract.client.full_name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "location": self.location,
            "attendees": self.attendees,
            "notes": self.notes,
            "contract_id": self.contract_id,
            "support_id": self.support_id,
        }
        
    def minimal_to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "contract_id": self.contract_id,
            "support_id": self.support_id
        }
