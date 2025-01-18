from app import app, db
from flask import jsonify, request
from models.contracts import Contract
from models.roles import RoleEnum
from helpers.authorize_helper import authentication_required, role_restricted, self_user_restricted


@app.route('/contract', methods=['POST'])
@role_restricted(RoleEnum.MANAGEMENT)
def add_contract():
    data = request.get_json()
    new_contract = Contract(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        role_id=data['role_id'])
    new_contract.set_password(data['password'])
    
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
    contracts = Contract.query.all()
    return jsonify([contract.to_dict() for contract in contracts])

@app.route('/contract/<int:id>', methods=['GET'])
@authentication_required
def get_contract(id, current_contract=None):
    contract = Contract.query.get(id)
    if contract:
        return jsonify(contract.to_dict())
    else:
        return jsonify({"message": "Contract not found"}), 404

@app.route('/contract/<int:id>', methods=['PATCH'])
@role_restricted(RoleEnum.MANAGEMENT, True)
def update_contract_patch(id):
    contract = Contract.query.get(id)
    if not contract:
        return jsonify({"message": "Contract not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid or missing data"}), 400

    if 'first_name' in data:
        contract.first_name = data['first_name']
    if 'last_name' in data:
        contract.last_name = data['last_name']
    if 'email' in data:
        existing_contract = Contract.query.filter_by(email=data['email']).first()
        if existing_contract and existing_contract.id != id:
            return jsonify({"message": "Email already in use"}), 400
        contract.email = data['email']
    if 'role_id' in data:
        contract.role_id = data['role_id']

    try:
        db.session.commit()
        return jsonify({"message": "Contract updated successfully!", "contract": contract.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating contract", "error": str(e)}), 500

@app.route('/contract/<int:id>', methods=['PUT'])
@role_restricted(RoleEnum.MANAGEMENT, True)
def update_contract_put(id):
    required_fields = ['first_name', 'last_name', 'email', 'role_id']

    data = request.get_json()

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"message": f"Missing fields: {', '.join(missing_fields)}"}), 400

    contract = Contract.query.get(id)
    if not contract:
        return jsonify({"message": "Contract not found"}), 404
    
    existing_contract = Contract.query.filter_by(email=data['email']).first()
    if existing_contract and existing_contract.id != id:
        return jsonify({"message": "Email already in use"}), 400

    contract.first_name = data['first_name']
    contract.last_name = data['last_name']
    contract.email = data['email']
    contract.role_id = data['role_id']

    try:
        db.session.commit()
        return jsonify({"message": "Contract updated successfully!", "contract": contract.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating contract", "error": str(e)}), 500

@app.route('/contract/<int:id>', methods=['DELETE'])
@role_restricted(RoleEnum.MANAGEMENT, True)
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
