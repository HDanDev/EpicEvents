from app import app, db
from flask import jsonify, request
from models.events import Event
from models.contracts import Contract
from models.roles import RoleEnum
from enums.relationships_enum import RelationshipEnum
from helpers.authorize_helper import authentication_required, role_restricted, self_user_restricted
from helpers.validator_helper import ValidatorHelper
from enums.model_type_enum import ModelTypeEnum


@app.route('/event', methods=['POST'])
# restrict to related user with signed contract
@role_restricted([RoleEnum.SALES], relationType=RelationshipEnum.COLLABORATOR_CLIENT)
def add_event(current_collaborator=None):
    data = request.get_json()
    data_validator = ValidatorHelper(ModelTypeEnum.EVENT, data)
    data_validator.validate_data()
    
    if not data_validator.is_valid():
        return jsonify({"message": "Validation errors", "errors": data_validator.error_messages}), 400
    
    # client_id = data.get('client_id')
    # contract_id = data.get('contract_id')
    
    # contract = Contract.query.filter_by(id=contract_id, commercial_id=current_collaborator.id, signed=True).first()
    
    # if not contract:
    #     return jsonify({"message": "Invalid or unsigned contract"}), 403
    
    new_event = Event(
        name=data['name'],
        start_date=data['start_date'],
        end_date=data['end_date'],
        location=data['location'],
        attendees=data['attendees'],
        notes=data['notes'],
        contract_id=data['contract_id']
        )
    
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
    if RoleEnum(current_collaborator.role_id) == RoleEnum.MANAGEMENT:
        data_name = request.args.get('name')
        data_start_date = request.args.get('start_date')
        data_end_date = request.args.get('end_date')
        data_location = request.args.get('location')
        data_attendees = request.args.get('attendees')
        data_contract_id = request.args.get('contract_id')
        data_support_id = request.args.get('support_id')
        
        if data_name is not None:    
            query = Contract.query.filter_by(name=data_name)
        if data_start_date is not None:    
            query = Contract.query.filter_by(start_date=data_start_date)
        if data_end_date is not None:    
            query = Contract.query.filter_by(end_date=data_end_date)
        if data_location is not None:    
            query = Contract.query.filter_by(location=data_location)
        if data_attendees is not None:    
            query = Contract.query.filter_by(attendees=data_attendees)
        if data_contract_id is not None:    
            query = Contract.query.filter_by(contract_id=data_contract_id)
        if data_support_id is not None:    
            query = Contract.query.filter_by(support_id=data_support_id)
            
        return jsonify([event.to_dict() for event in query])
            
    events = Event.query.all()
    return jsonify([event.minimal_to_dict() for event in events])

@app.route('/event/<int:id>', methods=['GET'])
@role_restricted([RoleEnum.SUPPORT])
def get_event(id, current_collaborator=None):
    event = Event.query.get(id)
    if event:
        return jsonify(event.to_dict())
    else:
        return jsonify({"message": "Event not found"}), 404

@app.route('/event/<int:id>', methods=['PATCH'])
@role_restricted([RoleEnum.MANAGEMENT, RoleEnum.SUPPORT], True)
def update_event_patch(id, current_collaborator=None):
    event = Event.query.get(id)
    if not event:
        return jsonify({"message": "Event not found"}), 404

    data = request.get_json()
    data_validator = ValidatorHelper(ModelTypeEnum.EVENT, data)
    data_validator.validate_data()
    
    if not data_validator.is_valid():
        return jsonify({"message": "Validation errors", "errors": data_validator.error_messages}), 400
    
    if not data:
        return jsonify({"message": "Invalid or missing data"}), 400
    
    if RoleEnum(current_collaborator.role_id) == RoleEnum.SUPPORT:
        if 'name' in data:
            event.name = data['name']
        if 'start_date' in data:
            event.start_date = data['start_date']
        if 'end_date' in data:
            event.end_date = data['end_date']
        if 'location' in data:
            event.location = data['location']
        if 'attendees' in data:
            event.attendees = data['attendees']
        if 'notes' in data:
            event.notes = data['notes']
        if 'contract_id' in data:
            event.contract_id = data['contract_id']
            
    if 'support_id' in data:
        event.support_id = data['support_id']

    try:
        db.session.commit()
        return jsonify({"message": "Event updated successfully!", "event": event.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating event", "error": str(e)}), 500

@app.route('/event/<int:id>', methods=['PUT'])
@role_restricted([RoleEnum.SUPPORT], True)
def update_event_put(id):
    required_fields = [
        'name',
        'start_date',
        'end_date',
        'location',
        'attendees',
        'notes',
        'contract_id',
        'support_id'
        ]

    data = request.get_json()
    data_validator = ValidatorHelper(ModelTypeEnum.EVENT, data)
    data_validator.validate_data()
    
    if not data_validator.is_valid():
        return jsonify({"message": "Validation errors", "errors": data_validator.error_messages}), 400

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"message": f"Missing fields: {', '.join(missing_fields)}"}), 400

    event = Event.query.get(id)
    if not event:
        return jsonify({"message": "Event not found"}), 404
    
    existing_event = Event.query.filter_by(email=data['email']).first()
    if existing_event and existing_event.id != id:
        return jsonify({"message": "Email already in use"}), 400

    event.name = data['name']
    event.start_date = data['start_date']
    event.end_date = data['end_date']
    event.location = data['location']
    event.attendees = data['attendees']
    event.notes = data['notes']
    event.contract_id = data['contract_id']
    event.support_id = data['support_id']

    try:
        db.session.commit()
        return jsonify({"message": "Event updated successfully!", "event": event.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating event", "error": str(e)}), 500

@app.route('/event/<int:id>', methods=['DELETE'])
@role_restricted([RoleEnum.SALES], True)
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
