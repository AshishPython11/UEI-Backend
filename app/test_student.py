import pytest
from faker import Faker
from app import db,app
from app.models.student import  StudentLogin, Student
from app.models.log import *
import random
from flask_jwt_extended import create_access_token
from datetime import datetime
faker = Faker()
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
        # db.session.query(Contact).filter_by(student_id=user_to_delete.student_id).delete()

        # Delete related subject preferences before deleting the student login
        

        # Now delete the student login itself
        db.session.delete(user_to_delete)

        # Commit the changes to reflect the deletions
        db.session.commit()


def seed_data(student_id):
    student_login = StudentLogin.query.filter_by(student_id=student_id).first()
    if not student_login:
        raise ValueError("Student login with userid '1' not found")

    student_id = student_login.student_id
    print(student_id)
    student = Student(
        
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        gender='Male',
        dob=faker.date_of_birth(),
        father_name=faker.name(),
        mother_name=faker.name(),
        guardian_name=faker.name(),
        student_login_id=student_id,
        is_kyc_verified=1,
        system_datetime=datetime.now(),
        pic_path='path/to/test/image.png',
        last_modified_datetime=datetime.now(),
        student_registration_no=faker.uuid4(),
        created_by=1,
        is_active=1
    )
    db.session.add(student)
    db.session.commit()

    return {
        'student_id': student.student_id,
        'student_login_id': student_login.student_id
    }

def cleanup_seed_data():
    Student.query.filter_by(student_id=seed_ids['student_id']).delete()
    db.session.commit()
def test_student_list(test_client, auth_header):
    response = test_client.get('/student/list', headers=auth_header)
    print(response.json) 
    assert response.status_code == 200
    
    assert isinstance(response.json['data'], list)  # Check if 'data' is a list
    assert response.json['message'] == 'Students found Successfully'

def test_student_add(test_client, auth_header):
    new_student_data = {
        'first_name': faker.first_name(),
        'last_name': faker.last_name(),
        'gender': 'Male',
        'dob': faker.date_of_birth().isoformat(),
        'father_name': faker.name(),
        'mother_name': faker.name(),
        'guardian_name': faker.name(),
        'student_login_id': seed_ids['student_login_id'],
        'is_kyc_verified': 1,
        'pic_path': 'path/to/new_image.png'
    }

    response = test_client.post('/student/add', headers=auth_header, json=new_student_data)
    assert response.status_code == 200
    assert response.json['message'] == 'Student record processed successfully'

def test_store_profile_picture(test_client, auth_header):
    update_data = {
        'student_login_id': seed_ids['student_login_id'],
        'pic_path': 'path/to/updated_image.png'
    }
    
    response = test_client.post('/student/add/store_profile_picture', headers=auth_header, json=update_data)
    assert response.status_code == 200
    assert response.json['message'] == 'Profile picture path stored successfully'
def test_edit_student(test_client, auth_header):
    edit_data = {
        'first_name': faker.first_name(),
        'last_name': faker.last_name(),
        'gender': 'Female',
        'dob': faker.date_of_birth().isoformat(),
        'father_name': faker.name(),
        'mother_name': faker.name(),
        'guardian_name': faker.name(),
        'is_kyc_verified': 1,
        'pic_path': 'path/to/updated_image.png',
        'student_login_id': seed_ids['student_login_id']

    }
    
    response = test_client.put(f'/student/edit/{seed_ids['student_login_id']}', headers=auth_header, json=edit_data)
    assert response.status_code == 200
    assert response.json['message'] == 'Student updated successfully'

def test_get_student_success(test_client, auth_header):
    
    response = test_client.get(f'/student/get/{seed_ids['student_login_id']}', headers=auth_header)
    
    assert response.status_code == 200
def test_get_student_not_found(test_client, auth_header):
    response = test_client.get('/student/get/9999999', headers=auth_header)  # Non-existing ID
    
    # assert response.status_code == 404
    assert response.json['message'] == 'Student not found'

