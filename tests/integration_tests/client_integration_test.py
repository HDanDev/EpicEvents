import pytest
from app import app, db
import os
from models.collaborators import Collaborator
from models.roles import RoleEnum
from tests.main_fixture import test_client, seed_roles, create_sales_collaborator, sales_login, secure_password

        
@pytest.fixture
def auth_token(test_client, create_sales_collaborator):
    """Logs in as an admin and returns a valid token"""
    login_data = {
        "email": sales_login,
        "password": secure_password
        }
    response = test_client.post("/auth/login", json=login_data)
    
    assert response.status_code == 200
    return response.json["token"]

def test_create_edit_delete_client(test_client, auth_token):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    client_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@email.com",
        "phone": "0606060606",
        "company_name": "Légia",
    }
    
    # Step 1: Create the client
    response = test_client.post("/client", json=client_data, headers=headers)
    assert response.status_code == 200

    # Step 2: Retrieve the client's ID
    client_id = response.json["client"]["id"]

    # Step 3: Update the client
    updated_data = {"first_name": "Jonathan"}
    response = test_client.patch(f"/client/{client_id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json["client"]["first_name"] == "Jonathan"
    
    # Step 4: Delete the client
    response = test_client.delete(f"/client/{client_id}", headers=headers)
    assert response.status_code == 200

    # Step 5: Attempt to get the client to ensure of the deletion' success
    response = test_client.get(f"/client/{client_id}", headers=headers)
    # The asserted response here is 403 and not 404 due to
    # the authorize system that will return a unauthorized if
    # no client-collaborator relationship is found
    assert response.status_code == 403
