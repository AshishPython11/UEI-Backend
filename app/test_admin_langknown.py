
import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from faker import Faker
faker=Faker()
import random
from app.models.log import *
from app.models.adminuser import AdminLanguageKnown,LanguageMaster,AdminLogin

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            
        yield testing_client
        with app.app_context():
            cleanup_data()
            db.session.remove()

@pytest.fixture
def auth_header(test_client):
#     test_client.post('/auth/signup', json={
#   "userid": "admin123",
#   "password": "admin123",
#   "user_type": "admin"
# })
    unique_email = f"{faker.unique.email().split('@')[0]}_{random.randint(1000, 9999)}@example.com"

    # First, sign up a new user
    signup_response = test_client.post('/auth/signup', json={
        "userid": unique_email,
        "password": "password",
        "user_type": "admin"
    })

    assert signup_response.status_code == 200, f"Signup failed with status code {signup_response.status_code}"
    assert signup_response.json['status'] == 200, f"Signup error: {signup_response.json['message']}"

    # Now, attempt to log in using the unique email
    login_response = test_client.post('/auth/login', json={
        "userid": unique_email,
        "password": "password",
        "user_type": "admin"
    })

    assert login_response.status_code == 200, f"Login failed with status code {login_response.status_code}"

    data = login_response.json
    if 'token' not in data:
        pytest.fail(f"Login response missing 'token': {data}")

    access_token = data['token']
    admin_id = data['data']['id'] 
    global seed_ids
    seed_ids = seed_data(admin_id) 
     # Extracting admin ID
    yield {'Authorization': access_token, 'admin_id': admin_id}
    # user_to_delete = AdminLogin.query.filter_by(userid=unique_email).first()
    # if user_to_delete:
    #     db.session.query(LoginLog).filter_by(admin_id=user_to_delete.admin_id).delete()
    #     db.session.delete(user_to_delete)
    #     db.session.commit()

def seed_data(admin_id):
    admin_login = AdminLogin.query.filter_by(admin_id=admin_id).first()
    if not admin_login:
        raise ValueError("Admin login with userid 'admin123' not found")

    admin_id = admin_login.admin_id
    language = LanguageMaster(language_name=faker.word())
    db.session.add(language)
    db.session.commit() 
    admin_language_known = AdminLanguageKnown(
        admin_id=admin_id,
        language_id=language.language_id,
        proficiency='Advanced',
        is_active=1
    )
    db.session.add(admin_language_known)
    db.session.commit()

    return {
        'admin_id': admin_id,
        'language_id': language.language_id,
        'admin_language_known_id': admin_language_known.id
    }

def cleanup_data():
    # Cleanup function to remove seeded data
    if 'admin_id' in seed_ids:
        admin_id = seed_ids['admin_id']
        
        # Delete related entries in tbl_login_log
        LoginLog.query.filter_by(admin_id=admin_id).delete()

        # Delete related entries in tbl_admin_language_known
        AdminLanguageKnown.query.filter_by(admin_id=admin_id).delete()
    
        # Finally, delete the AdminLogin entry
        user_to_delete = AdminLogin.query.filter_by(admin_id=admin_id).first()
        if user_to_delete:
            db.session.delete(user_to_delete)

    # Commit all deletions
    db.session.commit()
def test_add_admin_language_known(test_client, auth_header):
    response = test_client.post('/admin_language_known/add', json={
        'admin_id': auth_header['admin_id'],
        'language_id': seed_ids['language_id'],  # Replace with actual language_id from seeded data
        'proficiency': 'Intermediate'
    }, headers=auth_header)
    
    assert response.status_code == 200
    data = response.json
    assert data['message'] == 'Admin language Known created successfully'


def test_edit_admin_language_known(test_client, auth_header):
    # First, add an AdminLanguageKnown entry
    add_response = test_client.post('/admin_language_known/add', json={
        'admin_id': auth_header['admin_id'],
        'language_id': seed_ids['language_id'],  # Replace with actual language_id from seeded data
        'proficiency': 'Intermediate'
    }, headers=auth_header)
    
    assert add_response.status_code == 200
    
    # Now, edit the proficiency level
    response = test_client.put(f'/admin_language_known/edit/{auth_header["admin_id"]}', json={
        'admin_id': auth_header['admin_id'],
        'language_id': seed_ids['language_id'],  # Replace with actual language_id from seeded data
        'proficiency': 'Advanced'
    }, headers=auth_header)
    
    assert response.status_code == 200
    data = response.json
    assert data['message'] == 'Admin language Known updated successfully'
def test_get_admin_language_known_by_id(test_client, auth_header):
    response = test_client.get(f'/admin_language_known/edit/{auth_header["admin_id"]}', headers=auth_header)
    
    assert response.status_code == 200
    data = response.json
    assert data['message'] == 'Admin Language Known found Successfully'
