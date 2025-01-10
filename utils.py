import jwt
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify
from models.collaborators import Collaborator


load_dotenv()

SECRET_KEY = os.getenv('HASH_SECRET_KEY')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Token is missing'}), 403

        try:
            token = auth_header.split(" ")[1]
            collaborator_id = decode_auth_token(token)
            current_collaborator = Collaborator.query.get(collaborator_id)
        except:
            return jsonify({'message': 'Token is invalid or expired'}), 403

        return f(current_collaborator, *args, **kwargs)
    return decorated

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
