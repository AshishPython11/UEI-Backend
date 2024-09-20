import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.adminuser import AdminDescription, AdminLogin

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
    admin_description = AdminDescription(
        admin_id=admin_id,
        description='Test Description',
        is_active=1
    )
    db.session.add(admin_description)
    db.session.commit()

    return {
        'admin_id': admin_id,
        'admin_description_id': admin_description.id
    }

def test_get_admin_description_list(test_client, auth_header):
    response = test_client.get('/admin_profile_description/list', headers=auth_header)
    
    # Print response details for debugging
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Data: {response.json}")

    # Check if the status code is either 200 or 404
    assert response.status_code in [200, 404], f"Unexpected status code: {response.status_code}"
    
    if response.status_code == 200:
        data = response.json
        assert data['message'] == 'Admin Profile Descriptions found Successfully'
        assert 'data' in data
        assert isinstance(data['data'], list)
    elif response.status_code == 404:
        data = response.json
        assert data['message'] == 'No Admin Profile Description found'

def test_get_all_admin_descriptions(test_client, auth_header):
    response = test_client.get('/admin_profile_description/alldata', headers=auth_header)
    assert response.status_code in [200, 404]
    data = response.json
    if response.status_code == 200:
        assert data['message'] == 'Admin Profile Descriptions found Successfully'
        assert 'data' in data
        assert isinstance(data['data'], list)
    elif response.status_code == 404:
        assert data['message'] == 'No Admin Profile Description found'

def test_add_admin_profile_description(test_client, auth_header):
    response = test_client.post('/admin_profile_description/add', json={
        'admin_id': auth_header['admin_id'],
        'description': 'New Test Description'
    }, headers=auth_header)
    
    assert response.status_code == 200
    data = response.json
    assert data['message'] == 'Admin Profile Description created successfully'

def test_edit_admin_profile_description(test_client, auth_header):
    add_response = test_client.post('/admin_profile_description/add', json={
        'admin_id': auth_header['admin_id'],
        'description': 'Another Test Description'
    }, headers=auth_header)
    
    assert add_response.status_code == 200
    

    response = test_client.put(f'/admin_profile_description/edit/{auth_header["admin_id"]}', json={
        'admin_id': auth_header['admin_id'],
        'description': 'Updated Description'
    }, headers=auth_header)
    
    assert response.status_code == 200
    data = response.json
    assert data['message'] == 'Admin Profile Description updated successfully'

def test_get_admin_profile_description_by_id(test_client, auth_header):
    response = test_client.get(f'/admin_profile_description/edit/{auth_header["admin_id"]}', headers=auth_header)
    
    assert response.status_code == 200
    data = response.json
    assert data['message'] == 'Admin Profile Description found Successfully'
    

def test_activate_admin_profile_description(test_client, auth_header):
    response = test_client.put(f'/admin_profile_description/activate/{seed_ids["admin_description_id"]}', headers=auth_header)
    
    assert response.status_code == 200
    data = response.json
    assert data['message'] == 'Admin Profile Description activated successfully'

def test_deactivate_admin_profile_description(test_client, auth_header):
    response = test_client.put(f'/admin_profile_description/deactivate/{seed_ids["admin_description_id"]}', headers=auth_header)
    
    assert response.status_code == 200
    data = response.json
    assert data['message'] == 'Admin Profile Description deactivated successfully'