def test_activate_admin_language_known(test_client, auth_header):
    # Seed data or manually add an entry for `admin_language_known`
    response = test_client.put(f'/admin_language_known/activate/{seed_ids["admin_language_known_id"]}', headers=auth_header)
    
    assert response.status_code == 200
    data = response.json
    assert data['message'] == 'Admin Language Known activated successfully'
def test_deactivate_admin_language_known(test_client, auth_header):
    # Seed data or manually add an entry for `admin_language_known`
    response = test_client.put(f'/admin_language_known/deactivate/{seed_ids["admin_language_known_id"]}', headers=auth_header)
    
    assert response.status_code == 200
    data = response.json
    assert data['message'] == 'Admin Language Known deactivated successfully'


def test_get_admin_langknown_list(test_client, auth_header):
    response = test_client.get('/admin_language_known/list', headers=auth_header)
    
    # Print response details for debugging
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Data: {response.json}")

    # Check if the status code is either 200 or 404
    assert response.status_code in [200, 404], f"Unexpected status code: {response.status_code}"
    
    if response.status_code == 200:
        data = response.json
        assert data['message'] == 'Admin Language Known found Successfully'
        assert 'data' in data
        assert isinstance(data['data'], list)
    elif response.status_code == 404:
        data = response.json
        assert data['message'] == 'No Admin Language Known found'
def test_get_admin_langknown_alldata(test_client, auth_header):
    response = test_client.get('/admin_language_known/alldata', headers=auth_header)
    
    # Print response details for debugging
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Data: {response.json}")

    # Check if the status code is either 200 or 404
    assert response.status_code in [200, 404], f"Unexpected status code: {response.status_code}"
    
    if response.status_code == 200:
        data = response.json
        assert data['message'] == 'Admin Language Known found Successfully'
        assert 'data' in data
        assert isinstance(data['data'], list)
    elif response.status_code == 404:
        data = response.json
        assert data['message'] == 'No Admin Language Known found'

def test_get_all_admin_language_known(test_client, auth_header):
    response = test_client.get('/admin_language_known/alldata', headers=auth_header)
    assert response.status_code in [200, 404]
    data = response.json
    if response.status_code == 200:
        assert data['message'] == 'Admin Language Known found Successfully'
        assert 'data' in data
    elif response.status_code == 404:
        assert data['message'] == 'No Admin Language Known found'


def test_multiple_add_admin_language_known(test_client, auth_header):
    data={
  "languages": [
    {
      "id": "1",
      "admin_id": str(auth_header['admin_id']),
      "language_id": str(seed_ids['language_id']),
      "proficiency": "string"
    },
     {
      "id": "2",
      "admin_id": str(auth_header['admin_id']),
      "language_id": str(seed_ids['language_id']),
      "proficiency": "string"
    }
  ]
}
    response = test_client.post('/admin_language_known/multiple/add', json=data, headers=auth_header)
    
    assert response.status_code == 200
    data = response.json
    
def test_multiple_edit_admin_language_known(test_client, auth_header):
    data={
  "languages": [
    {
      "id": "1",
      "admin_id": str(auth_header['admin_id']),
      "language_id": str(seed_ids['language_id']),
      "proficiency": "string"
    },
     {
      "id": "2",
      "admin_id": str(auth_header['admin_id']),
      "language_id": str(seed_ids['language_id']),
      "proficiency": "string"
    }
  ]
}
    response = test_client.put('/admin_language_known/multiple_language/edit', json=data, headers=auth_header)
    
    assert response.status_code == 200
    # data = response.json
    # assert data['message'] == 'Admin language Known Updated successfully'
def test_add_admin_language_known_missing_admin_id(test_client, auth_header):
    response = test_client.post('/admin_language_known/add', json={
        'language_id': 1,
        'proficiency': 'Fluent'
    }, headers=auth_header)

    
    assert response.json['message'] == 'Please Provide Admin Id'
def test_add_admin_language_known_missing_language_id(test_client, auth_header):
    response = test_client.post('/admin_language_known/add', json={
        'admin_id': auth_header['admin_id'],
        'proficiency': 'Fluent'
    }, headers=auth_header)

    
    assert response.json['message'] == 'Please Provide Language Id'
def test_add_admin_language_known_missing_proficiency(test_client, auth_header):
    response = test_client.post('/admin_language_known/add', json={
        'admin_id': auth_header['admin_id'],
        'language_id': 1
    }, headers=auth_header)

    
    assert response.json['message'] == 'Please Provide Proficiency'
