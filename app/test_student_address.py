import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.student import StudentAddress,StudentLogin
from faker import Faker
from app.models.student import StudentLogin
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
        db.session.query(StudentAddress).filter_by(student_id=user_to_delete.student_id).delete()

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
    student_address = StudentAddress(
        student_id=student_id,
        address1=faker.address()[:80],
        address2=faker.address()[:80],
        country=faker.country(),
        state=faker.state(),
        city=faker.city(),
        district=faker.city(),
        pincode=faker.postcode(),
        address_type=faker.word()[:10],
        is_active=1,
        created_by=student_id  # Assuming 'admin' is the admin ID or email
    )
    db.session.add(student_address)
    db.session.commit()
    
    return {
        'address_id': student_address.address_id,
        'student_id': student_address.student_id
    }

def cleanup_seed_data():
    # Remove the seeded student address
    StudentAddress.query.filter_by(address_id=seed_ids['address_id']).delete()
    db.session.commit()

def test_student_address_list(test_client, auth_header):
    response = test_client.get('/student_address/list', headers=auth_header)
    assert response.status_code == 200
    assert isinstance(response.json['data'], list)  # Check if data is a list

def test_student_address_add(test_client, auth_header):
    new_address_data = {
        'student_id': auth_header['student_id'],
        'address1': faker.address(),
        'address2': faker.address(),
        'country': faker.country(),
        'state': faker.state(),
        'city': faker.city(),
        'district': faker.city(),
        'pincode': faker.postcode(),
        'address_type': faker.word()
    }
    response = test_client.post('/student_address/add', headers=auth_header, json=new_address_data)
    assert response.status_code == 200
    assert response.json['message'] == 'Student Address created successfully'

# Add more test cases for edit, delete, activate, deactivate, etc.
def test_list_student_addresses(test_client,auth_header):
    
    response = test_client.get('/student_address/list',headers=auth_header)
    assert response.status_code == 200
    assert 'data' in response.json

def test_get_student_address(test_client, auth_header):
    
    student_id = auth_header['student_id']  # replace with actual generated student ID
    response = test_client.get(f'/student_address/edit/{student_id}',headers=auth_header)
    assert response.status_code == 200
    assert 'data' in response.json

def test_edit_student_address(test_client, auth_header):
    student_id = auth_header['student_id']  # Replace with actual generated student ID

    # Send the request to create or update student address
    response = test_client.put(f'/student_address/edit/{student_id}', json={
        'student_id': student_id,
        'address1': faker.address(),
        'address2': faker.address(),
        'country': faker.country(),
        'state': faker.state(),
        'city': faker.city(),
        'district': faker.city(),
        'pincode': faker.zipcode(),
        'address_type': faker.random_element(['home', 'work'])
    }, headers=auth_header)

    assert response.status_code in [200, 201]  # Allow both success codes

    # Allow both messages (either creation or update)
    expected_messages = ['Student Address updated successfully', 'Student Address created successfully']
    assert response.json['message'] in expected_messages


def test_delete_student_address(test_client, auth_header):
  
    student_id =seed_ids['address_id']   # replace with actual generated student ID
    response = test_client.delete(f'/student_addressdelete/{student_id}',headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'Student Address deleted successfully'

def test_activate_student_address(test_client, auth_header):
    student_id=seed_ids['address_id'] 
     # replace with actual generated student ID
    response = test_client.put(f'/student_address/activate/{student_id}',headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'Student Address activated successfully'

def test_deactivate_student_address(test_client, auth_header):
   
    student_id = seed_ids['address_id']   # replace with actual generated student ID
    response = test_client.put(f'/student_address/deactivate/{student_id}',headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'Student Address deactivated successfully'