def test_get_profile_success(test_client, auth_header):
    
    response = test_client.get(f'/student/getProfile/{seed_ids['student_login_id']}', headers=auth_header)
    
    assert response.status_code == 200
    assert response.json['status'] == 200
    assert 'prompt' in response.json['data']
    

def test_edit_student(test_client, auth_header):

    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'gender': 'Male',
        'dob': '2000-01-01',
        'father_name': 'Father Name',
        'mother_name': 'Mother Name',
        'guardian_name': 'Guardian Name',
        'is_kyc_verified': True,
        'student_login_id': seed_ids['student_login_id'],
        'pic_path': 'path/to/pic.jpg',
        'aim': 'Engineer',
        'mobile_no_call': '1234567890',
        'email_id': "john@gmail.com",  
    }

    response = test_client.put(f'/student/editstudent/{seed_ids['student_login_id']}', json=data, headers=auth_header)
    assert response.status_code == 200
    



def test_delete_student(test_client, auth_header):
    student_id = seed_ids['student_id']  # Use an existing student ID for testing
    response = test_client.delete(f'/studentdelete/{student_id}', headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'Student deleted successfully'



def test_activate_student(test_client, auth_header):
    student_id = seed_ids['student_id']  # Use an existing student ID for testing
    response = test_client.put(f'/student/activate/{student_id}', headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'Student activated successfully'



def test_deactivate_student(test_client, auth_header):
     # Use an existing student ID for testing
    student_id = seed_ids['student_id']  # Use an existing student ID for testing
    response = test_client.put(f'/student/deactivate/{student_id}', headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'Student deactivated successfully'



def test_profile_completion(test_client, auth_header):
     # Use an existing student ID for testing
    response = test_client.get(f'/student/profile-completion/{seed_ids['student_login_id']}', headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'Student not found'
   


def test_store_profile_picture(test_client, auth_header):
    # Assuming you have a valid student_login_id and a pic_path for testing
    student_login_id = seed_ids['student_login_id']  # Use an existing student login ID for testing
    pic_path = 'path/to/new/profile/pic.jpg'

    data = {
        'student_login_id': student_login_id,
        'pic_path': pic_path
    }

    response = test_client.post('/student/add/store_profile_picture', json=data, headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'Profile picture path stored successfully'

def test_add_subject_missing_subject_name(test_client, auth_header):
    response = test_client.post(
        '/subject/add',
        json={},  # No subject_name provided
        headers=auth_header
    )

    assert response.is_json
    assert response.json['message'] == 'Please Provide Subject name'





def test_edit_student_invalid(test_client, auth_header):

    data = {
        'first_name': 'John',
        'last_name': 'Doe',
        'gender': 'Male',
        'dob': '2000-01-01',
        'father_name': 'Father Name',
        'mother_name': 'Mother Name',
        'guardian_name': 'Guardian Name',
        'is_kyc_verified': True,
        'student_login_id': seed_ids['student_login_id'],
        'pic_path': 'path/to/pic.jpg',
        'aim': 'Engineer',
        'mobile_no_call': '1234567890',
        'email_id': "john@gmail.com",  
    }

    response = test_client.put('/student/editstudent/8885695', json=data, headers=auth_header)
    assert response.json['message'] == 'Student not found'
    

def test_delete_student_invalid(test_client, auth_header):
    response = test_client.delete('/studentdelete/8885695', headers=auth_header)
    assert response.json['message'] == 'Student not found'

def test_activate_student_invalid(test_client, auth_header):
     # Use an existing student ID for testing
    response = test_client.put('/student/activate/8885695', headers=auth_header)
  
    assert response.json['message'] == 'Student not found'


def test_deactivate_student_invalid(test_client, auth_header):

    response = test_client.put('/student/deactivate/8856958', headers=auth_header)

    assert response.json['message'] == 'Student not found'
