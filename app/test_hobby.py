import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.student import Hobby
import time
from faker import Faker
from app.models.student import StudentLogin
from app.models.log import LoginLog
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
    unique_email = faker.unique.email()

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
    hobby_name = faker.word()  # Generate a fake hobby name
    hobby = Hobby(hobby_name=hobby_name, is_active=1, created_by='1')
    db.session.add(hobby)
    db.session.commit()
    return {'hobby_id': hobby.hobby_id}

def cleanup_seed_data():
    hobby = Hobby.query.filter_by(hobby_id=seed_ids['hobby_id']).first()  # Adjust as needed
    if hobby:
        db.session.delete(hobby)
        db.session.commit()
def test_hobby_list(test_client, auth_header):
    response = test_client.get('/hobby/list', headers=auth_header)
    assert response.status_code == 200
    assert 'Hobbies found Successfully' in response.json['message']

def test_hobby_add(test_client, auth_header):
    unique_hobby_name = f"Hobby {int(time.time())}"
    response = test_client.post('/hobby/add', headers=auth_header, json={
        "hobby_name": unique_hobby_name
    })
    assert response.status_code == 200
    assert 'Hobby created successfully' in response.json['message']

    # Cleanup: Delete the hobby added during this test
    Hobby.query.filter_by(hobby_name=unique_hobby_name).delete()
    db.session.commit()

def test_hobby_edit(test_client, auth_header):
    new_hobby_name = f"Updated Hobby {int(time.time())}"
    response = test_client.put(f'/hobby/edit/{seed_ids["hobby_id"]}', headers=auth_header, json={
        "hobby_name": new_hobby_name
    })
    assert response.status_code == 200
    assert 'Hobby updated successfully' in response.json['message']

def test_hobby_get(test_client, auth_header):
    response = test_client.get(f'/hobby/edit/{seed_ids["hobby_id"]}', headers=auth_header)
    assert response.status_code == 200
    assert 'Hobby found Successfully' in response.json['message']

def test_hobby_delete(test_client, auth_header):
    hobby_id = seed_ids['hobby_id']
    response = test_client.delete(f'/hobbydelete/{hobby_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Hobby deleted successfully' in response.json['message']

def test_hobby_activate(test_client, auth_header):
    response = test_client.put(f'/hobby/activate/{seed_ids["hobby_id"]}', headers=auth_header)
    assert response.status_code == 200
    assert 'Hobby activated successfully' in response.json['message']

def test_hobby_deactivate(test_client, auth_header):
    response = test_client.put(f'/hobby/deactivate/{seed_ids["hobby_id"]}', headers=auth_header)
    assert response.status_code == 200
    assert 'Hobby deactivated successfully' in response.json['message']

def test_hobby_add_missing_hobby_name(test_client, auth_header):
    # Test adding hobby with missing hobby_name
    response = test_client.post('/hobby/add', json={}, headers=auth_header)
    
    assert response.is_json
    
    assert response.json['message'] == 'Please Provide Hobby name'

def test_hobby_edit_missing_hobby_name(test_client, auth_header):
    # Test adding hobby with missing hobby_name
    response = test_client.put(f'/hobby/edit/{seed_ids["hobby_id"]}', json={}, headers=auth_header)
    
    assert response.is_json
    
    assert response.json['message'] == 'Please provide hobby name'






def test_hobby_edit_invalid(test_client, auth_header):
    new_hobby_name = f"Updated Hobby {int(time.time())}"
    response = test_client.put('/hobby/edit/885695', headers=auth_header, json={
        "hobby_name": new_hobby_name
    })
   
    assert 'Hobby not found' in response.json['message']

def test_hobby_get_invalid(test_client, auth_header):
    response = test_client.get('/hobby/edit/888569', headers=auth_header)
  
    assert 'Hobby not found' in response.json['message']

def test_hobby_delete_invalid(test_client, auth_header):
    
    response = test_client.delete('/hobbydelete/888956', headers=auth_header)
   
    assert 'hobby not found' in response.json['message']

def test_hobby_activate_invalid(test_client, auth_header):
    response = test_client.put('/hobby/activate/8875965', headers=auth_header)

    assert 'Hobby not found' in response.json['message']

def test_hobby_deactivate_invalid(test_client, auth_header):
    response = test_client.put('/hobby/deactivate/8899965', headers=auth_header)
   
    assert 'Hobby not found' in response.json['message']