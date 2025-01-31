from flask import Blueprint, request, jsonify
from app import db
from models.collaborators import Collaborator
from helpers.authorize_helper import encode_auth_token, decode_auth_token

auth_bp = Blueprint('auth', __name__)

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


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Logs out a user by blacklisting the token."""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return jsonify({"message": "Token is missing"}), 403

    try:
        token = auth_header.split(" ")[1]
        decoded_token = decode_auth_token(token)

        if isinstance(decoded_token, str):
            return jsonify({"message": decoded_token}), 401

        return jsonify({"message": "Successfully logged out"}), 200

    except Exception as e:
        return jsonify({"message": "Error logging out", "error": str(e)}), 500
