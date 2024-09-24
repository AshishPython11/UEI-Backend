import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.adminuser import Institution, EntityType, AdminBasicInformation
import time
from app.models.student import StudentLogin
from app.models.log import LoginLog
from faker import Faker

faker = Faker()

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
#     test_client.post('/auth/signup', json={
#   "userid": "admin123",
#   "password": "admin123",
#   "user_type": "admin"
# })
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
    student_id = data['data']['id']  # Extracting student ID
    yield {'Authorization': access_token, 'student_id': student_id}
    user_to_delete = StudentLogin.query.filter_by(userid=unique_email).first()
    if user_to_delete:
        db.session.query(LoginLog).filter_by(student_id=user_to_delete.student_id).delete()
        db.session.delete(user_to_delete)
        db.session.commit()

def seed_data():
    # Create an EntityType to associate with Institution
    entity_name=faker.word()
    entity_type = EntityType(entity_type=entity_name)
    db.session.add(entity_type)
    db.session.commit()
    
    institution_name = faker.word()
    institution = Institution(
        institution_name=institution_name,
        entity_id=entity_type.entity_id,
        address=faker.address(),
        country=faker.country(),
        state=faker.state(),
        city=faker.city(),
        district=faker.city_suffix(),
        pincode=faker.postcode(),
        website_url=faker.url(),
        email_id=faker.email(),
        mobile_no=faker.phone_number(),
        is_active=1,
        created_by=1 # Assuming 'admin' is the admin ID or email
    )
    db.session.add(institution)
    db.session.commit()
    return {
        'institution_id': institution.institution_id,
        'entity_type_id': entity_type.entity_id,
        'institution_name': institution_name
    }

def cleanup_seed_data():
    Institution.query.filter_by(institution_id=seed_ids['institution_id']).delete()
    EntityType.query.filter_by(entity_id=seed_ids['entity_type_id']).delete()
    db.session.commit()

def test_institution_list(test_client, auth_header):
    response = test_client.get('/institution/list', headers=auth_header)
    assert response.status_code == 200
    
    # Check for the message in the response
    response_data = response.json  # Get the response as JSON
    assert 'message' in response_data  # Ensure 'message' key is present
    assert response_data['message'] == 'Institutions found Successfully'

def test_institution_add(test_client, auth_header):
    institution_name = faker.company()
    response = test_client.post('/institution/add', headers=auth_header, json={
        'institution_name': institution_name,
        'entity_id': seed_ids['entity_type_id'],
        'address': faker.address(),
        'country': faker.country(),
        'state': faker.state(),
        'city': faker.city(),
        'district': faker.city_suffix(),
        'pincode': faker.postcode(),
        'website_url': faker.url(),
        'email_id': faker.email(),
        'mobile_no': faker.phone_number()
    })
    assert response.status_code == 200
    assert 'Institution created successfully' in response.json['message']

    # Cleanup: Delete the institution added during this test
    institution_id = response.json['institution']['id']
    Institution.query.filter_by(institution_id=institution_id).delete()
    db.session.commit()

# def test_institution_add_duplicate(test_client, auth_header):
#     # Attempt to add an institution with the same name as the seeded one
#     response = test_client.post('/institution/add', headers=auth_header, json={
#         'institution_name': seed_ids['institution_name'],  # Duplicate name
#         'entity_id': seed_ids['entity_type_id'],
#         'address': faker.address(),
#         'country': faker.country(),
#         'state': faker.state(),
#         'city': faker.city(),
#         'district': faker.city_suffix(),
#         'pincode': faker.postcode(),
#         'website_url': faker.url(),
#         'email_id': faker.email(),
#         'mobile_no': faker.phone_number()
#     })
#     assert response.status_code == 409  # Conflict
#     assert 'Institute already exists' in response.json['message']

def test_institution_edit(test_client, auth_header):
    new_institution_name = faker.company()
    response = test_client.put(f'/institution/edit/{seed_ids["institution_id"]}', headers=auth_header, json={
        'institution_name': new_institution_name,
        'entity_id': seed_ids['entity_type_id'],
        'address': faker.address(),
        'country': faker.country(),
        'state': faker.state(),
        'city': faker.city(),
        'district': faker.city_suffix(),
        'pincode': faker.postcode(),
        'website_url': faker.url(),
        'email_id': faker.email(),
        'mobile_no': faker.phone_number()
    })
    assert response.status_code == 200
    assert 'Institution updated successfully' in response.json['message']

def test_institution_get(test_client, auth_header):
    response = test_client.get(f'/institution/edit/{seed_ids["institution_id"]}', headers=auth_header)
    assert response.status_code == 200
    assert 'Institution found Successfully' in response.json['message']
    assert response.json['data']['id'] == seed_ids['institution_id']

def test_institution_delete(test_client, auth_header):
    institution_id = seed_ids['institution_id']
    response = test_client.delete(f'/institutiondelete/{institution_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Institution deleted successfully' in response.json['message']

    # Verify that the institution is marked as deleted
    institution = Institution.query.get(institution_id)
    assert institution.is_deleted is True

def test_institution_activate(test_client, auth_header):
    institution_id = seed_ids['institution_id']
    # Ensure the institution is deactivated first
    institution = Institution.query.get(institution_id)
    if institution.is_active == 1:
        institution.is_active = 0
        db.session.commit()

    response = test_client.put(f'/institution/activate/{institution_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Institution activated successfully' in response.json['message']
    # Verify activation
    institution = Institution.query.get(institution_id)
    assert institution.is_active == 1

def test_institution_deactivate(test_client, auth_header):
    institution_id = seed_ids['institution_id']
    response = test_client.put(f'/institution/deactivate/{institution_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Institution deactivated successfully' in response.json['message']
    # Verify deactivation
    institution = Institution.query.get(institution_id)
    assert institution.is_active == 0
