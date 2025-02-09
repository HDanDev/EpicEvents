import pytest
from app import app, db
import os
from models.collaborators import Collaborator
from models.roles import RoleEnum
from tests.main_fixture import test_client, seed_roles, create_manager_collaborator, manager_login, secure_password


        
@pytest.fixture
def auth_token(test_client, create_manager_collaborator):
    """Logs in as an admin and returns a valid token"""
    login_data = {
        "email": manager_login,
        "password": secure_password
        }
    response = test_client.post("/auth/login", json=login_data)
    
    assert response.status_code == 200
    return response.json["token"]

def test_create_edit_delete_collaborator(test_client, auth_token, seed_roles):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    collaborator_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "password": "S3curep@ssword",
        "role_id": RoleEnum.SALES.value,
    }
    response = test_client.post("/collaborator", json=collaborator_data, headers=headers)
    assert response.status_code == 200

    collaborator_id = response.json["collaborator"]["id"]

    updated_data = {"first_name": "Jonathan"}
    response = test_client.patch(f"/collaborator/{collaborator_id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json["collaborator"]["first_name"] == "Jonathan"
    
    response = test_client.delete(f"/collaborator/{collaborator_id}", headers=headers)
    assert response.status_code == 200

    response = test_client.get(f"/collaborator/{collaborator_id}", headers=headers)
    assert response.status_code == 404
    
def test_login_edit_password_logout_login(test_client, auth_token, create_manager_collaborator, seed_roles):
    headers = {"Authorization": f"Bearer {auth_token}"}

    # Step 1: Retrieve the manager's ID
    manager_id = Collaborator.query.filter_by(email=manager_login).first().id

    # Step 2: Change the manager's name
    updated_role_data = {"role_id": RoleEnum.SALES.value}
    response = test_client.patch(f"/collaborator/{manager_id}", json=updated_role_data, headers=headers)
    assert response.status_code == 200
    assert response.json["collaborator"]["role_id"] == RoleEnum.SALES.value

    # Step 3: Change the password
    new_password = "NewSecureP@ssword123"
    password_data = {"password": new_password}
    response = test_client.patch(f"/collaborator/update-password/{manager_id}", json=password_data, headers=headers)
    assert response.status_code == 200
    assert response.json["message"] == "Password updated successfully!"

    # Step 4: Logout (invalidate the token)
    response = test_client.post("/auth/logout", headers=headers)
    assert response.status_code == 200

    # Step 5: Try logging in with the old password (should fail)
    old_login_data = {
        "email": manager_login,
        "password": secure_password
    }
    response = test_client.post("/auth/login", json=old_login_data)
    assert response.status_code == 401  # Unauthorized

    # Step 6: Log in with the new password (should succeed)
    new_login_data = {
        "email": manager_login,
        "password": new_password
    }
    response = test_client.post("/auth/login", json=new_login_data)
    assert response.status_code == 200
    assert "token" in response.json

