import pytest
from unittest.mock import patch, MagicMock
from app import app, db
from models.collaborators import Collaborator
from models.roles import RoleEnum
from tests.main_fixture import test_client, seed_roles

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
def test_add_collaborator_success(mock_auth, test_client, seed_roles):

    with app.app_context():

        mock_collaborator = MagicMock(spec=Collaborator)
        mock_collaborator.to_dict.return_value = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "role_id": RoleEnum.SALES.value
        }

        with patch("models.collaborators.Collaborator", return_value=mock_collaborator), \
                patch("app.db.session.add"), \
                patch("app.db.session.commit"):

            payload = {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "password": "S3curep@ssword",
                "role_id": RoleEnum.SALES.value
            }

            response = test_client.post("/collaborator", json=payload)

            assert response.status_code == 200, f"Unexpected status code: {response.status_code}. Response: {response.json}"
            assert response.json["message"] == "Collaborator added successfully!"
            assert "collaborator" in response.json

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SALES.value), None, None))
def test_add_collaborator_unauthorized(mock_auth, test_client, seed_roles):

    with app.app_context():

        mock_collaborator = MagicMock(spec=Collaborator)
        mock_collaborator.to_dict.return_value = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "role_id": RoleEnum.SALES.value
        }

        with patch("models.collaborators.Collaborator", return_value=mock_collaborator), \
                patch("app.db.session.add"), \
                patch("app.db.session.commit"):

            payload = {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "password": "S3curep@ssword",
                "role_id": RoleEnum.SALES.value
            }

            response = test_client.post("/collaborator", json=payload)

            assert response.status_code == 403, f"Unexpected status code: {response.status_code}. Response: {response.json}"
            assert response.json["message"] == "Permission denied"


@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
def test_add_collaborator_validation_failure(mock_auth, test_client, seed_roles):

    with app.app_context():

        mock_collaborator = MagicMock(spec=Collaborator)
        mock_collaborator.to_dict.return_value = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "role_id": RoleEnum.SALES.value
        }

        with patch("models.collaborators.Collaborator", return_value=mock_collaborator), \
                patch("app.db.session.add"), \
                patch("app.db.session.commit"):

            payload = {
                "first_name": 1,
                "last_name": False,
                "email": "invalidemailformat",
                "password": "unsecurepassword",
                "role_id": "3"
            }

            response = test_client.post("/collaborator", json=payload)

            assert response.status_code == 400, f"Unexpected status code: {response.status_code}. Response: {response.json}"
            assert response.json["message"] == "Validation errors"


@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("app.db.session.get")
@patch("app.db.session.commit")
def test_edit_collaborator_success(mock_commit, mock_get, mock_auth, test_client):
    
    with app.app_context():
        mock_collaborator = MagicMock(spec=Collaborator)
        mock_collaborator.id = 1
        mock_collaborator.first_name = "John"
        mock_collaborator.last_name = "Doe"
        mock_collaborator.email = "john@example.com"
        mock_collaborator.role_id = RoleEnum.SALES.value

        mock_collaborator.to_dict.return_value = {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "role_id": RoleEnum.SALES.value
        }

        mock_get.return_value = mock_collaborator

        updated_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com"
        }

        response = test_client.patch("/collaborator/1", json=updated_data)

        assert response.status_code == 200, f"Unexpected status code: {response.status_code}. Response: {response.json}"
        assert response.json["message"] == "Collaborator updated successfully!"
        assert "collaborator" in response.json
        mock_commit.assert_called_once()

        mock_collaborator.first_name = updated_data["first_name"]
        mock_collaborator.last_name = updated_data["last_name"]
        mock_collaborator.email = updated_data["email"]


@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("app.db.session.get")
def test_edit_collaborator_not_found(mock_get, mock_auth, test_client):
    
    with app.app_context():
        mock_get.return_value = None
        
        updated_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com"
        }
        
        response = test_client.patch("/collaborator/999", json=updated_data)

        assert response.status_code == 404, f"Unexpected status code: {response.status_code}. Response: {response.json}"
        assert response.json["message"] == "Collaborator not found"


@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("app.db.session.get")
@patch("app.db.session.commit")
def test_edit_collaborator_db_error(mock_commit, mock_get, mock_auth, test_client):
    
    with app.app_context():
        mock_collaborator = MagicMock(spec=Collaborator)
        mock_collaborator.id = 1
        mock_collaborator.first_name = "John"
        mock_collaborator.last_name = "Doe"
        mock_collaborator.email = "john@example.com"
        mock_collaborator.role_id = RoleEnum.SALES.value
        
        mock_get.return_value = mock_collaborator
        
        mock_commit.side_effect = Exception("Database error")
        
        updated_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com"
        }
        
        response = test_client.patch("/collaborator/1", json=updated_data)

        assert response.status_code == 500, f"Unexpected status code: {response.status_code}. Response: {response.json}"
        assert response.json["message"] == "Error updating collaborator"
        assert "error" in response.json
        
