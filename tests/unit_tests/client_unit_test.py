import pytest
from unittest.mock import patch, MagicMock
from app import app, db
from models.collaborators import Collaborator
from models.clients import Client
from models.roles import RoleEnum
from tests.main_fixture import test_client, seed_roles
from enums.relationships_enum import RelationshipEnum
from helpers.validator_helper import ValidatorHelper


@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SALES.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_add_client_success(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "123456789",
            "company_name": "Doe Enterprises"
        }
        response = test_client.post("/client", json=data)
        assert response.status_code == 200
        assert response.json["message"] == "Client added successfully!"

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SALES.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_get_clients_success(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        mock_client = MagicMock(spec=Client)
        mock_client.minimal_to_dict.return_value = {"id": 1, "first_name": "John", "last_name": "Doe"}
        
        with patch("models.clients.Client.query") as mock_query:
            mock_query.all.return_value = [mock_client]
        
            response = test_client.get("/clients")
            assert response.status_code == 200
            assert isinstance(response.json, list)
            assert response.json[0]["id"] == 1


@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SALES.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_get_client_success(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        mock_client = MagicMock(spec=Client, to_dict=lambda: {"id": 1, "first_name": "John", "last_name": "Doe"})
        
        with patch("app.db.session.get", return_value=mock_client):
            response = test_client.get("/client/1")
            assert response.status_code == 200
            assert response.json["id"] == 1

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SALES.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_get_client_not_found(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        with patch("app.db.session.get", return_value=None):
            response = test_client.get("/client/99")
            assert response.status_code == 404
            assert response.json["message"] == "Client not found"

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SALES.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_update_client_patch_success(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        mock_client = MagicMock(spec=Client, to_dict=lambda: {"id": 1, "first_name": "John", "last_name": "Doe"})
        
        with patch("app.db.session.get", return_value=mock_client), \
            patch("app.db.session.commit", return_value=None):
            response = test_client.patch("/client/1", json={"first_name": "Jane"})
            assert response.status_code == 200
            assert response.json["message"] == "Client updated successfully!"

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SALES.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_update_client_patch_not_found(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        with patch("app.db.session.get", return_value=None):
            response = test_client.patch("/client/99", json={"first_name": "Jane"})
            assert response.status_code == 404
            assert response.json["message"] == "Client not found"

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SALES.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
@patch.object(ValidatorHelper, 'entity_exists_check', return_value=None)
def test_update_client_put_success(mock_auth, mock_relationship_check, mock_fk_validator, test_client, seed_roles):
    with app.app_context():
        mock_client = MagicMock(spec=Client, to_dict=lambda: {"id": 1, "first_name": "John", "last_name": "Doe"})
        
        with patch("app.db.session.get", return_value=mock_client), \
            patch("app.db.session.commit", return_value=None):
            data = {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "janedoe@example.com",
                "phone": "0612345678",
                "company_name": "Doe Enterprises",
                "commercial_id": 1
            }
            response = test_client.put("/client/1", json=data)
            assert response.status_code == 200
            assert response.json["message"] == "Client updated successfully!"


@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SALES.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
@patch.object(ValidatorHelper, 'entity_exists_check', return_value=None)
def test_update_client_put_not_found(mock_auth, mock_relationship_check, mock_fk_validator, test_client, seed_roles):
    with app.app_context():
        with patch("app.db.session.get", return_value=None):
            data = {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "janedoe@example.com",
                "phone": "0612345678",
                "company_name": "Doe Enterprises",
                "commercial_id": 1
            }
            response = test_client.put("/client/99", json=data)
            assert response.status_code == 404
            assert response.json["message"] == "Client not found"



@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SALES.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_delete_client_success(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        mock_client = MagicMock(spec=Client, to_dict=lambda: {"id": 1, "first_name": "John", "last_name": "Doe"})
        
        with patch("app.db.session.get", return_value=mock_client), \
            patch("app.db.session.delete", return_value=None), \
            patch("app.db.session.commit", return_value=None):
            response = test_client.delete("/client/1")
            assert response.status_code == 200
            assert response.json["message"] == "Client deleted successfully!"

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SALES.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_delete_client_not_found(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        with patch("app.db.session.get", return_value=None):
            response = test_client.delete("/client/99")
            assert response.status_code == 404
            assert response.json["message"] == "Client not found"
