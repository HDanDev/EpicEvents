from unittest.mock import patch, MagicMock
import pytest
from flask import jsonify
from app import app, db
from models.roles import RoleEnum
from models import Client
from helpers.authorize_helper import role_restricted, relationship_check_switch, collaborator_client_relationship_check, collaborator_contract_relationship_check
from enums.relationships_enum import RelationshipEnum
from tests.main_fixture import test_client, seed_roles


@patch('helpers.authorize_helper.get_authenticated_collaborator')
def test_permission_denied_for_invalid_role(mock_get_authenticated_collaborator):
    mock_collaborator = MagicMock()
    mock_collaborator.role_id = RoleEnum.SUPPORT.value

    mock_get_authenticated_collaborator.return_value = (mock_collaborator, None, None)

    @role_restricted(roles=[RoleEnum.SALES, RoleEnum.MANAGEMENT])
    def protected_function(*args, **kwargs):
        return "Success"

    with app.app_context():
        result = protected_function(id=1)
        assert result[1] == 403
        assert result[0].json['message'] == 'Permission denied'


@patch('helpers.authorize_helper.get_authenticated_collaborator')
@patch('flask.jsonify')
def test_permission_denied_if_no_authenticated_user(mock_jsonify, mock_get_authenticated_collaborator):
    mock_response = MagicMock()
    mock_response.json = {'message': 'Token is missing or invalid'}
    mock_jsonify.return_value = mock_response
    mock_get_authenticated_collaborator.return_value = (None, mock_response, 403)

    @role_restricted(roles=[RoleEnum.SALES, RoleEnum.MANAGEMENT])
    def protected_function(*args, **kwargs):
        return "Success"

    with app.app_context():
        result = protected_function(id=1)
        assert result[1] == 403
        assert result[0].json['message'] == 'Token is missing or invalid'


@patch('helpers.authorize_helper.get_authenticated_collaborator')
@patch('flask.jsonify')
def test_token_invalid_or_expired(mock_jsonify, mock_get_authenticated_collaborator):
    mock_response = MagicMock()
    mock_response.json = {'message': 'Token is invalid or expired'}
    mock_jsonify.return_value = mock_response
    mock_get_authenticated_collaborator.return_value = (None, mock_response, 403)

    @role_restricted(roles=[RoleEnum.SALES, RoleEnum.MANAGEMENT])
    def protected_function(*args, **kwargs):
        return "Success"

    with app.app_context():
        result = protected_function(id=1)
        assert result[1] == 403
        assert result[0].json['message'] == 'Token is invalid or expired'


@patch('helpers.authorize_helper.get_authenticated_collaborator')
def test_successful_access_with_valid_role(mock_get_authenticated_collaborator):
    mock_collaborator = MagicMock()
    mock_collaborator.role_id = RoleEnum.SALES.value
    mock_get_authenticated_collaborator.return_value = (mock_collaborator, None, None)

    @role_restricted(roles=[RoleEnum.SALES, RoleEnum.MANAGEMENT])
    def protected_function(*args, **kwargs):
        return jsonify({"message": "Access granted"}), 200

    with app.app_context():
        result = protected_function(id=1)
        assert result[1] == 200
        assert result[0].json['message'] == 'Access granted'

def test_relationship_check_switch_none():
    mock_collaborator = MagicMock()
    mock_collaborator.role_id = RoleEnum.SALES.value

    result = relationship_check_switch(mock_collaborator, RelationshipEnum.NONE)

    assert result is None


@patch('helpers.authorize_helper.collaborator_client_relationship_check')
def test_relationship_check_switch_collaborator_client(mock_collaborator_client):
    mock_collaborator = MagicMock()
    mock_collaborator.role_id = RoleEnum.SALES.value
    mock_collaborator_client.return_value = 'Client Relationship Check Successful'

    result = relationship_check_switch(mock_collaborator, RelationshipEnum.COLLABORATOR_CLIENT)

    mock_collaborator_client.assert_called_once_with(mock_collaborator)

    assert result == 'Client Relationship Check Successful'


@patch('helpers.authorize_helper.collaborator_contract_relationship_check')
def test_relationship_check_switch_collaborator_contract(mock_collaborator_contract):
    mock_collaborator = MagicMock()
    mock_collaborator.role_id = RoleEnum.SALES.value
    mock_collaborator_contract.return_value = 'Contract Relationship Check Successful'

    result = relationship_check_switch(mock_collaborator, RelationshipEnum.COLLABORATOR_CONTRACT)

    mock_collaborator_contract.assert_called_once_with(mock_collaborator)

    assert result == 'Contract Relationship Check Successful'

