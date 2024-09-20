import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.student import StudentLogin,ClassMaster
from datetime import datetime
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
#     test_client.post('/auth/signup', json={
#   "userid": "admin123",
#   "password": "admin123",
#   "user_type": "admin"
# })
    response = test_client.post('/auth/login', json={
  "userid": "1",
  "password": "111",
  "user_type": "student"
})

    print("Login response status code:", response.status_code)
    print("Login response data:", response.json)
    
    assert response.status_code == 200, f"Login failed with status code {response.status_code}"
    
    data = response.json
    if 'token' not in data:
        pytest.fail(f"Login response missing 'token': {data}")
    
    access_token = data['token']
    student_id=data['data']['id']
    return {'Authorization': access_token,'student_id':student_id}

def seed_data():
    student_login = StudentLogin.query.filter_by(userid='1').first()
    if not student_login:
        raise ValueError("Admin login with userid 'admin123' not found")

    student_id = student_login.student_id
    class_master = ClassMaster.query.filter_by(class_name='Samples Class').first()
    
    if not class_master:
        # If it doesn't exist, create the class
        class_master = ClassMaster(
            class_name='Samples Class',
            is_active=True,
            is_deleted=False,
            created_by='1',
            updated_by='1'
        )
        db.session.add(class_master)
        db.session.commit()

    return {
        'student_login_id': student_id,
        'class_master_id': class_master.class_id,
    }
def cleanup_seed_data():
    # Clean up the data after the test
    class_master = ClassMaster.query.filter_by(class_name='Samples Class').first()
    if class_master:
        db.session.delete(class_master)
        db.session.commit()
def test_class_list_success(test_client, auth_header):
    response = test_client.get('/class/list', headers=auth_header)
    assert response.status_code == 200
    response_json = response.get_json()
    assert 'message' in response_json
    assert response_json['message'] == 'Class Found Successfully'
    assert 'data' in response_json
    assert isinstance(response_json['data'], list)  


import time
def test_class_add_success(test_client, auth_header):
  
    base_class_name = 'Unique Class Name'
    unique_suffix = str(int(time.time())) 
    unique_class_name = f"{base_class_name}_{unique_suffix}"

   
    response = test_client.post('/class/add', json={
        'class_name': unique_class_name
    }, headers=auth_header)

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['message'] == 'Class Created Successfully'
def test_class_edit_success(test_client, auth_header):
    # Check if the class you're trying to update already exists
    existing_class = test_client.get(f'/class/get/{seed_ids["class_master_id"]}', headers=auth_header)
    existing_class_json = existing_class.get_json()

    # Generate a unique class name using a timestamp to avoid conflicts
    base_class_name = 'Updated Class Name'
    unique_suffix = str(int(time.time()))  # Appends current timestamp as a suffix
    new_class_name = f"{base_class_name}_{unique_suffix}"

    response = test_client.put(f'/class/edit/{seed_ids["class_master_id"]}', json={
        'class_name': new_class_name
    }, headers=auth_header)

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['message'] == 'Class Updated Successfully'



    # Clean up by deleting the class after the test
    
   
def test_class_get_success(test_client, auth_header):
    # Assuming an existing class with ID 1
    response = test_client.get(f'/class/get/{seed_ids["class_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['message'] == 'Class Found Successfully'
    assert 'data' in response_json

def test_class_delete_success(test_client, auth_header):
    # Assuming an existing class with ID 1
    response = test_client.delete(f'/class/delete/{seed_ids["class_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['message'] == 'Class Deleted Successfully'

def test_class_activate_success(test_client, auth_header):
    # Assuming an existing class with ID 1
    response = test_client.put(f'/class/activate/{seed_ids["class_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['message'] == 'Class Activated Successfully'

def test_class_deactivate_success(test_client, auth_header):
    # Assuming an existing class with ID 1
    response = test_client.put(f'/class/deactivate/{seed_ids["class_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['message'] == 'Class Deactivated Successfully'