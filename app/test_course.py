import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.log import *
from app.models.adminuser import CourseMaster
from app.models.student import StudentLogin
import time
import random
from faker import Faker
faker=Faker()
@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
              # Seed once for the module
        yield testing_client
        with app.app_context():
            cleanup_seed_data()  # Cleanup after all tests
            db.session.remove()



@pytest.fixture
def auth_header(test_client):
    # You can seed user data here if needed for login
    unique_email = f"{faker.unique.email().split('@')[0]}_{random.randint(1000, 9999)}@example.com"

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
    global seed_ids
    seed_ids = seed_data(student_id)  # Extracting student ID
    yield {'Authorization': access_token, 'student_id': student_id}
    cleanup_seed_data()

    # Fetch the user to delete based on the unique email
    user_to_delete = StudentLogin.query.filter_by(userid=unique_email).first()
    if user_to_delete:
        # First, delete any logs related to the user from LoginLog
        db.session.query(LoginLog).filter_by(student_id=user_to_delete.student_id).delete()

        # Delete any addresses related to the user from tbl_student_address
        

        # Delete related subject preferences before deleting the student login
        

        # Now delete the student login itself
        db.session.delete(user_to_delete)

        # Commit the changes to reflect the deletions
        db.session.commit()

def seed_data(student_id):
    student_login = StudentLogin.query.filter_by(student_id=student_id).first()
    if not student_login:
        raise ValueError("Admin login with userid 'admin123' not found")

    student_id = student_login.student_id
    course = CourseMaster(course_name=faker.word(), is_active=1, is_deleted=False,created_by='Seeded Course 2')
    db.session.add(course)
    db.session.commit()
    
    return {
        'student_login_id': student_id,
        'course_master_id': course.course_id,
    }
def cleanup_seed_data():
    # Clean up the data after the test
    class_master = CourseMaster.query.filter_by(course_id=seed_ids['course_master_id']).first()
    if class_master:
        db.session.delete(class_master)
        db.session.commit()
    CourseMaster.query.filter_by(course_id=seed_ids['course_master_id']).delete()
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
def test_add_course_missing_course_name(test_client, auth_header):
    response = test_client.post('/course/add', json={}, headers=auth_header)
    
    assert response.is_json
    assert response.json['message'] == 'Please Provide Course name'

def test_edit_course_missing_course_name(test_client, auth_header):
    response = test_client.put(f'/course/edit/{seed_ids['course_master_id']}', json={}, headers=auth_header)
    
    assert response.is_json
    assert response.json['message'] == 'Please provide course name'






def test_course_edit_invalid(test_client, auth_header):
      # Using seeded course_id
    new_class_name = 'Unique Class Name'
    unique_suffix = str(int(time.time())) 
    new_course_name = f"{new_class_name}_{unique_suffix}"
    response = test_client.put('/course/edit/888856', headers=auth_header, json={
        "course_name": new_course_name
    })
   
    assert 'Course not found' in response.json['message']

def test_course_get_invalid(test_client, auth_header):
      # Using seeded course_id
    response = test_client.get('/course/edit/8888569', headers=auth_header)
    
    assert 'Course not found' in response.json['message']

def test_course_delete_invalid(test_client, auth_header):
    
    response = test_client.delete('/coursedelete/88856', headers=auth_header)
    assert 'course not found' in response.json['message']

def test_course_activate_invalid(test_client, auth_header):
     # Using seeded course_id
    response = test_client.put('/course/activate/888856', headers=auth_header)
    
    assert 'Course not found' in response.json['message']

def test_course_deactivate_invalid(test_client, auth_header):
  
    response = test_client.put('/course/deactivate/888856', headers=auth_header)
    
    assert 'Course not found' in response.json['message']