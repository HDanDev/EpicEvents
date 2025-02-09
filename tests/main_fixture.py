import pytest
from app import app, db
from models.roles import RoleEnum
from models import Collaborator, Client
from unittest.mock import patch
from models.roles import Role


manager_login = 'testmanagement@email.com'
sales_login = 'testsales@email.com'
secure_password = 'AS3cureP@ssword'


@pytest.fixture
def test_client():
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.session.remove()
            db.drop_all()
        
                
@pytest.fixture
def seed_roles():
    roles = [
        Role(id=RoleEnum.MANAGEMENT.value, name="Management"),
        Role(id=RoleEnum.SALES.value, name="Sales"),
        Role(id=RoleEnum.SUPPORT.value, name="Support"),
    ]

    with app.app_context():
        for role in roles:
            existing_role = db.session.get(Role, role.id)
            if not existing_role:
                db.session.add(role)

        db.session.commit()


@pytest.fixture
def create_manager_collaborator():
    with app.app_context():
        manager = Collaborator(
            first_name='Test',
            last_name='Manage',
            email=manager_login,
            role_id=RoleEnum.MANAGEMENT.value
        )
        manager.set_password(secure_password)
        db.session.add(manager)
        db.session.commit()


@pytest.fixture
def create_sales_collaborator():
    with app.app_context():
        sales_collaborator = Collaborator(
            first_name='Test',
            last_name='Sales',
            email=sales_login,
            role_id=RoleEnum.SALES.value
        )
        sales_collaborator.set_password(secure_password)
        db.session.add(sales_collaborator)
        db.session.commit()
        return sales_collaborator.id


@pytest.fixture
def create_client(create_sales_collaborator):
    with app.app_context():
        client = Client(
            first_name="Test",
            last_name="Client",
            email="testclient@email.com",
            phone="1234567890",
            company_name="TestCompany",
            commercial_id=create_sales_collaborator
        )
        db.session.add(client)
        db.session.commit()
        return client.id, client.commercial_id


def create_collaborator(role):
    collaborator = Collaborator(
        first_name='Test',
        last_name=role.name.lower(),
        email=f"{role.name.lower()}@test.com",
        role_id=role.value
    )
    collaborator.set_password(secure_password)
    return collaborator
