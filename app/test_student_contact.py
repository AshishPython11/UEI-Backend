import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.student import Contact,StudentLogin
from faker import Faker
from app.models.log import LoginLog
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
        db.session.query(Contact).filter_by(student_id=user_to_delete.student_id).delete()

        # Delete related subject preferences before deleting the student login
        

        # Now delete the student login itself
        db.session.delete(user_to_delete)

        # Commit the changes to reflect the deletions
        db.session.commit()


def seed_data(student_id):
    student_login = StudentLogin.query.filter_by(student_id=student_id).first()
    if not student_login:
        raise ValueError("student login with userid '1' not found")
    # Create unique student addresses for testing
    student_id=student_login.student_id
    contact = Contact(
        student_id=student_id,
        mobile_isd_call=faker.phone_number(),
        mobile_no_call=faker.phone_number(),
        mobile_isd_watsapp=faker.phone_number(),
        mobile_no_watsapp=faker.phone_number(),
        email_id=faker.email(),
        is_active=1
    )
    db.session.add(contact)
    db.session.commit()
    print(f"Created student contact with ID: {contact.contact_id}")
    return {
        'contact_id': contact.contact_id,
        'student_id': contact.student_id
    }

def cleanup_seed_data():
    Contact.query.filter_by(contact_id=seed_ids['contact_id']).delete()
    db.session.commit()

def test_student_contact_list(test_client, auth_header):
    response = test_client.get('/student_contact/list', headers=auth_header)
    assert response.status_code == 200
    assert isinstance(response.json['data'], list)  # Check if data is a list
def test_student_contact_alldata(test_client, auth_header):
    response = test_client.get('/student_contact/alldata', headers=auth_header)
    assert response.status_code == 200
    assert isinstance(response.json['data'], list)
def test_student_contact_add(test_client, auth_header):
    new_contact_data = {
        'student_id': auth_header['student_id'],
        'mobile_isd_call': faker.phone_number(),
        'mobile_no_call': faker.phone_number(),
        'mobile_isd_watsapp': faker.phone_number(),
        'mobile_no_watsapp': faker.phone_number(),
        'email_id': faker.email()
    }
    response = test_client.post('/student_contact/add', headers=auth_header, json=new_contact_data)
    assert response.status_code == 200
    assert response.json['message'] == 'Student Contact created successfully'


def test_get_student_contact(test_client, auth_header):

    
    response = test_client.get(f'/student_contact/edit/{auth_header['student_id']}', headers=auth_header)
    assert response.status_code == 200
    assert 'data' in response.json


def test_edit_student_contact(test_client, auth_header):
      # replace with actual generated contact ID
    response = test_client.put(f'/student_contact/edit/{auth_header['student_id']}', json={
        'student_id':auth_header['student_id'],
        'mobile_isd_call': faker.country_calling_code(),
        'mobile_no_call': faker.phone_number(),
        'mobile_isd_watsapp': faker.country_calling_code(),
        'mobile_no_watsapp': faker.phone_number(),
        'email_id': faker.email()
    }, headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'Student Contact updated successfully'

def test_activate_student_contact(test_client, auth_header):
    contact_id = seed_ids['contact_id']  # replace with actual generated contact ID
    response = test_client.put(f'/student_contact/activate/{contact_id}', headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'Student contact activated successfully'

def test_deactivate_student_contact(test_client, auth_header):
    contact_id = seed_ids['contact_id']  # replace with actual generated contact ID
    response = test_client.put(f'/student_contact/deactivate/{contact_id}', headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'Student Contact deactivated successfully'
