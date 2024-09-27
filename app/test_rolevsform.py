import pytest
from flask import jsonify
from app.models.role import  RoleVsFormMasterData, RoleMasterData,FormMasterData
from datetime import datetime
from faker import Faker
from app import app, db
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

from flask import jsonify

def seed_data():
    # Create a single RoleMaster entry
    role = RoleMasterData(
        role_name=faker.job(),
        created_by=faker.name(),
        updated_by=faker.name(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.session.add(role)
    db.session.commit()

    # Create a single FormMasterData entry
    form = FormMasterData(
        menu_master_id=faker.random_int(min=1, max=5),  # Adjust based on your existing menu data
        sub_menu_master_id=faker.random_int(min=1, max=5),  # Adjust based on your existing submenu data
        form_name=faker.catch_phrase(),
        form_url=faker.url(),
        form_description=faker.sentence(),
        is_menu_visible=faker.boolean(),
        created_by=faker.name(),
        updated_by=faker.name(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.session.add(form)
    db.session.commit()

    # Create a single RoleVsFormMaster entry
    role_vs_form = RoleVsFormMasterData(
        form_master_id=form.form_master_id,
        role_master_id=role.role_master_id,
        is_search=faker.boolean(),
        is_save=faker.boolean(),
        is_update=faker.boolean(),
        is_active=1,
        created_by=faker.name(),
        updated_by=faker.name(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.session.add(role_vs_form)
    db.session.commit()

    return {
        'role_master_id': role.role_master_id,
        'form_master_id': form.form_master_id,
        'role_form_master_id': role_vs_form.role_form_master_id  # Include the role_form_master_id
    }

def cleanup_seed_data():
    RoleVsFormMasterData.query.filter_by(role_form_master_id=seed_ids['role_form_master_id']).delete()
    db.session.commit()

# Test: List RoleVsForm
def test_list_rolevsform(test_client, auth_header):
    response = test_client.get('/rolevsform/list', headers=auth_header)
    assert response.status_code == 200

# Test: Add RoleVsForm
def test_add_rolevsform(test_client, auth_header):
    payload = {
        "role_master_id": seed_ids['role_master_id'],
        "form_master_id": seed_ids['form_master_id'],
        "is_search": True,
        "is_save": True,
        "is_update": True
    }
    
    response = test_client.post('/rolevsform/add', json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'RolevsForm Data created successfully' in data['message']

# Test: Edit RoleVsForm
def test_edit_rolevsform(test_client, auth_header):
    seed_ids = seed_data()  # Seed initial data

    payload = {
        "role_master_id": str(seed_ids['role_master_id']),
        "form_master_id": str(seed_ids['form_master_id']),
        "is_search": False,
        "is_save": False,
        "is_update": False
    }
    
    response = test_client.put(f'/rolevsform/edit/{seed_ids["role_form_master_id"]}', json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'RolevsForm Data updated successfully' in data['message']

      # Cleanup after test

# Test: Get RoleVsForm by ID
def test_get_rolevsform(test_client, auth_header):
    seed_ids = seed_data()  # Seed initial data

    response = test_client.get(f'/rolevsform/edit/{seed_ids["role_form_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'RolevsForm Data found Successfully' in data['message']

     # Cleanup after test

# Test: Activate RoleVsForm
def test_activate_rolevsform(test_client, auth_header):
      # Seed initial data

    response = test_client.put(f'/rolevsform/activate/{seed_ids["role_form_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Rolevsform activated successfully' in data['message']

      # Cleanup after test

# Test: Deactivate RoleVsForm
def test_deactivate_rolevsform(test_client, auth_header):
      # Seed initial data

    response = test_client.put(f'/rolevsform/deactivate/{seed_ids["role_form_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Rolevsform deactivated successfully' in data['message']

     # Cleanup after test

# Test: Delete RoleVsForm
def test_delete_rolevsform(test_client, auth_header):
    # Seed initial data

    response = test_client.delete(f'/rolevsformdelete/{seed_ids["role_form_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Rolevsform deleted successfully' in data['message']

      # Cleanup after test
def test_add_role_vs_form_missing_form_master_id(test_client, auth_header):
    response = test_client.post(
        '/rolevsform/add', 
        json={
            'role_master_id': str(faker.random_int(min=1, max=100)), 
            'is_search': True, 
            'is_save': True, 
            'is_update': True
        }, 
        headers=auth_header
    )
    
    assert response.json['message'] == 'Please Provide RolevsForm Data Id'

def test_add_role_vs_form_missing_role_master_id(test_client, auth_header):
    response = test_client.post(
        '/rolevsform/add', 
        json={
            'form_master_id': str(faker.random_int(min=1, max=100)), 
            'is_search': True, 
            'is_save': True, 
            'is_update': True
        }, 
        headers=auth_header
    )
    
    assert response.json['message'] == 'Please Provide Role Id'

def test_edit_role_vs_form_missing_form_master_id(test_client, auth_header):
    response = test_client.put(
        f'/rolevsform/edit/{seed_ids["role_form_master_id"]}', 
        json={
            'role_master_id': str(faker.random_int(min=1, max=100)), 
            'is_search': True, 
            'is_save': True, 
            'is_update': True
        }, 
        headers=auth_header
    )
    
    assert response.json['message'] == 'Please Provide From Id'

def test_edit_role_vs_form_missing_role_master_id(test_client, auth_header):
    response = test_client.put(
        f'/rolevsform/edit/{seed_ids["role_form_master_id"]}', 
        json={
            'form_master_id': str(faker.random_int(min=1, max=100)), 
            'is_search': True, 
            'is_save': True, 
            'is_update': True
        }, 
        headers=auth_header
    )
    
    assert response.json['message'] == 'Please Provide Role Id'