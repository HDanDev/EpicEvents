import pytest
from unittest.mock import patch, MagicMock
from app import app, db
from models.collaborators import Collaborator
from models.contracts import Contract
from models.clients import Client
from models.roles import RoleEnum
from tests.main_fixture import test_client, seed_roles
from helpers.validator_helper import ValidatorHelper

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_add_contract_success(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        contract_data = {
            "costing": 1000.0,
            "remaining_due_payment": 500.0,
            "signed": True,
            "client_id": 1,
            "commercial_id": 2
        }

        mock_client = MagicMock(id=1)
        mock_collaborator = MagicMock(id=2, role_id=RoleEnum.SALES.value)

        with patch("app.db.session.get") as mock_get, \
             patch("app.db.session.add") as mock_add, \
             patch("app.db.session.commit") as mock_commit:
            
            def mock_db_get(model, id):
                if model == Client and id == 1:
                    return mock_client
                elif model == Collaborator and id == 2:
                    return mock_collaborator
                return None

            mock_get.side_effect = mock_db_get
            mock_commit.return_value = None

            response = test_client.post("/contract", json=contract_data)

            assert response.status_code == 200
            assert response.json["message"] == "Contract added successfully!"
            assert "contract" in response.json


@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_add_contract_validation_error(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        contract_data = {
            "costing": 1000.0,
            "signed": True,
            "client_id": 1
        }

        response = test_client.post("/contract", json=contract_data)
        
        assert response.status_code == 400
        assert response.json["message"] == "Validation errors"
        assert "errors" in response.json

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SALES.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_get_contracts_success(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        mock_contract = MagicMock(spec=Contract, to_dict=lambda: {"id": 1, "costing": 1000.0, "client_id": 1})
        
        with patch("models.contracts.Contract.query") as mock_query:
            mock_query.all.return_value = [mock_contract]
            response = test_client.get("/contracts")
            assert response.status_code == 200
            assert isinstance(response.json, list)
            assert response.json[0]["id"] == 1

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SALES.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_get_contracts_no_results(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        with patch("models.contracts.Contract.query.all", return_value=[]):
            response = test_client.get("/contracts")
            assert response.status_code == 200
            assert response.json == []

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_get_contract_success(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        mock_contract = MagicMock(spec=Contract, to_dict=lambda: {"id": 1, "costing": 1000.0, "client_id": 1})
        
        with patch("app.db.session.get", return_value=mock_contract):
            response = test_client.get("/contract/1")
            assert response.status_code == 200
            assert response.json["id"] == 1

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_get_contract_not_found(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        with patch("app.db.session.get", return_value=None):
            response = test_client.get("/contract/99")
            assert response.status_code == 404
            assert response.json["message"] == "Contract not found"

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_update_contract_patch_success(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        mock_contract = MagicMock(
            spec=Contract,
            to_dict=lambda: {
                "id": 1,
                "costing": 1000.0,
                "client_id": 1,
                "signed": False
            }
        )

        with patch("app.db.session.get", return_value=mock_contract), \
             patch("app.db.session.commit", return_value=None):
            
            response = test_client.patch("/contract/1", json={"costing": 1500.0})

            assert response.status_code == 200
            assert response.json["message"] == "Contract updated successfully!"

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_update_contract_patch_not_found(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        with patch("app.db.session.get", return_value=None):
            response = test_client.patch("/contract/99", json={"costing": 1500.0})
            assert response.status_code == 404
            assert response.json["message"] == "Contract not found"

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
@patch.object(ValidatorHelper, 'entity_exists_check', return_value=None)
def test_update_contract_put_success(mock_auth, mock_relationship_check, mock_fk_validator, test_client):
    with app.app_context():
        mock_contract = MagicMock(spec=Contract, to_dict=lambda: {"id": 1, "costing": 1000.0, "client_id": 1})
        
        with patch("app.db.session.get", return_value=mock_contract), \
             patch("app.db.session.commit", return_value=None):
            contract_data = {
                "costing": 1500.0,
                "remaining_due_payment": 300.0,
                "creation_date": "2025-02-01",
                "signed": True,
                "client_id": 1,
                "commercial_id": 2
            }
            response = test_client.put("/contract/1", json=contract_data)
            assert response.status_code == 200
            assert response.json["message"] == "Contract updated successfully!"

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
@patch.object(ValidatorHelper, 'entity_exists_check', return_value=None)
def test_update_contract_put_missing_fields(mock_auth, mock_relationship_check, mock_fk_validator, test_client):
    with app.app_context():
        contract_data = {
            "costing": 1500.0,
            "remaining_due_payment": 300.0,
            "signed": True,
            "client_id": 1
        }
        response = test_client.put("/contract/1", json=contract_data)
        assert response.status_code == 400
        assert "Missing fields" in response.json["message"]

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_delete_contract_success(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        mock_contract = MagicMock(spec=Contract, to_dict=lambda: {"id": 1, "costing": 1000.0, "client_id": 1})
        
        with patch("app.db.session.get", return_value=mock_contract), \
             patch("app.db.session.delete", return_value=None), \
             patch("app.db.session.commit", return_value=None):
            response = test_client.delete("/contract/1")
            assert response.status_code == 200
            assert response.json["message"] == "Contract deleted successfully!"

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_delete_contract_not_found(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        with patch("app.db.session.get", return_value=None):
            response = test_client.delete("/contract/99")
            assert response.status_code == 404
            assert response.json["message"] == "Contract not found"
