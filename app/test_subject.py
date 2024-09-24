import pytest
from faker import Faker
from app import db,app
from app.models.student import  StudentLogin, SubjectMaster
from flask_jwt_extended import create_access_token
from datetime import datetime
from app.models.log import *
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
def auth_headers(test_client):
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
    unique_subject_name = faker.unique.word().capitalize() + " Subject"
    
    # Check if the subject already exists
    subject = SubjectMaster.query.filter_by(subject_name=unique_subject_name).first()
    if not subject:
        subject = SubjectMaster(
            subject_name=unique_subject_name,
            is_active=1,
            created_by=1,  # Assuming 1 is the ID of the admin user
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.session.add(subject)
        db.session.commit()

    return {
        'subject_id': subject.subject_id
    }

def cleanup_seed_data():
    # Cleanup the seeded subject data
    SubjectMaster.query.filter_by(subject_id=seed_ids['subject_id']).delete()
    db.session.commit()

def test_list_subjects(test_client, auth_headers):
    response = test_client.get('subject/list', headers=auth_headers)
    assert response.status_code == 200
    assert 'data' in response.json

def test_add_subject(test_client, auth_headers):
    unique_subject_name = faker.unique.word() # Seed initial data
    subject_data = {'subject_name': unique_subject_name}
    response = test_client.post('subject/add', json=subject_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Subject created successfully'

def test_edit_subject(test_client, auth_headers):
    updated_subject_name = faker.unique.word()# Seed data and get the subject ID
    subject_data = {'subject_name':updated_subject_name}
    response = test_client.put(f'subject/edit/{seed_ids["subject_id"]}', json=subject_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Subject updated successfully'

def test_get_subject(test_client, auth_headers):
     # Seed data and get the subject ID
    response = test_client.get(f'subject/edit/{seed_ids["subject_id"]}', headers=auth_headers)
    assert response.status_code == 200
     # Adjust based on actual seeded name

def test_delete_subject(test_client, auth_headers):
     # Seed data and get the subject ID
    response = test_client.delete(f'subjectdelete/{seed_ids["subject_id"]}', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Subject deleted successfully'

def test_activate_subject(test_client, auth_headers):
     # Seed data and get the subject ID
    response = test_client.put(f'subject/activate/{seed_ids["subject_id"]}', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Subject activated successfully'

def test_deactivate_subject(test_client, auth_headers):
      # Seed data and get the subject ID
    response = test_client.put(f'subject/deactivate/{seed_ids["subject_id"]}', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['message'] == 'Subject deactivated successfully'
