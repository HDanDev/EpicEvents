from app import app, db
from flask import jsonify, request
from models.events import Event
from models.roles import RoleEnum
from helpers.authorize_helper import authentication_required, role_restricted, self_user_restricted


@app.route('/event', methods=['POST'])
@role_restricted(RoleEnum.MANAGEMENT)
def add_event():
    data = request.get_json()
    new_event = Event(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        role_id=data['role_id'])
    new_event.set_password(data['password'])
    
    db.session.add(new_event)
    try:
        db.session.commit()
        return jsonify(
            {
                "message": "Event added successfully!",
                "event": new_event.to_dict()
                }
            ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error adding event", "error": str(e)}), 500


@app.route('/events', methods=['GET'])
@authentication_required
def get_events(current_collaborator=None):
    events = Event.query.all()
    return jsonify([event.to_dict() for event in events])

@app.route('/event/<int:id>', methods=['GET'])
@authentication_required
def get_event(id, current_collaborator=None):
    event = Event.query.get(id)
    if event:
        return jsonify(event.to_dict())
    else:
        return jsonify({"message": "Event not found"}), 404

@app.route('/event/<int:id>', methods=['PATCH'])
@role_restricted(RoleEnum.MANAGEMENT, True)
def update_event_patch(id):
    event = Event.query.get(id)
    if not event:
        return jsonify({"message": "Event not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid or missing data"}), 400

    if 'first_name' in data:
        event.first_name = data['first_name']
    if 'last_name' in data:
        event.last_name = data['last_name']
    if 'email' in data:
        existing_event = Event.query.filter_by(email=data['email']).first()
        if existing_event and existing_event.id != id:
            return jsonify({"message": "Email already in use"}), 400
        event.email = data['email']
    if 'role_id' in data:
        event.role_id = data['role_id']

    try:
        db.session.commit()
        return jsonify({"message": "Event updated successfully!", "event": event.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating event", "error": str(e)}), 500

@app.route('/event/<int:id>', methods=['PUT'])
@role_restricted(RoleEnum.MANAGEMENT, True)
def update_event_put(id):
    required_fields = ['first_name', 'last_name', 'email', 'role_id']

    data = request.get_json()

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"message": f"Missing fields: {', '.join(missing_fields)}"}), 400

    event = Event.query.get(id)
    if not event:
        return jsonify({"message": "Event not found"}), 404
    
    existing_event = Event.query.filter_by(email=data['email']).first()
    if existing_event and existing_event.id != id:
        return jsonify({"message": "Email already in use"}), 400

    event.first_name = data['first_name']
    event.last_name = data['last_name']
    event.email = data['email']
    event.role_id = data['role_id']

    try:
        db.session.commit()
        return jsonify({"message": "Event updated successfully!", "event": event.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating event", "error": str(e)}), 500

@app.route('/event/<int:id>', methods=['DELETE'])
@role_restricted(RoleEnum.MANAGEMENT, True)
def delete_event(id):
    event = Event.query.get(id)
    if event:
        db.session.delete(event)
        try:
            db.session.commit()
            return jsonify({"message": "Event deleted successfully!", "event": event.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error deleting event", "error": str(e)}), 500
    else:
        return jsonify({"message": "Event not found"}), 404
