import pytest
from unittest.mock import patch, MagicMock
from app import app, db
from models import Collaborator, Contract, Client, Event
from models.roles import RoleEnum
from enums.relationships_enum import RelationshipEnum
from helpers.authorize_helper import encode_auth_token
from tests.main_fixture import test_client, seed_roles

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SALES.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_add_event_success(mock_auth, mock_relationship_check, test_client):
    with app.app_context():

        mock_sales_collaborator = MagicMock(spec=Collaborator)
        mock_sales_collaborator.id = 1
        mock_sales_collaborator.role_id = RoleEnum.SALES.value

        mock_client = MagicMock(spec=Client)
        mock_client.id = 10
        mock_client.commercial_id = mock_sales_collaborator.id

        mock_contract = MagicMock(spec=Contract)
        mock_contract.id = 100
        mock_contract.client_id = mock_client.id
        mock_contract.signed = True

        with patch("app.db.session.get", side_effect=lambda model, id:
            mock_contract if model == Contract and id == mock_contract.id else
            mock_sales_collaborator if model == Collaborator and id == mock_sales_collaborator.id else
            mock_client if model == Client and id == mock_client.id else
            None), \
            patch("models.clients.Client.query") as mock_client_query:

            mock_client_query.filter_by.return_value.first.return_value = mock_client

            payload = {
                "name": "Bigevent",
                "location": "1 Main Street, 1000 Paris, France",
                "attendees": 150,
                "notes": "A memorable event",
                "contract_id": mock_contract.id,
                "start_date": "2026-01-01T09:00:00Z",
                "end_date": "2026-01-02T18:00:00Z"
            }

            response = test_client.post("/event", json=payload)

            assert response.status_code == 200
            assert response.json["message"] == "Event added successfully!"
            assert "event" in response.json

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.MANAGEMENT.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_get_events_success(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        with patch("models.events.Event.query") as mock_query:
            mock_query.filter_by.return_value = mock_query
            mock_query.order_by.return_value = mock_query 
            mock_query.all.return_value = [MagicMock(spec=Event, to_dict=lambda: {"id": 1, "name": "Conference", "attendees": 150})]
            
            response = test_client.get("/events")
            assert response.status_code == 200
            assert isinstance(response.json, list)
            assert len(response.json) == 1
            assert response.json[0]["id"] == 1


@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SUPPORT.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_get_event_success(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        mock_event = MagicMock(spec=Event, to_dict=lambda: {"id": 1, "name": "Conference", "attendees": 150})
        
        with patch("app.db.session.get", return_value=mock_event):
            response = test_client.get("/event/1")
            assert response.status_code == 200
            assert response.json["id"] == 1

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SUPPORT.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_get_event_not_found(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        with patch("app.db.session.get", return_value=None):
            response = test_client.get("/event/99")
            assert response.status_code == 404
            assert response.json["message"] == "Event not found"

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SUPPORT.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_update_event_patch_success(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        mock_event = MagicMock(spec=Event, to_dict=lambda: {"id": 1, "name": "Updated Conference"})
        
        with patch("app.db.session.get", return_value=mock_event), \
            patch("app.db.session.commit", return_value=None):
            response = test_client.patch("/event/1", json={"name": "Updated Conference"})
            assert response.status_code == 200
            assert response.json["message"] == "Event updated successfully!"

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SUPPORT.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_update_event_patch_not_found(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        with patch("app.db.session.get", return_value=None):
            response = test_client.patch("/event/99", json={"name": "Updated Conference"})
            assert response.status_code == 404
            assert response.json["message"] == "Event not found"

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SALES.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_delete_event_success(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        mock_event = MagicMock(spec=Event, to_dict=lambda: {"id": 1, "name": "Conference"})
        
        with patch("app.db.session.get", return_value=mock_event), \
            patch("app.db.session.delete", return_value=None), \
            patch("app.db.session.commit", return_value=None):
            response = test_client.delete("/event/1")
            assert response.status_code == 200
            assert response.json["message"] == "Event deleted successfully!"

@patch("helpers.authorize_helper.get_authenticated_collaborator", return_value=(MagicMock(id=1, role_id=RoleEnum.SALES.value), None, None))
@patch("helpers.authorize_helper.relationship_check_switch", return_value=None)
def test_delete_event_not_found(mock_auth, mock_relationship_check, test_client):
    with app.app_context():
        with patch("app.db.session.get", return_value=None):
            response = test_client.delete("/event/99")
            assert response.status_code == 404
            assert response.json["message"] == "Event not found"
