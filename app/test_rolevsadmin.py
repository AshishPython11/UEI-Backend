import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.role import RoleVsAdminMaster, ManageRole,RoleMasterData
from app.models.adminuser import AdminBasicInformation,AdminLogin,DepartmentMaster
from faker import Faker
from app.models.student import StudentLogin
from app.models.log import LoginLog
from datetime import datetime
faker = Faker()
import random
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
    unique_email = f"{faker.unique.email().split('@')[0]}_{random.randint(1000, 9999)}@example.com"

    # First, sign up a new user
    signup_response = test_client.post('/auth/signup', json={
        "userid": unique_email,  # Unique email for signup
        "password": "password",  # Assuming a fixed password
        "user_type": "admin"
    })

    assert signup_response.status_code == 200, f"Signup failed with status code {signup_response.status_code}"
    assert signup_response.json['status'] == 200, f"Signup error: {signup_response.json['message']}"

    # Now, attempt to log in using the unique email directly
    login_response = test_client.post('/auth/login', json={
        "userid": unique_email,  # Use the same unique email
        "password": "password",  # Same password
        "user_type": "admin"
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
    admin_id = data['data']['id']  # Extracting student ID
    yield {'Authorization': access_token, 'admin_id': admin_id}
    user_to_delete = StudentLogin.query.filter_by(userid=unique_email).first()
    if user_to_delete:
        db.session.query(LoginLog).filter_by(admin_id=user_to_delete.admin_id).delete()
        db.session.delete(user_to_delete)
        db.session.commit()
def seed_data():
    # Create a sample admin basic information entry
    department_name = faker.unique.company()  # Generate a unique department name
    department = DepartmentMaster(department_name=department_name)
    db.session.add(department)
    db.session.commit()

    # Fetch the integer ID of the newly created department
    department_id = department.department_id

    # Create a sample admin basic information entry
    admin_registration_no = f"REG-{faker.unique.random_int(min=10000, max=99999)}"  # Unique registration number
    admin_basic_info = AdminBasicInformation(
        admin_registration_no=admin_registration_no,
        department_id=department_id,  # Use the newly created department ID
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        gender=faker.random_element(elements=('Male', 'Female', 'Other')),
        dob=faker.date_of_birth(minimum_age=18, maximum_age=65),  # Adjust age range as needed
        father_name=faker.name(),
        mother_name=faker.name(),
        guardian_name=faker.name(),
        is_kyc_verified=faker.boolean(),
        system_datetime=datetime.now(),
        pic_path=faker.image_url(),
        created_by=faker.name(),
        updated_by=faker.name(),
        last_modified_datetime=datetime.now(),
        is_active=1
    )

    db.session.add(admin_basic_info)
    db.session.commit()

    # Fetch the integer ID of the newly created admin basic info
    admin_id = admin_basic_info.admin_id  # Assuming this is the primary key

    # Generate a unique role name using Faker
    role_name = faker.unique.job()  # Using job title as a unique role name

    # Create a role and retrieve its integer ID
    role_master = RoleMasterData(role_name=role_name)
    db.session.add(role_master)
    db.session.commit()

    # Fetch the integer ID of the newly created role
    role_master_id = role_master.role_master_id

    # Create a RoleVsAdminMaster instance with integer IDs
    rolevsadmin = RoleVsAdminMaster(
        admin_id=admin_id,
        role_master_id=role_master_id,
        is_active=1,
        is_deleted=False,
        created_by=admin_basic_info.first_name  # Use admin's first name or appropriate field
    )

    db.session.add(rolevsadmin)
    db.session.commit()

    return {
        'admin_id': admin_id,
        'role_master_id': role_master_id,
        'role_admin_master_id': rolevsadmin.role_admin_master_id
    }

# def seed_data():
#     admin_login = AdminLogin.query.filter_by(userid='admin123').first()
#     if not admin_login:
#         raise ValueError("Admin login with userid 'admin123' not found")
#     admin_id = admin_login.admin_id
#     role_name = faker.unique.job()  # Using job title as a unique role name

#     # Create a role and retrieve its integer ID
#     role_master = RoleMasterData(role_name=role_name)
#     db.session.add(role_master)
#     db.session.commit()

#     # Fetch the integer ID of the newly created role
#     role_master_id = role_master.role_master_id

#     # Create a RoleVsAdminMaster instance with integer IDs
#     rolevsadmin = RoleVsAdminMaster(
#         admin_id=admin_id,
#         role_master_id=role_master_id,
#         is_active=1,
#         is_deleted=False,
#         created_by=admin_login.userid
#     )
    
#     db.session.add(rolevsadmin)
#     db.session.commit()

#     return {
#         'admin_id': admin_id,
#         'role_master_id': role_master_id,
#         'role_admin_master_id': rolevsadmin.role_admin_master_id
#     }

def cleanup_seed_data():
    RoleVsAdminMaster.query.filter_by(role_admin_master_id=seed_ids['role_admin_master_id']).delete()
    db.session.commit()

# Test: List RolevsAdmin
def test_list_rolevsadmin(test_client, auth_header):
    response = test_client.get('/rolevsadmin/list', headers=auth_header)
    assert response.status_code == 200
    
    

# Test: Add RolevsAdmin
def test_add_rolevsadmin(test_client, auth_header):
    payload = {
        "admin_id": auth_header['admin_id'],
        "role_master_id": seed_ids['role_master_id']
    }
    
    response = test_client.post('/rolevsadmin/add', json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    # assert 'RolevsUser Data created successfully' in data['message']

# Test: Edit RolevsAdmin
def test_edit_rolevsadmin(test_client, auth_header):
    payload = {
        "admin_id": auth_header['admin_id'],
        "role_master_id": seed_ids['role_master_id']
    }
    response = test_client.put(f'/rolevsadmin/edit/{seed_ids["role_admin_master_id"]}', json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    # assert 'RolevsUser Data updated successfully' in data['message']

# Test: Get RolevsAdmin by ID
def test_get_rolevsadmin(test_client, auth_header):
    response = test_client.get(f'/rolevsadmin/edit/{seed_ids["role_admin_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'RolevsUser Data found Successfully' in data['message']

# Test: Activate RolevsAdmin
def test_activate_rolevsadmin(test_client, auth_header):
    response = test_client.put(f'/rolevsadmin/activate/{seed_ids["role_admin_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'RolevsUser Data activated successfully' in data['message']

# Test: Deactivate RolevsAdmin
def test_deactivate_rolevsadmin(test_client, auth_header):
    response = test_client.put(f'/rolevsadmin/deactivate/{seed_ids["role_admin_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'RolevsUser Data deactivated successfully' in data['message']

# Test: Delete RolevsAdmin
def test_delete_rolevsadmin(test_client, auth_header):
    response = test_client.delete(f'/rolevsadmindelete/{seed_ids["role_admin_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'RolevsUser deleted successfully' in data['message']
def test_add_role_vs_admin_missing_admin_id(test_client, auth_header):
    response = test_client.post('/rolevsadmin/add', json={'role_master_id': str(faker.random_int(min=1,max=100)),'admin_id':''}, headers=auth_header)
    
    assert response.json['message'] == 'Please Provide Admin Id'

def test_add_role_vs_admin_missing_role_master_id(test_client, auth_header):
    response = test_client.post('/rolevsadmin/add', json={'admin_id':str(faker.random_int(min=1,max=100)), 'role_master_id': ''}, headers=auth_header)
    
    assert response.json['message'] == 'Please Role Master Id'

def test_edit_role_vs_admin_missing_admin_id(test_client, auth_header):
    response = test_client.put(f'/rolevsadmin/edit/{seed_ids["role_admin_master_id"]}', json={'role_master_id': str(faker.random_int(min=1,max=100)),'admin_id':''}, headers=auth_header)
    
    assert response.json['message'] == 'Please Provide Admin Id'

def test_edit_role_vs_admin_missing_role_master_id(test_client, auth_header):
    response = test_client.put(f'/rolevsadmin/edit/{seed_ids["role_admin_master_id"]}', json={'admin_id':str(faker.random_int(min=1,max=100)), 'role_master_id': ''}, headers=auth_header)
    
    assert response.json['message'] == 'Please Role Master Id'


def test_edit_rolevsadmin_invalid(test_client, auth_header):
    payload = {
        "admin_id": auth_header['admin_id'],
        "role_master_id": seed_ids['role_master_id']
    }
    response = test_client.put('/rolevsadmin/edit/8885695', json=payload, headers=auth_header)
 
    data = response.get_json()
    assert 'RolevsUser Data not found' in data['message']

# Test: Get RolevsAdmin by ID
def test_get_rolevsadmin_invalid(test_client, auth_header):
    response = test_client.get('/rolevsadmin/edit/8885695', headers=auth_header)
 
    data = response.get_json()
    assert 'RolevsUser Data not found' in data['message']

# Test: Activate RolevsAdmin
def test_activate_rolevsadmin_invalid(test_client, auth_header):
    response = test_client.put('/rolevsadmin/activate/8856958', headers=auth_header)
    
    data = response.get_json()
    assert 'RolevsUser Data not found' in data['message']

# Test: Deactivate RolevsAdmin
def test_deactivate_rolevsadmin_invalid(test_client, auth_header):
    response = test_client.put('/rolevsadmin/deactivate/8856959', headers=auth_header)

    data = response.get_json()
    assert 'RolevsUser Data not found' in data['message']

# Test: Delete RolevsAdmin
def test_delete_rolevsadmin_invalid(test_client, auth_header):
    response = test_client.delete('/rolevsadmindelete/8859659', headers=auth_header)

    data = response.get_json()
    assert 'RolevsUser not found' in data['message']