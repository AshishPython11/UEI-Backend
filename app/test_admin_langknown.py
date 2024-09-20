
import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.adminuser import AdminLanguageKnown,LanguageMaster,AdminLogin

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            global seed_ids
            seed_ids = seed_data()  
        yield testing_client
        with app.app_context():
            db.session.remove()

@pytest.fixture
def auth_header(test_client):
#     test_client.post('/auth/signup', json={
#   "userid": "admin123",
#   "password": "admin123",
#   "user_type": "admin"
# })
    response = test_client.post('/auth/login', json={
  "userid": "admin123",
  "password": "admin123",
  "user_type": "admin"
})

    print("Login response status code:", response.status_code)
    print("Login response data:", response.json)
    
    assert response.status_code == 200, f"Login failed with status code {response.status_code}"
    
    data = response.json
    if 'token' not in data:
        pytest.fail(f"Login response missing 'token': {data}")
    
    access_token = data['token']
    admin_id=data['data']['id']
    return {'Authorization': access_token,'admin_id':admin_id}

def seed_data():
    admin_login = AdminLogin.query.filter_by(userid='admin123').first()
    if not admin_login:
        raise ValueError("Admin login with userid 'admin123' not found")

    admin_id = admin_login.admin_id
    language = LanguageMaster(language_name='English')
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
def test_add_admin_language_known(test_client, auth_header):
    response = test_client.post('/admin_language_known/add', json={
        'admin_id': auth_header['admin_id'],
        'language_id': 1,  # Replace with actual language_id from seeded data
        'proficiency': 'Intermediate'
    }, headers=auth_header)
    
    assert response.status_code == 200
    data = response.json
    assert data['message'] == 'Admin language Known created successfully'


def test_edit_admin_language_known(test_client, auth_header):
    # First, add an AdminLanguageKnown entry
    add_response = test_client.post('/admin_language_known/add', json={
        'admin_id': auth_header['admin_id'],
        'language_id': 1,  # Replace with actual language_id from seeded data
        'proficiency': 'Intermediate'
    }, headers=auth_header)
    
    assert add_response.status_code == 200
    
    # Now, edit the proficiency level
    response = test_client.put(f'/admin_language_known/edit/{auth_header["admin_id"]}', json={
        'admin_id': auth_header['admin_id'],
        'language_id': 1,  # Replace with actual language_id from seeded data
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

def test_get_all_admin_language_known(test_client, auth_header):
    response = test_client.get('/admin_language_known/alldata', headers=auth_header)
    assert response.status_code in [200, 404]
    data = response.json
    if response.status_code == 200:
        assert data['message'] == 'Admin Language Known found Successfully'
        assert 'data' in data
    elif response.status_code == 404:
        assert data['message'] == 'No Admin Language Known found'

