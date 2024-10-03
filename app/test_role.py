import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.adminuser import AdminBasicInformation
from app.models.role import RoleMasterData
from faker import Faker
from app.models.student import StudentLogin
from app.models.log import LoginLog
import random
faker = Faker()

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            global seed_ids
            seed_ids = seed_data()  # Seed once for the module
        yield testing_client
        with app.app_context():
            cleanup_seed_data()  # Cleanup after all tests
            db.session.remove()

@pytest.fixture
def auth_header(test_client):
    unique_email = f"{faker.unique.email().split('@')[0]}_{random.randint(1000, 9999)}@example.com"

    # First, sign up a new user
    signup_response = test_client.post('/auth/signup', json={
        "userid": unique_email,  # Unique email for signup
        "password": "password",  # Assuming a fixed password
        "user_type": "student"
    })

    assert signup_response.status_code == 200, f"Signup failed with status code {signup_response.status_code}"
    assert signup_response.json['status'] == 200, f"Signup error: {signup_response.json['message']}"

    # Now, attempt to log in using the unique email directly
    login_response = test_client.post('/auth/login', json={
        "userid": unique_email,  # Use the same unique email
        "password": "password",  # Same password
        "user_type": "student"
    })

    assert login_response.status_code == 200, f"Login failed with status code {login_response.status_code}"

    # response = test_client.post('/auth/login', json={
    #     "userid": "1",
    #     "password": "111",
    #     "user_type": "student"
    # })

    # assert response.status_code == 200, f"Login failed with status code {response.status_code}"
    
    data = login_response.json
    if 'token' not in data:
        pytest.fail(f"Login response missing 'token': {data}")
    
    access_token = data['token']
    student_id = data['data']['id']  # Extracting student ID
    yield {'Authorization': access_token, 'student_id': student_id}
    user_to_delete = StudentLogin.query.filter_by(userid=unique_email).first()
    if user_to_delete:
        db.session.query(LoginLog).filter_by(student_id=user_to_delete.student_id).delete()
        db.session.delete(user_to_delete)
        db.session.commit()

def seed_data():
    role_name = faker.unique.word()  # Ensure unique role name
    role = RoleMasterData(
        role_name=role_name,
        is_active=1,
        created_by=1  # Assuming 'admin' is the admin ID or email
    )
    db.session.add(role)
    db.session.commit()
    
    return {
        'role_master_id': role.role_master_id,
        'role_name': role.role_name
    }

def cleanup_seed_data():
    RoleMasterData.query.filter_by(role_master_id=seed_ids['role_master_id']).delete()
    db.session.commit()

# Test: List Roles
def test_list_roles(test_client, auth_header):
    response = test_client.get('/role/list', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    

# Test: Add Role
def test_add_role(test_client, auth_header):
    payload = {
        "role_name": faker.unique.word()  # Using Faker for unique role name
    }
    
    response = test_client.post('/role/add', json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Role created successfully' in data['message']

# Test: Edit Role
def test_edit_role(test_client, auth_header):
    payload = {
        "role_name": faker.unique.word()  # Faker for new role name
    }
    response = test_client.put(f'/role/edit/{seed_ids["role_master_id"]}', json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Role updated successfully' in data['message']

# Test: Get Role by ID
def test_get_role(test_client, auth_header):
    response = test_client.get(f'/role/edit/{seed_ids["role_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Role found Successfully' in data['message']

# Test: Activate Role
def test_activate_role(test_client, auth_header):
    response = test_client.put(f'/role/activate/{seed_ids["role_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Role activated successfully' in data['message']

# Test: Deactivate Role
def test_deactivate_role(test_client, auth_header):
    response = test_client.put(f'/role/deactivate/{seed_ids["role_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Role deactivated successfully' in data['message']

# Test: Delete Role
def test_delete_role(test_client, auth_header):
    response = test_client.delete(f'/roledelete/{seed_ids["role_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Role deleted successfully' in data['message']
def test_add_role_missing_name(test_client, auth_header):
    response = test_client.post('/role/add', json={}, headers=auth_header)
    # assert response.status_code == 201
    assert response.is_json
    assert response.json['message'] == 'Please Provide Role name'

def test_edit_role_missing_name(test_client, auth_header):
    response = test_client.put(f'/role/edit/{seed_ids["role_master_id"]}', json={}, headers=auth_header)
    # assert response.status_code == 201
    assert response.is_json
    assert response.json['message'] == 'Please Provide Role name'





def test_edit_role_invalid(test_client, auth_header):
    payload = {
        "role_name": faker.unique.word()  # Faker for new role name
    }
    response = test_client.put('/role/edit/8885965', json=payload, headers=auth_header)
    
    data = response.get_json()
    assert 'Role not found' in data['message']

# Test: Get Role by ID
def test_get_role_invalid(test_client, auth_header):
    response = test_client.get('/role/edit/8885695', headers=auth_header)

    data = response.get_json()
    assert 'Role not found' in data['message']

# Test: Activate Role
def test_activate_role_invalid(test_client, auth_header):
    response = test_client.put('/role/activate/8859659', headers=auth_header)
   
    data = response.get_json()
    assert 'Role not found' in data['message']

# Test: Deactivate Role
def test_deactivate_role_invalid(test_client, auth_header):
    response = test_client.put('/role/deactivate/8856959', headers=auth_header)
  
    data = response.get_json()
    assert 'Role not found' in data['message']

# Test: Delete Role
def test_delete_role_invalid(test_client, auth_header):
    response = test_client.delete('/roledelete/8885695', headers=auth_header)
   
    data = response.get_json()
    assert 'Role not found' in data['message']