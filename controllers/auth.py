from flask import Blueprint, request, jsonify
from app import db
from models.collaborators import Collaborator
from utils import encode_auth_token

auth_bp = Blueprint('auth', __name__)
admin_auth_bp = Blueprint('admin_auth', __name__)

# @auth_bp.route('/register', methods=['POST'])
# def register():
#     data = request.get_json()
#     email = data.get('email')
#     password = data.get('password')
#     role = data.get('role')  # Optional role assignment at registration

#     if Collaborator.query.filter_by(email=email).first():
#         return jsonify({'message': 'Collaborator already exists'}), 400

#     collaborator = Collaborator(email=email, role=role)
#     collaborator.set_password(password)
#     db.session.add(collaborator)
#     db.session.commit()

#     return jsonify({'message': 'Collaborator registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    collaborator = Collaborator.query.filter_by(email=email).first()

    if collaborator and collaborator.check_password(password):
        auth_token = encode_auth_token(collaborator.id)
        if auth_token:
            return jsonify({'token': auth_token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401
