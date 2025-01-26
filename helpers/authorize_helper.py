import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
from models.collaborators import Collaborator
from models.clients import Client
from models.contracts import Contract
from models.roles import RoleEnum
from enums.relationships_enum import RelationshipEnum


load_dotenv()

SECRET_KEY = os.getenv('HASH_SECRET_KEY')

def authentication_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        current_collaborator, error_response, status_code = get_authenticated_collaborator()
        if error_response:
            return error_response, status_code

        kwargs['current_collaborator'] = current_collaborator

        return f(*args, **kwargs)
    return decorated

def get_authenticated_collaborator():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, jsonify({'message': 'Token is missing or invalid'}), 403

    try:
        token = auth_header.split(" ")[1]
        collaborator_id = decode_auth_token(token)
        current_collaborator = Collaborator.query.get(collaborator_id)
        if not current_collaborator:
            return None, jsonify({'message': 'User not found'}), 404
        return current_collaborator, None, None
    except Exception as e:
        return None, jsonify({'message': 'Token is invalid or expired'}), 403

def self_user_restricted(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        current_collaborator, error_response, status_code = get_authenticated_collaborator()
        if error_response:
            return error_response, status_code
        
        target_user_id = kwargs.get('id')
        if current_collaborator.id != target_user_id :
            return jsonify({'message': 'Permission denied'}), 403

        kwargs['current_collaborator'] = current_collaborator
        return f(*args, **kwargs)
    return decorated

def role_restricted(roles, is_self_edition_exception=False, relationType=RelationshipEnum.NONE):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_collaborator, error_response, status_code = get_authenticated_collaborator()
            if error_response:
                return error_response, status_code
            
            target_user_id = kwargs.get('id')
            if is_self_edition_exception and current_collaborator.id == target_user_id:
                kwargs['current_collaborator'] = current_collaborator
                return func(*args, **kwargs)
            
            role = RoleEnum(current_collaborator.role_id)
            if (role not in roles):
                return jsonify({'message': 'Permission denied'}), 403

            if relationType:
                result = relationship_check_switch(current_collaborator, relationType, *args, **kwargs)
                if result:
                    return result
            
            kwargs['current_collaborator'] = current_collaborator
            return func(*args, **kwargs)
        return wrapper
    return decorator

# def user_related_restricted(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         current_collaborator, error_response, status_code = get_authenticated_collaborator()
#         if error_response:
#             return error_response, status_code
        
#         target_user_id = kwargs.get('id')
#         if not target_user_id or not is_client_assigned_to_collaborator(target_user_id, current_collaborator):
#             return jsonify({'message': 'Permission denied'}), 403
        
#         kwargs['current_collaborator'] = current_collaborator
#         return func(*args, **kwargs)            
#     return wrapper

def encode_auth_token(user_id):
    try:
        payload = {
            'exp': datetime.now(timezone.utc) + timedelta(days=1),
            'iat': datetime.now(timezone.utc),
            'sub': user_id
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    except Exception as e:
        return e

def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, SECRET_KEY, algorithms=['HS256'])
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'
    
def relationship_check_switch(current_collaborator, relationship_enum=RelationshipEnum.NONE, *args, **kwargs):
    if relationship_enum == RelationshipEnum.NONE:
        return None
    elif RoleEnum(current_collaborator.role_id) == RoleEnum.SALES and relationship_enum == RelationshipEnum.COLLABORATOR_CLIENT:
        return collaborator_client_relationship_check(current_collaborator, *args, **kwargs)

def collaborator_client_relationship_check(current_collaborator, *args, **kwargs):
    data = request.get_json()
    contract = Contract.query.get(data.get('contract_id'))
    if not contract:
        return jsonify({'message': 'The contract_id field is mandatory to create an event'}), 403
    
    if Client.query.filter_by(id=contract.client_id, commercial_id=current_collaborator.id).first() is None:
        return jsonify({'message': 'Permission denied, you only have the right to create events for clients you are assigned to'}), 403
    return None