def test_edit_admin_language_known_missing_admin_id(test_client, auth_header):
    response = test_client.put(f'/admin_language_known/edit/{auth_header['admin_id']}', json={
        'language_id': 1,
        'proficiency': 'Fluent'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Admin Id'


def test_edit_admin_language_known_missing_language_id(test_client, auth_header):
    response = test_client.put(f'/admin_language_known/edit/{auth_header['admin_id']}', json={
        'admin_id': auth_header['admin_id'],
        'proficiency': 'Fluent'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Language Id'


def test_edit_admin_language_known_missing_proficiency(test_client, auth_header):
    response = test_client.put(f'/admin_language_known/edit/{auth_header['admin_id']}', json={
        'admin_id': auth_header['admin_id'],
        'language_id': 1
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Proficiency'

def test_edit_admin_multiple_language_known_missing_record_id(test_client, auth_header):
    response = test_client.put('/admin_language_known/multiple_language/edit', json={
        'languages': [
            {
                'admin_id': auth_header['admin_id'],
                'language_id': seed_ids['language_id'],
                'proficiency': 'Fluent'
            }
        ]
    }, headers=auth_header)

    assert response.is_json
    # assert response.status_code == 400
    assert response.json['message'] == 'Input payload validation failed' 


def test_edit_admin_multiple_language_known_missing_admin_id(test_client, auth_header):
    response = test_client.put('/admin_language_known/multiple_language/edit', json={
        'languages': [
            {
                'id': 1,
                'language_id': seed_ids['language_id'],
                'proficiency': 'Fluent'
            }
        ]
    }, headers=auth_header)

    assert response.is_json
    # assert response.status_code == 400
    assert response.json['message'] == 'Input payload validation failed' 


def test_edit_admin_multiple_language_known_missing_language_id(test_client, auth_header):
    response = test_client.put('/admin_language_known/multiple_language/edit', json={
        'languages': [
            {
                'id': 1,
                'admin_id': auth_header['admin_id'],
                'proficiency': 'Fluent'
            }
        ]
    }, headers=auth_header)

    assert response.is_json
    # assert response.status_code == 400
    assert response.json['message'] == 'Input payload validation failed' 


def test_edit_admin_multiple_language_known_missing_proficiency(test_client, auth_header):
    response = test_client.put('/admin_language_known/multiple_language/edit', json={
        'languages': [
            {
                'id': 1,
                'admin_id': auth_header['admin_id'],
                'language_id': seed_ids['language_id']
            }
        ]
    }, headers=auth_header)

    assert response.is_json
    # assert response.status_code == 400
    assert response.json['message'] == 'Input payload validation failed' 


def test_edit_admin_multiple_language_known_invalid_payload(test_client, auth_header):
    response = test_client.put('/admin_language_known/multiple_language/edit', json={
        'languages': 'invalid_payload'  # not a list
    }, headers=auth_header)

    assert response.is_json
    # assert response.status_code == 400
    assert response.json['message'] == 'Input payload validation failed' 


def test_add_admin_multiple_language_known_missing_record_id(test_client, auth_header):
    response = test_client.post('/admin_language_known/multiple/add', json={
        'languages': [
            {
                'admin_id': auth_header['admin_id'],
                'language_id': seed_ids['language_id'],
                'proficiency': 'Fluent'
            }
        ]
    }, headers=auth_header)

    assert response.is_json
    # assert response.status_code == 400
    assert response.json['message'] == 'Input payload validation failed' 


def test_add_admin_multiple_language_known_missing_admin_id(test_client, auth_header):
    response = test_client.post('/admin_language_known/multiple/add', json={
        'languages': [
            {
                'id': 1,
                'language_id': seed_ids['language_id'],
                'proficiency': 'Fluent'
            }
        ]
    }, headers=auth_header)

    assert response.is_json
    # assert response.status_code == 400
    assert response.json['message'] == 'Input payload validation failed' 


def test_add_admin_multiple_language_known_missing_language_id(test_client, auth_header):
    response = test_client.post('/admin_language_known/multiple/add', json={
        'languages': [
            {
                'id': 1,
                'admin_id': auth_header['admin_id'],
                'proficiency': 'Fluent'
            }
        ]
    }, headers=auth_header)

    assert response.is_json
    # assert response.status_code == 400
    assert response.json['message'] == 'Input payload validation failed' 


def test_add_admin_multiple_language_known_missing_proficiency(test_client, auth_header):
    response = test_client.post('/admin_language_known/multiple/add', json={
        'languages': [
            {
                'id': 1,
                'admin_id': auth_header['admin_id'],
                'language_id': seed_ids['language_id']
            }
        ]
    }, headers=auth_header)

    assert response.is_json
    # assert response.status_code == 400
    assert response.json['message'] == 'Input payload validation failed' 


def test_add_admin_multiple_language_known_invalid_payload(test_client, auth_header):
    response = test_client.post('/admin_language_known/multiple/add', json={
        'languages': 'invalid_payload'  # not a list
    }, headers=auth_header)

    assert response.is_json
    # assert response.status_code == 400
    assert response.json['message'] == 'Input payload validation failed' 