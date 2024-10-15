from app import app, db
from flask import jsonify, request
from models.collaborators import Collaborator


@app.route('/collaborator', methods=['POST'])
def add_collaborator():
    data = request.get_json()
    new_collaborator = Collaborator(first_name=data['first_name'], last_name=data['last_name'], email=data['email'])
    
    db.session.add(new_collaborator)
    db.session.commit()

    return jsonify({"message": "Collaborator added successfully!"}), 201

@app.route('/collaborators', methods=['GET'])
def get_collaborators():
    collaborators = Collaborator.query.all()
    return jsonify([collaborator.to_dict() for collaborator in collaborators])

@app.route('/collaborator/<int:id>', methods=['GET'])
def get_collaborator(id):
    collaborator = Collaborator.query.get(id)
    if collaborator:
        return jsonify(collaborator.to_dict())
    else:
        return jsonify({"message": "Collaborator not found"}), 404

@app.route('/collaborator/<int:id>', methods=['DELETE'])
def delete_collaborator(id):
    collaborator = Collaborator.query.get(id)
    if collaborator:
        db.session.delete(collaborator)
        db.session.commit()
        return jsonify({"message": "Collaborator deleted successfully!"})
    else:
        return jsonify({"message": "Collaborator not found"}), 404
