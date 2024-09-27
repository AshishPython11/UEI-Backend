import pytest
from app import app, db
from app.models.log import *
from app.models.adminuser import DepartmentMaster
import time
from faker import Faker
faker=Faker()
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
    # You can seed user data here if needed for login
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
    student_id = data['data']['id'] 
      # Extracting student ID
    yield {'Authorization': access_token, 'student_id': student_id}
    


def seed_data():
    department = DepartmentMaster(department_name=faker.word(), is_active=1, is_deleted=False, created_by='1')
    db.session.add(department)
    db.session.commit()
    return {'department_id': department.department_id}

def cleanup_seed_data():
    DepartmentMaster.query.filter_by(department_id=seed_ids['department_id']).delete()
    db.session.commit()

# Test cases

def test_department_add(test_client, auth_header):
    base_class_name = 'Unique Class Name'
    unique_suffix = str(int(time.time())) 
    unique_class_name = f"{base_class_name}_{unique_suffix}"
    response = test_client.post('/department/add', headers=auth_header, json={
        "department_name": unique_class_name
    })
    assert response.status_code == 200
    assert 'Department created successfully' in response.json['message']
    

def test_department_list(test_client, auth_header):
    response = test_client.get('/department/list', headers=auth_header)
    assert response.status_code == 200
    

def test_department_edit(test_client, auth_header):
    updated_name = 'Unique Class Name'
    unique_suffix = str(int(time.time())) 
    updated_edit_name = f"{updated_name}_{unique_suffix}"
    department_id = seed_ids['department_id']
    response = test_client.put(f'/department/edit/{department_id}', headers=auth_header, json={
        "department_name": updated_edit_name
    })
    assert response.status_code == 200
    assert 'Department updated successfully' in response.json['message']

def test_department_get(test_client, auth_header):
    department_id = seed_ids['department_id']
    response = test_client.get(f'/department/edit/{department_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Department found Successfully' in response.json['message']

def test_department_delete(test_client, auth_header):
    department_id = seed_ids['department_id']
    response = test_client.delete(f'/departmentdelete/{department_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Department deleted successfully' in response.json['message']

def test_department_activate(test_client, auth_header):
    department_id = seed_ids['department_id']
    response = test_client.put(f'/department/activate/{department_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Department activated successfully' in response.json['message']

def test_department_deactivate(test_client, auth_header):
    department_id = seed_ids['department_id']
    response = test_client.put(f'/department/deactivate/{department_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Department deactivated successfully' in response.json['message']
def test_add_department_missing_department_name(test_client, auth_header):
    response = test_client.post('/department/add', json={}, headers=auth_header)
    
    assert response.is_json
    assert response.json['message'] == 'Please Provide Department name'



def test_edit_department_missing_department_name(test_client, auth_header):
    response = test_client.put(f'/department/edit/{seed_ids['department_id']}', json={}, headers=auth_header)
    
    assert response.is_json
    assert response.json['message'] == 'Please provide department name'