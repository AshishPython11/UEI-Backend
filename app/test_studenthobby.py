import pytest
from faker import Faker
from app import db,app
from app.models.student import  StudentLogin, StudentHobby,Hobby
from app.models.log import *

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
    hobby = Hobby(
        hobby_name=faker.word(),
        is_active=1,
        created_by=faker.email(),
        updated_by=faker.email()
    )
    db.session.add(hobby)
    db.session.commit()
    student_hobby = StudentHobby(
        student_id=student_id,
        hobby_id=hobby.hobby_id,
        is_active=1,
        created_by=1,
        created_at=datetime.now()
    )

    db.session.add(student_hobby)
    db.session.commit()

    # Return the seeded data for use in tests
    return {
        'student_id': student_id,
        'hobby_id': hobby.hobby_id
    }

def cleanup_seed_data():
    # Cleanup the seeded student hobby
    StudentHobby.query.filter_by(student_id=seed_ids['student_id'], hobby_id=seed_ids['hobby_id']).delete()
    db.session.commit()

def test_student_hobby_add(test_client, auth_header):
    response = test_client.post('/student_hobby/add', 
                                 headers=auth_header, 
                                 json={"student_id": auth_header['student_id'], "hobby_id": seed_ids['hobby_id']})
    assert response.status_code == 200
    assert 'Student Hobby created successfully' in response.json['message']

def test_student_hobby_list(test_client, auth_header):
    response = test_client.get('/student_hobby/list', headers=auth_header)
    assert response.status_code == 200
    assert isinstance(response.json['data'], list)

def test_student_multiple_hobby_add(test_client, auth_header):
    hobbies = [
        {"student_id": str(auth_header['student_id']), "hobby_id": seed_ids['hobby_id']},
        {"student_id": str(auth_header['student_id']), "hobby_id": seed_ids['hobby_id']}
    ]
    response = test_client.post('/student_hobby/multiadd', 
                                 headers=auth_header, 
                                 json={"hobbies": hobbies})
    assert response.status_code == 200
    assert len(response.json) > 0  # Check that some response was returned

def test_student_hobby_edit(test_client, auth_header):
    student_hobby = StudentHobby.query.filter_by(student_id=auth_header['student_id']).first()
    response = test_client.put(f'/student_hobby/edit/{student_hobby.id}', 
                                headers=auth_header, 
                                json={"student_id": auth_header['student_id'], "hobby_id": seed_ids['hobby_id']})
    assert response.status_code == 200
    assert 'Student Hobby updated successfully' in response.json['message']

def test_student_hobby_get(test_client, auth_header):
    student_hobby = StudentHobby.query.filter_by(student_id=auth_header['student_id']).first()
    response = test_client.get(f'/student_hobby/edit/{auth_header['student_id']}', headers=auth_header)
    assert response.status_code == 200
    

def test_student_hobby_delete(test_client, auth_header):
    student_hobby = StudentHobby.query.filter_by(student_id=auth_header['student_id']).first()
    response = test_client.delete(f'/student_hobby/delete/{student_hobby.id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Student Hobby deleted successfully' in response.json['message']

def test_student_hobby_activate(test_client, auth_header):
    student_hobby = StudentHobby.query.filter_by(student_id=auth_header['student_id'], is_active=0).first()
    if not student_hobby:
        student_hobby = StudentHobby(student_id=auth_header['student_id'], hobby_id=seed_ids['hobby_id'], is_active=0)
        db.session.add(student_hobby)
        db.session.commit()
    
    response = test_client.put(f'/student_hobby/activate/{student_hobby.id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Student Hobby activated successfully' in response.json['message']

def test_student_hobby_deactivate(test_client, auth_header):
    student_hobby = StudentHobby.query.filter_by(student_id=auth_header['student_id'], is_active=1).first()
    response = test_client.put(f'/student_hobby/deactivate/{student_hobby.id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Student Hobby deactivated successfully' in response.json['message']

def test_get_all_student_hobbies(auth_header, test_client):
    # Test fetching all student hobbies
    response = test_client.get('/student_hobby/alldata', headers=auth_header)
    
    assert response.status_code == 200
    


def test_multiple_hobby_edit_success(auth_header, test_client):
    # Seed data for editing
    hobby_id = seed_ids['hobby_id']
    
    # Prepare data for multiple edit
    data = {
        'hobbies': [
            {
                'id': 1,  # Assuming this ID exists in the database
                'student_id': str(seed_ids['student_id']),
                'hobby_id': hobby_id
            }
        ]
    }
    
    response = test_client.put('/student_hobby/multiple_hobby_edit', json=data, headers=auth_header)
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    




