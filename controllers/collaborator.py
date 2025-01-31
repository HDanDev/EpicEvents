from app import app, db
from flask import jsonify, request
from models.collaborators import Collaborator
from models.roles import RoleEnum
from helpers.authorize_helper import authentication_required, role_restricted, self_user_restricted
from helpers.validator_helper import ValidatorHelper
from enums.model_type_enum import ModelTypeEnum


@app.route('/collaborator', methods=['POST'])
@role_restricted([RoleEnum.MANAGEMENT])
def add_collaborator(current_collaborator=None):
    data = request.get_json()
    data_validator = ValidatorHelper(ModelTypeEnum.COLLABORATOR, data)
    data_validator.validate_data()
    
    if not data_validator.is_valid():
        return jsonify({"message": "Validation errors", "errors": data_validator.error_messages}), 400

    new_collaborator = Collaborator(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        role_id=data['role_id'])
    new_collaborator.set_password(data['password'])
    
    db.session.add(new_collaborator)
    try:
        db.session.commit()
        return jsonify(
            {
                "message": "Collaborator added successfully!",
                "collaborator": new_collaborator.to_dict()
                }
            ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error adding collaborator", "error": str(e)}), 500


@app.route('/collaborators', methods=['GET'])
@authentication_required
def get_collaborators(current_collaborator=None):
    collaborators = Collaborator.query.all()
    return jsonify([collaborator.minimal_to_dict() for collaborator in collaborators])

@app.route('/collaborator/<int:id>', methods=['GET'])
@authentication_required
def get_collaborator(id, current_collaborator=None):
    collaborator = db.session.get(Collaborator, id)
    if collaborator:
        return jsonify(collaborator.to_dict())
    else:
        return jsonify({"message": "Collaborator not found"}), 404

@app.route('/collaborator/<int:id>', methods=['PATCH'])
@role_restricted([RoleEnum.MANAGEMENT], True)
def update_collaborator_patch(id, current_collaborator=None):
    collaborator = db.session.get(Collaborator, id)
    if not collaborator:
        return jsonify({"message": "Collaborator not found"}), 404

    data = request.get_json()
    data_validator = ValidatorHelper(ModelTypeEnum.COLLABORATOR, data)
    data_validator.validate_data()
    
    if not data_validator.is_valid():
        return jsonify({"message": "Validation errors", "errors": data_validator.error_messages}), 400
    
    if not data:
        return jsonify({"message": "Invalid or missing data"}), 400

    if 'first_name' in data:
        collaborator.first_name = data['first_name']
    if 'last_name' in data:
        collaborator.last_name = data['last_name']
    if 'email' in data:
        existing_collaborator = Collaborator.query.filter_by(email=data['email']).first()
        if existing_collaborator and existing_collaborator.id != id:
            return jsonify({"message": "Email already in use"}), 400
        collaborator.email = data['email']
    if 'role_id' in data:
        collaborator.role_id = data['role_id']

    try:
        db.session.commit()
        return jsonify({"message": "Collaborator updated successfully!", "collaborator": collaborator.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating collaborator", "error": str(e)}), 500
    
@app.route('/collaborator/update-password/<int:id>', methods=['PATCH'])
@self_user_restricted
def update_password(id, current_collaborator=None):
    collaborator = db.session.get(Collaborator, id)
    if not collaborator:
        return jsonify({"message": "Collaborator not found"}), 404

    data = request.get_json()
    data_validator = ValidatorHelper(ModelTypeEnum.COLLABORATOR, data)
    data_validator.validate_data()
    
    if not data_validator.is_valid():
        return jsonify({"message": "Validation errors", "errors": data_validator.error_messages}), 400
    
    if not data:
        return jsonify({"message": "Invalid or missing data"}), 400

    if 'password' in data:
        collaborator.set_password(data['password'])

    try:
        db.session.commit()
        return jsonify({"message": "Password updated successfully!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating Password", "error": str(e)}), 500

@app.route('/collaborator/<int:id>', methods=['PUT'])
@role_restricted([RoleEnum.MANAGEMENT], True)
def update_collaborator_put(id, current_collaborator=None):
    required_fields = ['first_name', 'last_name', 'email', 'role_id']

    data = request.get_json()
    data_validator = ValidatorHelper(ModelTypeEnum.COLLABORATOR, data)
    data_validator.validate_data()
    
    if not data_validator.is_valid():
        return jsonify({"message": "Validation errors", "errors": data_validator.error_messages}), 400

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"message": f"Missing fields: {', '.join(missing_fields)}"}), 400

    collaborator = db.session.get(Collaborator, id)
    if not collaborator:
        return jsonify({"message": "Collaborator not found"}), 404
    
    existing_collaborator = Collaborator.query.filter_by(email=data['email']).first()
    if existing_collaborator and existing_collaborator.id != id:
        return jsonify({"message": "Email already in use"}), 400

    collaborator.first_name = data['first_name']
    collaborator.last_name = data['last_name']
    collaborator.email = data['email']
    collaborator.role_id = data['role_id']

    try:
        db.session.commit()
        return jsonify({"message": "Collaborator updated successfully!", "collaborator": collaborator.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating collaborator", "error": str(e)}), 500

@app.route('/collaborator/<int:id>', methods=['DELETE'])
@role_restricted([RoleEnum.MANAGEMENT], True)
def delete_collaborator(id, current_collaborator=None):
    collaborator = db.session.get(Collaborator, id)
    if collaborator:
        db.session.delete(collaborator)
        try:
            db.session.commit()
            return jsonify({"message": "Collaborator deleted successfully!", "collaborator": collaborator.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error deleting collaborator", "error": str(e)}), 500
    else:
        return jsonify({"message": "Collaborator not found"}), 404
