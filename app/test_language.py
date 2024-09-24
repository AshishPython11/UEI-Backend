import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.adminuser import LanguageMaster
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

    
    language_name = faker.unique.word()  # Ensure unique language name
    language = LanguageMaster(
        language_name=language_name,
        description=faker.sentence(),
        icon=faker.image_url(),
        is_active=1,
        created_by=1  # Assuming 'admin' is the admin ID or email
    )
    db.session.add(language)
    db.session.commit()
    
    return {
        'language_id': language.language_id,
     
        
    }

def cleanup_seed_data():
    LanguageMaster.query.filter_by(language_id=seed_ids['language_id']).delete()
    
    db.session.commit()

# Test: List Languages
def test_list_languages(test_client, auth_header):
    response = test_client.get('/language/list', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Languages found Successfully' in data['message']

# Test: Add Language
def test_add_language(test_client, auth_header):
    payload = {
        "language_name": faker.unique.language_name(),  # Using Faker for unique language name
        "description": faker.sentence(),  # Generating random description
        "icon": faker.image_url()  # Random image URL
    }
    
    response = test_client.post('/language/add', json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Language created successfully' in data['message']

    # Cleanup: Retrieve the added language and delete it
    language = LanguageMaster.query.filter_by(language_name=payload["language_name"]).first()
    if language:
        db.session.delete(language)
        db.session.commit()


# Test: Edit Language
def test_edit_language(test_client, auth_header):
    
    payload = {
        "language_name": faker.unique.language_name(),  # Faker for new language name
        "description": faker.sentence(),  # New random sentence for description
        "icon": faker.image_url()  # New random image URL
    }
    response = test_client.put(f'/language/edit/{seed_ids['language_id']}', json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Language updated successfully' in data['message']

# Test: Get Language by ID
def test_get_language(test_client, auth_header):
   
    response = test_client.get(f'/language/edit/{seed_ids['language_id']}', headers=auth_header)
    assert response.status_code == 200
    

# Test: Activate Language
def test_activate_language(test_client, auth_header):
    
    response = test_client.put(f'/language/activate/{seed_ids['language_id']}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Language activated successfully' in data['message']

# Test: Deactivate Language
def test_deactivate_language(test_client, auth_header):
    
    response = test_client.put(f'/language/deactivate/{seed_ids['language_id']}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Language deactivated successfully' in data['message']

# Test: Delete Language
def test_delete_language(test_client, auth_header):
    
    response = test_client.delete(f'/languagedelete/{seed_ids['language_id']}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Language deleted successfully' in data['message']