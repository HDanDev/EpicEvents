import pytest
from app import app, db
import os
from tests.main_fixture import test_client, seed_roles, create_manager_collaborator, create_sales_collaborator, create_client, manager_login, secure_password

        
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

def test_create_edit_delete_contract(test_client, auth_token, create_client):
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    client_id, commercial_id = create_client
        
    contract_data = {
        "costing": 50.0,
        "remaining_due_payment": 50.0,
        "signed": False,
        "client_id": client_id,
        "commercial_id": commercial_id,
    }
    
    # Step 1: Create the contract
    response = test_client.post("/contract", json=contract_data, headers=headers)
    assert response.status_code == 200

    # Step 2: Retrieve the contract's ID
    contract_id = response.json["contract"]["id"]

    # Step 3: Update the contract
    updated_data = {"signed": True}
    response = test_client.patch(f"/contract/{contract_id}", json=updated_data, headers=headers)
    assert response.status_code == 200
    assert response.json["contract"]["signed"] == True
    
    # Step 4: Delete the contract
    response = test_client.delete(f"/contract/{contract_id}", headers=headers)
    assert response.status_code == 200

    # Step 5: Attempt to get the contract to ensure of the deletion' success
    response = test_client.get(f"/contract/{contract_id}", headers=headers)
    assert response.status_code == 404
