
import pytest
from app.models.log import *
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from faker import Faker
faker=Faker()
from app.models.adminuser import AdminContact,AdminLogin
import random
@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
              
        yield testing_client
        with app.app_context():
            AdminContact.query.filter_by(admin_contact_id=seed_ids['admin_contact_id']).delete()
            db.session.commit() 
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
    user_to_delete = AdminLogin.query.filter_by(userid=unique_email).first()
    if user_to_delete:
        db.session.query(LoginLog).filter_by(admin_id=user_to_delete.admin_id).delete()
        db.session.query(AdminContact).filter_by(admin_id=user_to_delete.admin_id).delete()

        db.session.delete(user_to_delete)
        db.session.commit()
def seed_data(admin_id):
    admin_login = AdminLogin.query.filter_by(admin_id=admin_id).first()
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
    
def test_add_admin_contact_missing_mobile_no_call(test_client, auth_header):
    response = test_client.post('/admin_contact/add', json={
        'admin_id': auth_header['admin_id'],
        'mobile_isd_call': '+91',
        'mobile_isd_watsapp': '+91',
        'mobile_no_watsapp': '9876543211',
        'email_id': 'admin_new@example.com'
    }, headers=auth_header)

    
    assert response.json['message'] == 'Please Provide Mobile No'

def test_add_admin_contact_missing_email_id(test_client, auth_header):
    response = test_client.post('/admin_contact/add', json={
        'admin_id': auth_header['admin_id'],
        'mobile_isd_call': '+91',
        'mobile_no_call': '9876543211',
        'mobile_isd_watsapp': '+91',
        'mobile_no_watsapp': '9876543211'
    }, headers=auth_header)

    
    assert response.json['message'] == 'Please Provide Email Id'
def test_add_admin_contact_missing_mobile_isd_call(test_client, auth_header):
    response = test_client.post('/admin_contact/add', json={
        'admin_id': auth_header['admin_id'],
        'mobile_no_call': '9876543211',
        'mobile_isd_watsapp': '+91',
        'mobile_no_watsapp': '9876543211',
        'email_id': 'admin_new@example.com'
    }, headers=auth_header)

    
    assert response.json['message'] == 'Please Provide Mobile ISD'
def test_add_admin_contact_missing_mobile_isd_watsapp(test_client, auth_header):
    response = test_client.post('/admin_contact/add', json={
        'admin_id': auth_header['admin_id'],
        'mobile_isd_call': '+91',
        'mobile_no_call': '9876543211',
        'mobile_no_watsapp': '9876543211',
        'email_id': 'admin_new@example.com'
    }, headers=auth_header)

    
    assert response.json['message'] == 'Please Provide Whatsapp mobile ISD'
def test_add_admin_contact_missing_admin_id(test_client, auth_header):
    response = test_client.post('/admin_contact/add', json={
        'mobile_isd_call': '+91',
        'mobile_no_call': '9876543211',
        'mobile_isd_watsapp': '+91',
        'mobile_no_watsapp': '9876543211',
        'email_id': 'admin_new@example.com'
    }, headers=auth_header)

    
    assert response.json['message'] == 'Please Provide Admin Id'

def test_edit_admin_contact_missing_mobile_no_call(test_client, auth_header):
    response = test_client.put(f'/admin_contact/edit/{auth_header['admin_id']}', json={
        'admin_id': auth_header['admin_id'],
        'mobile_isd_call': '+91',
        'mobile_isd_watsapp': '+91',
        'mobile_no_watsapp': '9876543211',
        'email_id': 'admin_new@example.com'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Mobile No'


def test_edit_admin_contact_missing_email_id(test_client, auth_header):
    response = test_client.put(f'/admin_contact/edit/{auth_header['admin_id']}', json={
        'admin_id': auth_header['admin_id'],
        'mobile_isd_call': '+91',
        'mobile_no_call': '9876543211',
        'mobile_isd_watsapp': '+91',
        'mobile_no_watsapp': '9876543211'
    }, headers=auth_header)

    assert response.json['message'] == 'Admin Contact updated successfully'


def test_edit_admin_contact_missing_mobile_isd_call(test_client, auth_header):
    response = test_client.put(f'/admin_contact/edit/{auth_header['admin_id']}', json={
        'admin_id': auth_header['admin_id'],
        'mobile_no_call': '9876543211',
        'mobile_isd_watsapp': '+91',
        'mobile_no_watsapp': '9876543211',
        'email_id': 'admin_new@example.com'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Mobile ISD'


def test_edit_admin_contact_missing_mobile_isd_watsapp(test_client, auth_header):
    response = test_client.put(f'/admin_contact/edit/{auth_header['admin_id']}', json={
        'admin_id': auth_header['admin_id'],
        'mobile_no_call': '9876543211',
        'mobile_isd_call': '+91',
        'mobile_no_watsapp': '9876543211',
        'email_id': 'admin_new@example.com'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Whatsapp mobile ISD'


def test_edit_admin_contact_missing_admin_id(test_client, auth_header):
    response = test_client.put(f'/admin_contact/edit/{auth_header['admin_id']}', json={
        'mobile_isd_call': '+91',
        'mobile_no_call': '9876543211',
        'mobile_isd_watsapp': '+91',
        'mobile_no_watsapp': '9876543211',
        'email_id': 'admin_new@example.com'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Admin Id'
# Test case for invalid mobile number format

def test_edit_admin_contact_invalid(test_client, auth_header):
    response = test_client.put('/admin_contact/edit/88856', json={
        'admin_id': auth_header['admin_id'],  # Use admin_id from seed data
        'mobile_isd_call': '+91',
        'mobile_no_call': '9999999999',  # Updated mobile number
        'mobile_isd_watsapp': '+91',
        'mobile_no_watsapp': '9876543210',
        'email_id': 'admin_seeder@example.com'
    }, headers=auth_header)
    
   
    assert response.json['message'] == 'Admin Contact not found'


def test_get_admin_contact_invalid(test_client, auth_header):
    response = test_client.get('/admin_contact/edit/88856', headers=auth_header)
    
   
    assert response.json['message'] == 'Admin Contact not found'
# Test case for activating an admin contact
def test_activate_admin_contact_invalid(test_client, auth_header):
    response = test_client.put('/admin_contact/activate/88568', headers=auth_header)
    
   
    assert response.json['message'] == 'Admin Contact not found'

# Test case for deactivating an admin contact
def test_deactivate_admin_contact_invalid(test_client, auth_header):
    response = test_client.put('/admin_contact/deactivate/88856', headers=auth_header)
    
   
    assert response.json['message'] == 'Admin Contact not found'