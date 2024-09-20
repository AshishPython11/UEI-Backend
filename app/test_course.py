import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.adminuser import CourseMaster
from app.models.student import StudentLogin
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
    student_login = StudentLogin.query.filter_by(userid='1').first()
    if not student_login:
        raise ValueError("Admin login with userid 'admin123' not found")

    student_id = student_login.student_id
    course = CourseMaster(course_name="final", is_active=1, is_deleted=False,created_by='Seeded Course 2')
    db.session.add(course)
    db.session.commit()
    
    return {
        'student_login_id': student_id,
        'course_master_id': course.course_id,
    }
def cleanup_seed_data():
    # Clean up the data after the test
    class_master = CourseMaster.query.filter_by(course_name='final').first()
    if class_master:
        db.session.delete(class_master)
        db.session.commit()
    CourseMaster.query.filter_by(is_deleted=True).delete()
    db.session.commit()


def test_course_list(test_client, auth_header):
    response = test_client.get('/course/list', headers=auth_header)
    assert response.status_code == 200
    

def test_course_add(test_client, auth_header):
    base_class_name = 'Unique Class Name'
    unique_suffix = str(int(time.time())) 
    unique_class_name = f"{base_class_name}_{unique_suffix}"  # Generate a unique course name
    response = test_client.post('/course/add', headers=auth_header, json={
        "course_name": unique_class_name
    })
    assert response.status_code == 200
    assert 'Course created successfully' in response.json['message']

    # Cleanup: Delete the course added during this test
    CourseMaster.query.filter_by(course_name=unique_class_name).delete()
    db.session.commit()

def test_course_edit(test_client, auth_header):
      # Using seeded course_id
    new_class_name = 'Unique Class Name'
    unique_suffix = str(int(time.time())) 
    new_course_name = f"{new_class_name}_{unique_suffix}"
    response = test_client.put(f'/course/edit/{seed_ids['course_master_id']}', headers=auth_header, json={
        "course_name": new_course_name
    })
    assert response.status_code == 200
    assert 'Course updated successfully' in response.json['message']

def test_course_get(test_client, auth_header):
      # Using seeded course_id
    response = test_client.get(f'/course/edit/{seed_ids['course_master_id']}', headers=auth_header)
    assert response.status_code == 200
    assert 'Course found Successfully' in response.json['message']

def test_course_delete(test_client, auth_header):
    course_id = seed_ids['course_master_id']
    response = test_client.delete(f'/coursedelete/{course_id}', headers=auth_header)
    assert response.status_code == 200

def test_course_activate(test_client, auth_header):
     # Using seeded course_id
    response = test_client.put(f'/course/activate/{seed_ids['course_master_id']}', headers=auth_header)
    assert response.status_code == 200
    assert 'Course activated successfully' in response.json['message']

def test_course_deactivate(test_client, auth_header):
  
    response = test_client.put(f'/course/deactivate/{seed_ids['course_master_id']}', headers=auth_header)
    assert response.status_code == 200
    assert 'Course deactivated successfully' in response.json['message']
