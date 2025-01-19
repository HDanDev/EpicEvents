from app import app, db
from flask import jsonify, request
from models.clients import Client
from models.roles import RoleEnum
from helpers.authorize_helper import authentication_required, role_restricted, user_related_restricted


@app.route('/client', methods=['POST'])
@role_restricted(RoleEnum.SALES)
def add_client(current_collaborator=None):
    data = request.get_json()
    new_client = Client(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        phone=data['phone'],
        company_name=data['company_name'])
    
    new_client.commercial_id = current_collaborator.id
    
    db.session.add(new_client)
    try:
        db.session.commit()
        return jsonify(
            {
                "message": "Client added successfully!",
                "client": new_client.to_dict()
                }
            ), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error adding client", "error": str(e)}), 500


@app.route('/clients', methods=['GET'])
@authentication_required
def get_clients(current_collaborator=None):
    clients = Client.query.all()
    return jsonify([client.to_dict() for client in clients])

@app.route('/client/<int:id>', methods=['GET'])
@authentication_required
@user_related_restricted
def get_client(id, current_collaborator=None):
    client = Client.query.get(id)
    if client:
        return jsonify(client.to_dict())
    else:
        return jsonify({"message": "Client not found"}), 404

@app.route('/client/<int:id>', methods=['PATCH'])
@role_restricted(RoleEnum.SALES, True)
@user_related_restricted
def update_client_patch(id, current_collaborator=None):
    client = Client.query.get(id)
    if not client:
        return jsonify({"message": "Client not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid or missing data"}), 400

    if 'first_name' in data:
        client.first_name = data['first_name']
    if 'last_name' in data:
        client.last_name = data['last_name']
    if 'email' in data:
        existing_client = Client.query.filter_by(email=data['email']).first()
        if existing_client and existing_client.id != id:
            return jsonify({"message": "Email already in use"}), 400
        client.email = data['email']
    if 'phone' in data:
        client.phone = data['phone']
    if 'company_name' in data:
        client.company_name = data['company_name']
    if 'commercial_id' in data:
        client.commercial_id = data['commercial_id']

    try:
        db.session.commit()
        return jsonify({"message": "Client updated successfully!", "client": client.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating client", "error": str(e)}), 500

@app.route('/client/<int:id>', methods=['PUT'])
@role_restricted(RoleEnum.SALES, True)
@user_related_restricted
def update_client_put(id, current_collaborator=None):
    required_fields = ['first_name', 'last_name', 'email', 'phone', 'company_name', 'commercial_id']

    data = request.get_json()

    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        return jsonify({"message": f"Missing fields: {', '.join(missing_fields)}"}), 400

    client = Client.query.get(id)
    if not client:
        return jsonify({"message": "Client not found"}), 404
    
    existing_client = Client.query.filter_by(email=data['email']).first()
    if existing_client and existing_client.id != id:
        return jsonify({"message": "Email already in use"}), 400

    client.first_name = data['first_name']
    client.last_name = data['last_name']
    client.email = data['email']
    client.phone = data['phone']
    client.company_name = data['company_name']
    client.commercial_id = data['commercial_id']

    try:
        db.session.commit()
        return jsonify({"message": "Client updated successfully!", "client": client.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error updating client", "error": str(e)}), 500

@app.route('/client/<int:id>', methods=['DELETE'])
@role_restricted(RoleEnum.SALES, True)
@user_related_restricted
def delete_client(id, current_collaborator=None):
    client = Client.query.get(id)
    if client:
        db.session.delete(client)
        try:
            db.session.commit()
            return jsonify({"message": "Client deleted successfully!", "client": client.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error deleting client", "error": str(e)}), 500
    else:
        return jsonify({"message": "Client not found"}), 404
