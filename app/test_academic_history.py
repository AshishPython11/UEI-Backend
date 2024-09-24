import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.log import *
from app.models.student import ClassMaster,CourseMaster,NewStudentAcademicHistory,StudentLogin
from app.models.adminuser import Institution
import time
from faker import Faker

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
    global seed_ids
    seed_ids = seed_data(student_id)  # Extracting student ID
    yield {'Authorization': access_token, 'student_id': student_id}
    cleanup_seed_data()

    # Fetch the user to delete based on the unique email
    user_to_delete = StudentLogin.query.filter_by(userid=unique_email).first()
    if user_to_delete:
        # First, delete any logs related to the user from LoginLog
        db.session.query(LoginLog).filter_by(student_id=user_to_delete.student_id).delete()

        db.session.delete(user_to_delete)

        # Commit the changes to reflect the deletions
        db.session.commit()
def seed_data(student_id):
    # Seed data for testing
    student_login = StudentLogin.query.filter_by(student_id=student_id).first()
    if not student_login:
        raise ValueError("Admin login with userid 'admin123' not found")
    student_id=student_login.student_id
    institution = Institution(institution_name=faker.unique.company(), is_active=1)
    course = CourseMaster(course_name=faker.unique.word(), is_active=1)
    class_master = ClassMaster(class_name=faker.word(), is_active=True)
    
    db.session.add(institution)
    db.session.add(course)
    db.session.add(class_master)
    db.session.commit()
    
    # Create an academic history entry
    academic_history = NewStudentAcademicHistory(
        student_id=student_id,  # Assuming a valid student ID exists
        institution_type='School',
        board='CBSE',
        state_for_stateboard='State A',
        institute_id=institution.institution_id,
        course_id=course.course_id,
        class_id=class_master.class_id,
        year_or_semester='2023',
        created_by=student_id,  # Replace with the admin ID as needed
        updated_by=student_id,
        learning_style='Visual'
    )
    
    db.session.add(academic_history)
    db.session.commit()

    return {
        'institution_id': institution.institution_id,
        'course_id': course.course_id,
        'class_id': class_master.class_id,
        'academic_history_id': academic_history.id
    }
def cleanup_seed_data():
    # Delete academic histories referencing the class
    NewStudentAcademicHistory.query.filter_by(class_id=seed_ids['class_id']).delete()
    
    # Now, safely delete the class
    ClassMaster.query.filter_by(class_id=seed_ids['class_id']).delete()
    
    # Delete courses
    CourseMaster.query.filter_by(course_id=seed_ids['course_id']).delete()
    
    # Delete institutions
    Institution.query.filter_by(institution_id=seed_ids['institution_id']).delete()
    
    db.session.commit()


