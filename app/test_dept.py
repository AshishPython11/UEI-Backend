import pytest
from app import app, db
from app.models.adminuser import DepartmentMaster
import time
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
    response = test_client.post('/auth/login', json={
        "userid": "1",
        "password": "111",
        "user_type": "student"
    })

    print("Login response status code:", response.status_code)
    print("Login response data:", response.json)
    
    # Ensure login was successful
    assert response.status_code == 200, f"Login failed with status code {response.status_code}"
    
    # Extract the token from the login response
    data = response.json
    if 'token' not in data:
        pytest.fail(f"Login response missing 'token': {data}")
    
    access_token = data['token']
    student_id = data['data']['id']  # Extracting student ID
    return {'Authorization': access_token,'student_id':student_id}


def seed_data():
    department = DepartmentMaster(department_name="finalllll Department", is_active=1, is_deleted=False, created_by='1')
    db.session.add(department)
    db.session.commit()
    return {'department_id': department.department_id}

def cleanup_seed_data():
    DepartmentMaster.query.filter_by(is_deleted=True).delete()
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
    DepartmentMaster.query.filter_by(department_name=unique_class_name).delete()
    db.session.commit()

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
