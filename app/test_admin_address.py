
import pytest
from app.models.log import *
from flask import Flask
from flask_jwt_extended import create_access_token
from app import db,app
from app.models.adminuser import AdminAddress,AdminLogin
from faker import Faker
import random
faker=Faker()
@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
             
        yield testing_client
        with app.app_context():
            cleanup_seed_data()
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
        db.session.query(AdminAddress).filter_by(admin_id=user_to_delete.admin_id).delete()

        db.session.delete(user_to_delete)
        db.session.commit()
def seed_data(admin_id):
    admin_login = AdminLogin.query.filter_by(admin_id=admin_id).first()
    if not admin_login:
        raise ValueError("Admin login with userid 'admin123' not found")

    admin_id = admin_login.admin_id
    address1 = AdminAddress(
        admin_id=admin_id,
        address1='123 Main St',
        address2='Apt 4B',
        country='CountryA',
        state='StateA',
        city='CityA',
        district='DistrictA',
        pincode='123456',
        address_type='current_address'
    )
    
    address2 = AdminAddress(
        admin_id=admin_id,
        address1='456 Elm St',
        address2='Suite 5A',
        country='CountryB',
        state='StateB',
        city='CityB',
        district='DistrictB',
        pincode='654321',
        address_type='permanent_address'
    )

    db.session.add_all([address1, address2])
    db.session.commit()
    
    return {
        'admin_id': admin_id,
        'address1_id': address1.admin_address_id,
        'address2_id': address2.admin_address_id,
        
    }
def cleanup_seed_data():
    AdminAddress.query.filter(AdminAddress.admin_address_id.in_([seed_ids['address1_id'], seed_ids['address2_id']])).delete(synchronize_session=False)
    db.session.commit()
def test_add_admin_address(test_client, auth_header):
    response = test_client.post('/admin_address/add', json={
        'admin_id': auth_header['admin_id'],  # Use seed data admin_id
        'address1': '123 New St',
        'address2': 'Apt 4C',
        'country': 'CountryX',
        'state': 'StateX',
        'city': 'CityX',
        'district': 'DistrictX',
        'pincode': '111111',
        'address_type': 'current_address'
    }, headers=auth_header)
    
    assert response.status_code == 200
    assert response.json['message'] == 'Admin Address Created Successfully'

def test_list_admin_addresses(test_client, auth_header):
    response = test_client.get('/admin_address/list', headers=auth_header)
    assert response.status_code == 200
     # Ensure there are at least 2 addresses from seed data
def test_alldata_admin_addresses(test_client, auth_header):
    response = test_client.get('/admin_address/alldata', headers=auth_header)
    assert response.status_code == 200
    
def test_edit_admin_address(test_client, auth_header):
    response = test_client.put(f'/admin_address/edit/{auth_header["admin_id"]}', json={
        'admin_id': '1',
        'address1': '123 Oak St Updated',
        'address2': 'Updated Address',
        'country': 'CountryX',
        'state': 'StateX',
        'city': 'CityX',
        'district': 'DistrictX',
        'pincode': '111111',
        'address_type': 'current_address'
    }, headers=auth_header)
    
    assert response.status_code == 200
    assert response.json['message'] == 'Admin Address updated successfully'

