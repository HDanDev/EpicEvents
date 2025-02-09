import pytest
from app import app, db
from tests.main_fixture import *
from models.roles import RoleEnum 
from models import Contract
from helpers.authorize_helper import encode_auth_token

@pytest.fixture
def prepare_fixture_data(test_client, seed_roles):
    with app.app_context():
        management_collaborator = create_collaborator(RoleEnum.MANAGEMENT)
        sales_collaborator = create_collaborator(RoleEnum.SALES)
        support_collaborator = create_collaborator(RoleEnum.SUPPORT)
        
        db.session.add_all([management_collaborator, sales_collaborator, support_collaborator])
        db.session.commit()
        
        client = Client(
            first_name="Test",
            last_name="Client",
            email="testclient@email.com",
            phone="1234567890",
            company_name="TestCompany",
            commercial_id=sales_collaborator.id
        )
        db.session.add(client)
        db.session.commit()
        
        contract = Contract(
            costing=50.0,
            remaining_due_payment=50.0,
            signed=True,
            client_id=client.id,
            commercial_id=sales_collaborator.id
        )
        db.session.add(contract)
        db.session.commit()
        
        sales_collaborator_header = {"Authorization": f"Bearer {encode_auth_token(sales_collaborator.id)}"}
        management_collaborator_header = {"Authorization": f"Bearer {encode_auth_token(management_collaborator.id)}"}
        support_collaborator_header = {"Authorization": f"Bearer {encode_auth_token(support_collaborator.id)}"}
        
        return sales_collaborator_header, management_collaborator_header, support_collaborator_header, management_collaborator.id, sales_collaborator.id, support_collaborator.id, contract.id,    

def test_add_event_sales_role(test_client, prepare_fixture_data):
    (sales_collaborator_header, management_collaborator_header, support_collaborator_header, sales_collaborator_id, management_collaborator_id, support_collaborator_id, contract_id) = prepare_fixture_data

    # Step 1: Creating an event with a sales collaborator
    event_data = {
        "name": "Test Event",
        "start_date": "2026-01-01T09:00:00Z",
        "end_date": "2026-01-02T18:00:00Z",
        "location": "123 Main Street, 1000 Paris, Fra",
        "attendees": 50,
        "notes": "Important event",
        "contract_id": contract_id
    }

    response = test_client.post("/event", json=event_data, headers=sales_collaborator_header)
    event_id = response.json["event"]["id"]

    assert response.status_code == 200

    # Step 2: Assigning a support collaborator to an event
    update_data = {
        "support_id": support_collaborator_id
    }

    response = test_client.patch(f"/event/{event_id}", json=update_data, headers=management_collaborator_header)

    assert response.status_code == 200
    assert response.json["message"] == "Event updated successfully!"
    assert response.json["event"]["support_id"] == support_collaborator_id

    # Step 3: Updating event with a support collaborator
    new_event_name = 'New event name'
    update_data = {
        "name": new_event_name
    }

    response = test_client.patch(f"/event/{event_id}", json=update_data, headers=support_collaborator_header)

    assert response.status_code == 200
    assert response.json["message"] == "Event updated successfully!"
    assert response.json["event"]["name"] == new_event_name
    
    # Step 4: Deleting the event with a sales collaborator
    response = test_client.delete(f"/event/{event_id}", headers=sales_collaborator_header)
    assert response.status_code == 200

    # Step 5: Attempting to get the event with a support collaborator to ensure its deletion
    response = test_client.get(f"/event/{event_id}", headers=support_collaborator_header)
    assert response.status_code == 404
    
    


