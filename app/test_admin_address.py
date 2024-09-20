
import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.adminuser import AdminAddress,AdminLogin

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