def test_collaborator_client_relationship_check_success(test_client, seed_roles):
    mock_collaborator = MagicMock()
    mock_collaborator.id = 1
    client_id = 100

    mock_client = MagicMock()

    with app.app_context():
        with patch.object(Client, "query") as mock_query:
            mock_filter_by = MagicMock()
            mock_filter_by.first.return_value = mock_client
            mock_query.filter_by.return_value = mock_filter_by

            result = collaborator_client_relationship_check(mock_collaborator, id=client_id)

    assert result is None, f"Expected None, but got {result}"


def test_collaborator_client_relationship_check_permission_denied(test_client, seed_roles):
    mock_collaborator = MagicMock()
    mock_collaborator.id = 1
    client_id = 100

    with app.app_context():
        with patch.object(Client, "query") as mock_query:
            mock_filter_by = MagicMock()
            mock_filter_by.first.return_value = None
            mock_query.filter_by.return_value = mock_filter_by

            result = collaborator_client_relationship_check(mock_collaborator, id=client_id)

    assert result[1] == 403, f"Expected 403, but got {result[1]}"
    assert result[0].json['message'] == 'Permission denied, you only have the right to interact with clients you are assigned to'  


def test_collaborator_client_relationship_check_success(test_client, seed_roles):
    mock_collaborator = MagicMock()
    mock_collaborator.id = 1
    client_id = 100

    mock_client = MagicMock()

    with app.app_context():
        with patch.object(Client, "query") as mock_query:
            mock_filter_by = MagicMock()
            mock_filter_by.first.return_value = mock_client
            mock_query.filter_by.return_value = mock_filter_by

            result = collaborator_client_relationship_check(mock_collaborator, id=client_id)

    assert result is None, f"Expected None, but got {result}"

def test_collaborator_contract_relationship_check_success(test_client, seed_roles):
    mock_collaborator = MagicMock()
    mock_collaborator.id = 1
    contract_id = 200
    client_id = 100

    mock_contract = MagicMock()
    mock_contract.id = contract_id
    mock_contract.client_id = client_id
    mock_contract.signed = True

    mock_client = MagicMock()
    mock_client.commercial_id = mock_contract.id

    with app.test_request_context(json={"contract_id": contract_id}):
        with patch.object(db.session, "get", return_value=mock_contract), \
             patch.object(Client, "query") as mock_query:
            mock_filter_by = MagicMock()
            mock_filter_by.first.return_value = mock_client
            mock_query.filter_by.return_value = mock_filter_by
            result = collaborator_contract_relationship_check(mock_collaborator)

    assert result is None, f"Expected None, but got {result}"

def test_collaborator_contract_relationship_check_missing_contract_id(test_client, seed_roles):
    mock_collaborator = MagicMock()

    with app.test_request_context(json={}):
        result = collaborator_contract_relationship_check(mock_collaborator)

    assert result[1] == 403
    assert result[0].json['message'] == 'The contract_id field is mandatory to create an event'

def test_collaborator_contract_relationship_check_contract_not_found(test_client, seed_roles):
    mock_collaborator = MagicMock()
    contract_id = 200

    with app.test_request_context(json={"contract_id": contract_id}):
        with patch.object(db.session, "get", return_value=None):
            result = collaborator_contract_relationship_check(mock_collaborator)

    assert result[1] == 403
    assert result[0].json['message'] == 'The contract_id field is mandatory to create an event'

def test_collaborator_contract_relationship_check_contract_not_signed(test_client, seed_roles):
    mock_collaborator = MagicMock()
    contract_id = 200

    mock_contract = MagicMock()
    mock_contract.id = contract_id
    mock_contract.signed = False

    with app.test_request_context(json={"contract_id": contract_id}):
        with patch.object(db.session, "get", return_value=mock_contract):
            result = collaborator_contract_relationship_check(mock_collaborator)

    assert result[1] == 403
    assert result[0].json['message'] == 'Permission denied. Event creation is only available to clients with a signed contract'

def test_collaborator_contract_relationship_check_collaborator_not_assigned(test_client, seed_roles):
    mock_collaborator = MagicMock()
    mock_collaborator.id = 1
    contract_id = 200
    client_id = 100

    mock_contract = MagicMock()
    mock_contract.id = contract_id
    mock_contract.client_id = client_id
    mock_contract.signed = True

    with app.test_request_context(json={"contract_id": contract_id}):
        with patch.object(db.session, "get", return_value=mock_contract), \
             patch.object(Client, "query") as mock_query:
            mock_filter_by = MagicMock()
            mock_filter_by.first.return_value = None
            mock_query.filter_by.return_value = mock_filter_by

            result = collaborator_contract_relationship_check(mock_collaborator)

            assert result[1] == 403, f"Expected 403, but got {result}"
            assert result[0].json['message'] == 'Permission denied, you only have the right to create events for clients you are assigned to'