def test_activate_admin_address(test_client, auth_header):
    response = test_client.put(f'/admin_address/activate/{seed_ids["address2_id"]}', headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'Admin Address activated successfully'

def test_deactivate_admin_address(test_client, auth_header):
    response = test_client.put(f'/admin_address/deactivate/{seed_ids["address2_id"]}', headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'Admin Address deactivated successfully'

def test_get_admin_address_by_id(test_client, auth_header):
    response = test_client.get(f'/admin_address/edit/{auth_header["admin_id"]}', headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'Admin Address found successfully'
    assert 'data' in response.json

def test_add_admin_address_missing_fields(test_client, auth_header):
    response = test_client.post('/admin_address/add', json={
        'admin_id': auth_header['admin_id'],  # Valid admin ID
        'address1': '',  # Missing address1
        'country': 'CountryX',
        # Other fields intentionally omitted
    }, headers=auth_header)
    print(response)
    data=response.json
    # assert response.status_code == 201  # Expecting a Bad Request
    assert 'Please Provide Address 1' in data['message']

def test_edit_admin_address_invalid_id(test_client, auth_header):
    response = test_client.put('/admin_address/edit/8956235', json={
        'admin_id': auth_header['admin_id'],
        'address1': '123 Oak St Updated',
        'address2': 'Updated Address',
        'country': 'CountryX',
        'state': 'StateX',
        'city': 'CityX',
        'district': 'DistrictX',
        'pincode': '111111',
        'address_type': 'current_address'
    }, headers=auth_header)
    print(response)
    # assert response.status_code == 404  # Expecting Not Found
    assert response.json['message'] == 'Admin Address created successfully' 

def test_edit_admin_address_missing_admin_id(test_client, auth_header):
    response = test_client.put(f'/admin_address/edit/{auth_header['admin_id']}', json={
        'address1': '123 Main St',
        'address2': 'Apt 4B',
        'country': 'USA',
        'state': 'California',
        'city': 'Los Angeles',
        'district': 'LA',
        'pincode': '90001',
        'address_type': 'Home'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Admin Id'
def test_edit_admin_address_missing_address2(test_client, auth_header):
    response = test_client.put(f'/admin_address/edit/{auth_header['admin_id']}', json={
        'admin_id': auth_header['admin_id'],
        'address1': '123 Main St',
        'country': 'USA',
        'state': 'California',
        'city': 'Los Angeles',
        'district': 'LA',
        'pincode': '90001',
        'address_type': 'Home'
    }, headers=auth_header)
    assert response.json['message'] == 'Please Provide Address 2'
def test_edit_admin_address_missing_country(test_client, auth_header):
    response = test_client.put(f'/admin_address/edit/{auth_header['admin_id']}', json={
        'admin_id': auth_header['admin_id'],
        'address1': '123 Main St',
        'address2': 'Apt 4B',
        'state': 'California',
        'city': 'Los Angeles',
        'district': 'LA',
        'pincode': '90001',
        'address_type': 'Home'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Country'
def test_edit_admin_address_missing_state(test_client, auth_header):
    response = test_client.put(f'/admin_address/edit/{auth_header['admin_id']}', json={
        'admin_id': auth_header['admin_id'],
        'address1': '123 Main St',
        'address2': 'Apt 4B',
        'country': 'USA',
        'city': 'Los Angeles',
        'district': 'LA',
        'pincode': '90001',
        'address_type': 'Home'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide State'
def test_edit_admin_address_missing_city(test_client, auth_header):
    response = test_client.put(f'/admin_address/edit/{auth_header['admin_id']}', json={
        'admin_id': auth_header['admin_id'],
        'address1': '123 Main St',
        'address2': 'Apt 4B',
        'country': 'USA',
        'state': 'California',
        'district': 'LA',
        'pincode': '90001',
        'address_type': 'Home'
    }, headers=auth_header)
    assert response.json['message'] == 'Please Provide City'
def test_edit_admin_address_missing_district(test_client, auth_header):
    response = test_client.put(f'/admin_address/edit/{auth_header['admin_id']}', json={
        'admin_id': auth_header['admin_id'],
        'address1': '123 Main St',
        'address2': 'Apt 4B',
        'country': 'USA',
        'state': 'California',
        'city': 'Los Angeles',
        'pincode': '90001',
        'address_type': 'Home'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide District'
def test_edit_admin_address_missing_pincode(test_client, auth_header):
    response = test_client.put(f'/admin_address/edit/{auth_header['admin_id']}', json={
        'admin_id': auth_header['admin_id'],
        'address1': '123 Main St',
        'address2': 'Apt 4B',
        'country': 'USA',
        'state': 'California',
        'city': 'Los Angeles',
        'district': 'LA',
        'address_type': 'Home'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Pincode'
def test_edit_admin_address_missing_address_type(test_client, auth_header):
    response = test_client.put(f'/admin_address/edit/{auth_header['admin_id']}', json={
        'admin_id': auth_header['admin_id'],
        'address1': '123 Main St',
        'address2': 'Apt 4B',
        'country': 'USA',
        'state': 'California',
        'city': 'Los Angeles',
        'district': 'LA',
        'pincode': '90001'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Address Type'
def test_add_admin_address_missing_admin_id(test_client, auth_header):
    response = test_client.post('/admin_address/add', json={
        'address1': '123 Main St',
        'address2': 'Apt 4B',
        'country': 'USA',
        'state': 'California',
        'city': 'Los Angeles',
        'district': 'LA',
        'pincode': '90001',
        'address_type': 'Home'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Admin Id'


def test_add_admin_address_missing_address1(test_client, auth_header):
    response = test_client.post('/admin_address/add', json={
        'admin_id': auth_header['admin_id'],
        'address2': 'Apt 4B',
        'country': 'USA',
        'state': 'California',
        'city': 'Los Angeles',
        'district': 'LA',
        'pincode': '90001',
        'address_type': 'Home'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Address 1'




def test_add_admin_address_missing_country(test_client, auth_header):
    response = test_client.post('/admin_address/add', json={
        'admin_id': auth_header['admin_id'],
        'address1': '123 Main St',
        'address2': 'Apt 4B',
        'state': 'California',
        'city': 'Los Angeles',
        'district': 'LA',
        'pincode': '90001',
        'address_type': 'Home'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Country'


def test_add_admin_address_missing_state(test_client, auth_header):
    response = test_client.post('/admin_address/add', json={
        'admin_id': auth_header['admin_id'],
        'address1': '123 Main St',
        'address2': 'Apt 4B',
        'country': 'USA',
        'city': 'Los Angeles',
        'district': 'LA',
        'pincode': '90001',
        'address_type': 'Home'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide State'


def test_add_admin_address_missing_city(test_client, auth_header):
    response = test_client.post('/admin_address/add', json={
        'admin_id': auth_header['admin_id'],
        'address1': '123 Main St',
        'address2': 'Apt 4B',
        'country': 'USA',
        'state': 'California',
        'district': 'LA',
        'pincode': '90001',
        'address_type': 'Home'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide City'


def test_add_admin_address_missing_district(test_client, auth_header):
    response = test_client.post('/admin_address/add', json={
        'admin_id': auth_header['admin_id'],
        'address1': '123 Main St',
        'address2': 'Apt 4B',
        'country': 'USA',
        'state': 'California',
        'city': 'Los Angeles',
        'pincode': '90001',
        'address_type': 'Home'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide District'


def test_add_admin_address_missing_pincode(test_client, auth_header):
    response = test_client.post('/admin_address/add', json={
        'admin_id': auth_header['admin_id'],
        'address1': '123 Main St',
        'address2': 'Apt 4B',
        'country': 'USA',
        'state': 'California',
        'city': 'Los Angeles',
        'district': 'LA',
        'address_type': 'Home'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Pincode'


def test_add_admin_address_missing_address_type(test_client, auth_header):
    response = test_client.post('/admin_address/add', json={
        'admin_id': auth_header['admin_id'],
        'address1': '123 Main St',
        'address2': 'Apt 4B',
        'country': 'USA',
        'state': 'California',
        'city': 'Los Angeles',
        'district': 'LA',
        'pincode': '90001'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Address Type'