def test_list_student_academic_histories(test_client, auth_header):
    response = test_client.get('/new_student_academic_history/list', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 200
    assert isinstance(data['data'], list)



def test_add_academic_history(test_client, auth_header):
    new_history = {
        'student_id': auth_header['student_id'],
        'institution_type': 'School',
        'board': 'CBSE',
        'state_for_stateboard': 'State',
        'institute_id': seed_ids['institution_id'],
        'course_id': seed_ids['course_id'],
        'class_id': seed_ids['class_id'],
        'year': '2023',
        'learning_style': 'Visual'
    }
    response = test_client.post('/new_student_academic_history/add', headers=auth_header, json=new_history)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Academic History created successfully'



def test_add_multiple_academic_histories(test_client, auth_header):
    histories = {
        'histories': [
            {
                'student_id': str(auth_header['student_id']),  # Ensure this is a string
                'institution_type': 'College',
                'board': 'ICSE',
                'state_for_stateboard': 'State',
                'institute_id': str(seed_ids['institution_id']),  # Ensure this is a string
                'course_id': str(seed_ids['course_id']),  # Ensure this is a string
                'class_id': str(seed_ids['class_id']),  # Ensure this is a string
                'year': '2023',
                'learning_style': 'Auditory'
            },
            {
                'student_id': str(auth_header['student_id']),  # Ensure this is a string
                'institution_type': 'School',
                'board': 'CBSE',
                'state_for_stateboard': 'State',
                'institute_id': str(seed_ids['institution_id']),  # Ensure this is a string
                'course_id': str(seed_ids['course_id']),  # Ensure this is a string
                'class_id': str(seed_ids['class_id']),  # Ensure this is a string
                'year': '2024',
                'learning_style': 'Visual'
            }
        ]
    }
    response = test_client.post('/new_student_academic_history/multiple_academic_history/add', headers=auth_header, json=histories)
    
    # Debugging output
    print(response.status_code)
    print(response.get_json())

    assert response.status_code == 200

def test_edit_multiple_academic_histories(test_client, auth_header):
    histories = {     
        'histories': [
            {
                'id': seed_ids['academic_history_id'],  # Ensure this ID exists in the database
                'student_id': str(auth_header['student_id']),  # Convert to string
                'institution_type': 'College',
                'board': 'ICSE',
                'state_for_stateboard': 'State',
                'institute_id': str(seed_ids['institution_id']),  # Ensure this is a string
                'course_id': str(seed_ids['course_id']),  # Ensure this is a string
                'class_id': str(seed_ids['class_id']),  # Ensure this is a string
                'year': '2023',
                'learning_style': 'Auditory'
            },
            {
                'id': seed_ids['academic_history_id'],  # Ensure this ID exists in the database
                'student_id': str(auth_header['student_id']),  # Convert to string
                'institution_type': 'School',
                'board': 'CBSE',
                'state_for_stateboard': 'State',
                'institute_id': str(seed_ids['institution_id']),
                'course_id': str(seed_ids['course_id']),
                'class_id': str(seed_ids['class_id']),
                'year': '2024',
                'learning_style': 'Visual'
            }
        ]
    }
    response = test_client.put('/new_student_academic_history/multiple_academic_history/edit', headers=auth_header, json=histories)
    
    # Print the response data for debugging
    print(response.get_data(as_text=True))  # Print the response content
    assert response.status_code == 200



def test_edit_academic_history(test_client, auth_header):
    academic_history_id = seed_ids['academic_history_id'] # Use a valid ID from your database
    updated_data = {
        'student_id': str(auth_header['student_id']),
        'institution_type': 'School',
        'board': 'CBSE',
        'state_for_stateboard': 'Updated State',
        'institute_id': str(seed_ids['institution_id']),  # Ensure this is a string
        'course_id': str(seed_ids['course_id']),  # Ensure this is a string
        'class_id': str(seed_ids['class_id']), # Adjust according to your seeded data
        'learning_style': 'Visual',
          # Adjust according to your seeded data
        'year': '2023'
    }
    response = test_client.put(f'/new_student_academic_history/edit/{academic_history_id}', headers=auth_header, json=updated_data)
    assert response.status_code == 200
    
    data = response.get_json()
    print(data)
    assert data['message'] == 'Academic History updated successfully'

def test_get_academic_history(test_client, auth_header):
    student_id=auth_header['student_id'] # Use the authenticated student ID
    response = test_client.get(f'/new_student_academic_history/get/{student_id}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 200
    assert isinstance(data['data'], list)

def test_delete_academic_history(test_client, auth_header):
    academic_history_id = seed_ids['academic_history_id']  # Use a valid ID from your database
    response = test_client.delete(f'/new_student_academic_history/delete/{academic_history_id}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Academic History deleted successfully'

def test_activate_academic_history(test_client, auth_header):
    academic_history_id = seed_ids['academic_history_id'] # Use a valid ID from your database
    response = test_client.put(f'/new_student_academic_history/activate/{academic_history_id}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Academic History activated successfully'

def test_deactivate_academic_history(test_client, auth_header):
    academic_history_id = seed_ids['academic_history_id'] # Use a valid ID from your database
    response = test_client.put(f'/new_student_academic_history/deactivate/{academic_history_id}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Academic History deactivated successfully'