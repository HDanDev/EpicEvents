from app import app, db
from flask import jsonify, request
from models.contracts import Contract
from models.roles import RoleEnum
from enums.relationships_enum import RelationshipEnum
from helpers.authorize_helper import authentication_required, role_restricted, self_user_restricted
from helpers.validator_helper import ValidatorHelper
from enums.model_type_enum import ModelTypeEnum


@app.route('/contract', methods=['POST'])
@role_restricted([RoleEnum.MANAGEMENT])
def add_contract(current_collaborator=None):
    data = request.get_json()
    data_validator = ValidatorHelper(ModelTypeEnum.CONTRACT, data)
    data_validator.validate_data()
    
    if not data_validator.is_valid():
        return jsonify({"message": "Validation errors", "errors": data_validator.error_messages}), 400
    
    new_contract = Contract(
        costing=data['costing'],
        remaining_due_payment=data['remaining_due_payment'],
        signed=data['signed'],
        client_id=data['client_id'],
        commercial_id=data['commercial_id'])
    
    db.session.add(new_contract)
    try:
        db.session.commit()
        return jsonify(
            {
                "message": "Contract added successfully!",
                "contract": new_contract.to_dict()
                }
            ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error adding contract", "error": str(e)}), 500


@app.route('/contracts', methods=['GET'])
@authentication_required
def get_contracts(current_collaborator=None):
    if RoleEnum(current_collaborator.role_id) == RoleEnum.SALES:
        data_costing = request.args.get('costing')
        data_remaining_due_payment = request.args.get('remaining_due_payment')
        data_creation_date = request.args.get('creation_date')
        data_signed = request.args.get('signed')
        data_client_id = request.args.get('client_id')
        data_commercial = request.args.get('commercial_id')
        data_events = request.args.get('events')
        
        query = Contract.query.all()
        
        if data_costing is not None:    
            query = Contract.query.filter_by(costing=data_costing)
        if data_remaining_due_payment is not None:    
            query = Contract.query.filter_by(remaining_due_payment=data_remaining_due_payment)
        if data_creation_date is not None:    
            query = Contract.query.filter_by(creation_date=data_creation_date)
        if data_signed is not None:
            query = query.filter(Contract.signed == (data_signed.lower() == 'true'))
        if data_client_id is not None:    
            query = Contract.query.filter_by(client_id=data_client_id)
        if data_commercial is not None:    
            query = Contract.query.filter_by(commercial_id=data_commercial)
        if data_events is not None:    
            query = Contract.query.filter_by(events=data_events)
        
        return jsonify([contract.to_dict() for contract in query])
    
    contracts = Contract.query.all()
    return jsonify([contract.minimal_to_dict() for contract in contracts])

@app.route('/contract/<int:id>', methods=['GET'])
@role_restricted([RoleEnum.MANAGEMENT, RoleEnum.SALES], relationType=RelationshipEnum.COLLABORATOR_CLIENT)
def get_contract(id, current_contract=None):
    contract = Contract.query.get(id)
    if contract:
        return jsonify(contract.to_dict())
    else:
        return jsonify({"message": "Contract not found"}), 404

@app.route('/contract/<int:id>', methods=['PATCH'])
@role_restricted([RoleEnum.MANAGEMENT, RoleEnum.SALES], relationType=RelationshipEnum.COLLABORATOR_CLIENT)
def update_contract_patch(id, current_collaborator=None):
    contract = Contract.query.get(id)
    if not contract:
        return jsonify({"message": "Contract not found"}), 404

    data = request.get_json()
    data_validator = ValidatorHelper(ModelTypeEnum.CONTRACT, data)
    data_validator.validate_data()
    
    if not data_validator.is_valid():
        return jsonify({"message": "Validation errors", "errors": data_validator.error_messages}), 400
    
    if not data:
        return jsonify({"message": "Invalid or missing data"}), 400

    if 'costing' in data:
        contract.costing = data['costing']
    if 'remaining_due_payment' in data:
        contract.remaining_due_payment = data['remaining_due_payment']
    if 'creation_date' in data:
        contract.creation_date = data['creation_date']
    if 'signed' in data:
        contract.signed = data['signed']
    if 'client_id' in data:
        contract.client_id = data['client_id']
    if 'commercial_id' in data:
        contract.commercial_id = data['commercial_id']

    try:
        db.session.commit()
        return jsonify({"message": "Contract updated successfully!", "contract": contract.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating contract", "error": str(e)}), 500

@app.route('/contract/<int:id>', methods=['PUT'])
@role_restricted([RoleEnum.MANAGEMENT, RoleEnum.SALES], relationType=RelationshipEnum.COLLABORATOR_CLIENT)
def update_contract_put(id):
    required_fields = [
        'costing',
        'remaining_due_payment',
        'creation_date',
        'signed',
        'client_id',
        'commercial_id'
        ]

    data = request.get_json()
    data_validator = ValidatorHelper(ModelTypeEnum.CONTRACT, data)
    data_validator.validate_data()
    
    if not data_validator.is_valid():
        return jsonify({"message": "Validation errors", "errors": data_validator.error_messages}), 400

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"message": f"Missing fields: {', '.join(missing_fields)}"}), 400

    contract = Contract.query.get(id)
    if not contract:
        return jsonify({"message": "Contract not found"}), 404
    
    existing_contract = Contract.query.filter_by(
        client_id=data['client_id'],
        commercial_id=data['commercial_id']
        ).first()
    if existing_contract and existing_contract.id != contract.id:
        return jsonify({"message": "Such contract already exist"}), 400

    contract.costing = data['costing']
    contract.remaining_due_payment = data['remaining_due_payment']
    contract.creation_date = data['creation_date']
    contract.signed = data['signed']
    contract.client_id = data['client_id']
    contract.commercial_id = data['commercial_id']

    try:
        db.session.commit()
        return jsonify({"message": "Contract updated successfully!", "contract": contract.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating contract", "error": str(e)}), 500

@app.route('/contract/<int:id>', methods=['DELETE'])
@role_restricted([RoleEnum.MANAGEMENT, RoleEnum.SALES], relationType=RelationshipEnum.COLLABORATOR_CLIENT)
def delete_contract(id):
    contract = Contract.query.get(id)
    if contract:
        db.session.delete(contract)
        try:
            db.session.commit()
            return jsonify({"message": "Contract deleted successfully!", "contract": contract.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error deleting contract", "error": str(e)}), 500
    else:
        return jsonify({"message": "Contract not found"}), 404
