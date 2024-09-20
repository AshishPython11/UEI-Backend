
import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.adminuser import AdminContact,AdminLogin

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
    admin_contact = AdminContact(
        admin_id=admin_login.admin_id,  # Use the admin_id from AdminLogin
        email_id='admin_seeder@example.com',
        mobile_isd_call='+91',
        mobile_no_call='1234567890',
        mobile_isd_watsapp='+91',
        mobile_no_watsapp='9876543210'
    )
    db.session.add(admin_contact)
    db.session.commit()

    return {
        'admin_id': admin_login.admin_id,
        'admin_contact_id': admin_contact.admin_contact_id
    }
def test_add_admin_contact(test_client, auth_header):
    response = test_client.post('/admin_contact/add', json={
        'admin_id': auth_header['admin_id'],  # Use admin_id from seed data
        'mobile_isd_call': '+91',
        'mobile_no_call': '9876543211',
        'mobile_isd_watsapp': '+91',
        'mobile_no_watsapp': '9876543211',
        'email_id': 'admin_new@example.com'
    }, headers=auth_header)
    
    assert response.status_code == 200
    assert response.json['message'] == 'Admin Contact created successfully'

# Test case for editing an existing admin contact
def test_edit_admin_contact(test_client, auth_header):
    response = test_client.put(f'/admin_contact/edit/{auth_header["admin_id"]}', json={
        'admin_id': auth_header['admin_id'],  # Use admin_id from seed data
        'mobile_isd_call': '+91',
        'mobile_no_call': '9999999999',  # Updated mobile number
        'mobile_isd_watsapp': '+91',
        'mobile_no_watsapp': '9876543210',
        'email_id': 'admin_seeder@example.com'
    }, headers=auth_header)
    
    assert response.status_code == 200
    assert response.json['message'] == 'Admin Contact updated successfully'

# Test case for activating an admin contact
def test_activate_admin_contact(test_client, auth_header):
    response = test_client.put(f'/admin_contact/activate/{seed_ids["admin_contact_id"]}', headers=auth_header)
    
    assert response.status_code == 200
    assert response.json['message'] == 'Admin Contact activated successfully'

# Test case for deactivating an admin contact
def test_deactivate_admin_contact(test_client, auth_header):
    response = test_client.put(f'/admin_contact/deactivate/{seed_ids["admin_contact_id"]}', headers=auth_header)
    
    assert response.status_code == 200
    assert response.json['message'] == 'Admin Contact deactivated successfully'

# Test case for listing all admin contacts
def test_list_admin_contacts(test_client, auth_header):
    response = test_client.get('/admin_contact/list', headers=auth_header)
    assert response.status_code == 200
    assert 'data' in response.json
    assert isinstance(response.json['data'], list)
def test_get_all_admin_constact_known(test_client, auth_header):
    response = test_client.get('/admin_contact/alldata', headers=auth_header)
    assert response.status_code in [200, 404]
    data = response.json
    if response.status_code == 200:
        assert data['message'] == 'Admin Contact found Successfully'
        assert 'data' in data
    elif response.status_code == 404:
        assert data['message'] == 'No Admin Contacte found'
def test_get_admin_contact_by_id(test_client, auth_header):
    response = test_client.get(f'/admin_contact/edit/{auth_header["admin_id"]}', headers=auth_header)
    
    assert response.status_code == 200
    data = response.json
    assert data['message'] == 'Admin Contact found Successfully'
    
