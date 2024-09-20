
    
import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from datetime import datetime
from app.models.adminuser import AdminBasicInformation,DepartmentMaster,AdminLogin

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
    department = DepartmentMaster(
        department_name="Test Department",
        is_active=1,
        created_by="Seeder",
        updated_by="Seeder"
    )
    db.session.add(department)
    db.session.commit()
    
    # Create seed data for AdminBasicInformation
    admin_info = AdminBasicInformation(
        admin_login_id=1,
        admin_registration_no="REG123",
        department_id=department.department_id,
        first_name="John",
        last_name="Doe",
        gender="Male",
        dob=datetime(1990, 1, 1),
        father_name="Father Doe",
        mother_name="Mother Doe",
        guardian_name="Guardian Doe",
        pic_path="/path/to/pic",
        is_kyc_verified=True,
        system_datetime=datetime.now(),
        created_by="Seeder",
        updated_by="Seeder",
        last_modified_datetime=datetime.now()
    )
    
    db.session.add(admin_info)
    db.session.commit()
    
    # Return the seeded data for use in the tests
    return {
        "admin_basic_info": admin_info,
        "department": department
    }
def test_get_all_admin_basic_info(test_client, auth_header):
    response = test_client.get('/admin_basicinfo/alldata', headers=auth_header)
    
    assert response.status_code in [200, 404]
    data = response.json
    if response.status_code == 200:
        assert data['message'] == 'Admin Basic Informations found Successfully'
        assert 'data' in data
    elif response.status_code == 404:
        assert data['message'] == 'No Admin Basic Informations found'
def test_list_admin_basic_info(test_client, auth_header):
    response = test_client.get('/admin_basicinfo/list', headers=auth_header)
    
    assert response.status_code == 200
    assert 'data' in response.json
    assert isinstance(response.json['data'], list)
def test_get_admin_basic_info_by_id(test_client, auth_header):
    response = test_client.get(f'/admin_basicinfo/edit/{auth_header["admin_id"]}', headers=auth_header)
    
    assert response.status_code == 200
    data = response.json
    assert data['message'] == 'Admin Basic Information found Successfully'


def test_add_admin_basic_info(test_client, auth_header):
    response = test_client.post('/admin_basicinfo/add', json={
        'department_id': 1,  # Ensure this ID exists in your seed data
        'first_name': 'John',
        'last_name': 'Doe',
        'gender': 'Male',
        'dob': '1990-01-01',
        'father_name': 'Father Name',
        'mother_name': 'Mother Name',
        'guardian_name': 'Guardian Name',
        'is_kyc_verified': 1,
        'pic_path': '/path/to/pic',
        'admin_login_id': auth_header['admin_id']  # Use admin_id from seed data
    }, headers=auth_header)
    
    assert response.status_code == 200
    assert response.json['message'] == 'Admin Basic Information created successfully'
def test_edit_admin_basic_info(test_client, auth_header):
    response = test_client.put(f'/admin_basicinfo/edit/{auth_header["admin_id"]}', json={
        'department_id': 2,  # Ensure this ID exists in your seed data
        'first_name': 'Jane',
        'last_name': 'Doe',
        'gender': 'Female',
        'dob': '1992-05-15',
        'father_name': 'Updated Father Name',
        'mother_name': 'Updated Mother Name',
        'guardian_name': 'Updated Guardian Name',
        'is_kyc_verified': 0,
        'pic_path': '/updated/path/to/pic',
        'admin_login_id': auth_header['admin_id']  # Use admin_id from seed data
    }, headers=auth_header)
    
    assert response.status_code == 200
    assert response.json['message'] == 'Admin Basic Information updated successfully'

def test_activate_admin_basic_info(test_client, auth_header):
    response = test_client.put(f'/admin_basicinfo/activate/{auth_header["admin_id"]}', headers=auth_header)
    
    assert response.status_code == 200
    assert response.json['message'] == 'Admin Basic Information activated successfully'
def test_deactivate_admin_basic_info(test_client, auth_header):
    response = test_client.put(f'/admin_basicinfo/deactivate/{auth_header["admin_id"]}', headers=auth_header)
    
    assert response.status_code == 200
    assert response.json['message'] == 'Admin Basic Information deactivated successfully'
def test_get_profile_success(test_client, auth_header):
    # Assume seed_data provides a valid admin ID
    
    
    response = test_client.get(f'/admin_basicinfo/getProfile/{auth_header["admin_id"]}', headers=auth_header)
    
    assert response.status_code == 200
    data = response.json
    assert data['message'] == 'Admin found Successfully'
    assert data['status'] == 200
    assert 'data' in data
    
    # Additional assertions to verify data integrity
    assert 'address' in data['data']
    assert 'admin_description' in data['data']
    assert 'profession' in data['data']
    assert 'language_known' in data['data']
    assert 'contact' in data['data']
    assert 'basic_info' in data['data']
    assert 'userid' in data['data']