@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("app.db.session.get")
@patch("app.db.session.commit")
def test_update_password_success(mock_commit, mock_get, mock_auth, test_client):
    with app.app_context():
        mock_collaborator = MagicMock(spec=Collaborator)
        mock_collaborator.id = 1
        mock_collaborator.first_name = "John"
        mock_collaborator.last_name = "Doe"
        mock_collaborator.email = "john@example.com"
        mock_collaborator.role_id = RoleEnum.SALES.value
        mock_collaborator.set_password = MagicMock()

        mock_get.return_value = mock_collaborator

        updated_data = {
            "password": "newPassword123!"
        }

        response = test_client.patch("/collaborator/update-password/1", json=updated_data)

        assert response.status_code == 200, f"Unexpected status code: {response.status_code}. Response: {response.json}"
        assert response.json["message"] == "Password updated successfully!"
        mock_commit.assert_called_once()
        mock_collaborator.set_password.assert_called_once_with("newPassword123!")

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("app.db.session.get")
@patch("app.db.session.commit")
def test_update_password_collaborator_not_found(mock_commit, mock_get, mock_auth, test_client):
    with app.app_context():
        mock_get.return_value = None

        updated_data = {
            "password": "newPassword123!"
        }

        response = test_client.patch("/collaborator/update-password/999", json=updated_data)

        assert response.status_code == 403, f"Unexpected status code: {response.status_code}. Response: {response.json}"
        assert response.json["message"] == "Permission denied"

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("app.db.session.get")
@patch("app.db.session.commit")
def test_update_password_validation_error(mock_commit, mock_get, mock_auth, test_client):
    with app.app_context():
        mock_collaborator = MagicMock(spec=Collaborator)
        mock_collaborator.id = 1
        mock_collaborator.first_name = "John"
        mock_collaborator.last_name = "Doe"
        mock_collaborator.email = "john@example.com"
        mock_collaborator.role_id = RoleEnum.SALES.value
        mock_collaborator.set_password = MagicMock()

        mock_get.return_value = mock_collaborator

        updated_data = {}

        response = test_client.patch("/collaborator/update-password/1", json=updated_data)

        assert response.status_code == 400, f"Unexpected status code: {response.status_code}. Response: {response.json}"
        assert response.json["message"] == "Invalid or missing data"

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("app.db.session.get")
@patch("app.db.session.commit")
def test_update_password_db_error(mock_commit, mock_get, mock_auth, test_client):
    with app.app_context():
        mock_collaborator = MagicMock(spec=Collaborator)
        mock_collaborator.id = 1
        mock_collaborator.first_name = "John"
        mock_collaborator.last_name = "Doe"
        mock_collaborator.email = "john@example.com"
        mock_collaborator.role_id = RoleEnum.SALES.value
        mock_collaborator.set_password = MagicMock()

        mock_get.return_value = mock_collaborator

        mock_commit.side_effect = Exception("Database error")

        updated_data = {
            "password": "newPassword123!"
        }

        response = test_client.patch("/collaborator/update-password/1", json=updated_data)

        assert response.status_code == 500, f"Unexpected status code: {response.status_code}. Response: {response.json}"
        assert response.json["message"] == "Error updating Password"
        assert "error" in response.json

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("app.db.session.get")
@patch("app.db.session.delete")
@patch("app.db.session.commit")
def test_delete_collaborator_success(mock_commit, mock_delete, mock_get, mock_auth, test_client):
    
    with app.app_context():
        mock_collaborator = MagicMock(spec=Collaborator)
        mock_collaborator.to_dict.return_value = {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "role_id": RoleEnum.SALES.value
        }
        
        mock_get.return_value = mock_collaborator
        
        response = test_client.delete("/collaborator/1")

        assert response.status_code == 200, f"Unexpected status code: {response.status_code}. Response: {response.json}"
        assert response.json["message"] == "Collaborator deleted successfully!"
        assert "collaborator" in response.json


@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("app.db.session.get")
def test_delete_collaborator_not_found(mock_get, mock_auth, test_client):
    
    with app.app_context():
        mock_get.return_value = None
        
        response = test_client.delete("/collaborator/999")

        assert response.status_code == 404, f"Unexpected status code: {response.status_code}. Response: {response.json}"
        assert response.json["message"] == "Collaborator not found"

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("app.db.session.get")
@patch("app.db.session.delete")
@patch("app.db.session.commit")
def test_delete_collaborator_db_error(mock_commit, mock_delete, mock_get, mock_auth, test_client):
    
    with app.app_context():
        mock_collaborator = MagicMock(spec=Collaborator)
        mock_collaborator.to_dict.return_value = {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "role_id": RoleEnum.SALES.value
        }
        
        mock_get.return_value = mock_collaborator
        
        mock_commit.side_effect = Exception("Database error")
        
        response = test_client.delete("/collaborator/1")

        assert response.status_code == 500, f"Unexpected status code: {response.status_code}. Response: {response.json}"
        assert response.json["message"] == "Error deleting collaborator"
        assert "error" in response.json