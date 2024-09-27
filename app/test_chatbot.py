import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.log import *
from app.models.student import StudentLogin
from app.models.chatbot import Chatbot,ChatCache,ChatConversionData,CustomChatData
from datetime import datetime
import random
from faker import Faker
faker=Faker()
@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
             
        yield testing_client
        with app.app_context():
            cleanup_seed_data()
            db.session.remove()

@pytest.fixture
def auth_header(test_client):
#     test_client.post('/auth/signup', json={
#   "userid": "admin123",
#   "password": "admin123",
#   "user_type": "admin"
# })
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
    chat_data = CustomChatData(
        student_id=student_id,
        chat_title=faker.word(),
        chat_conversation='This is a test conversation.',
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    db.session.add(chat_data)
    db.session.commit()
    return {
        'student_login_id': student_id,
        'chat_data_id': chat_data.id  # Return the id of the created chat data
    }
def cleanup_seed_data():
    # Clean up the data after the test
    class_master = CustomChatData.query.filter_by(id=seed_ids['chat_data_id']).first()
    if class_master:
        db.session.delete(class_master)
        db.session.commit()
def test_chatbot_list_based_on_id_success(test_client, auth_header):
    # Assuming `seed_data` function creates and returns necessary data including student_id and chat data
    
    student_id = seed_ids['student_login_id']
    
    response = test_client.get(f'/Chatbot/list_based_on_id/{student_id}', headers=auth_header)

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['status'] == 200
    assert 'message' in response_json
    assert 'data' in response_json
def test_chatbot_get_all_data_success(test_client, auth_header):
    response = test_client.get('/Chatbot/getalldata', headers=auth_header)

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['status'] == 200
    assert 'message' in response_json
    assert 'data' in response_json
def test_chatbot_add_success(test_client, auth_header):
    data = {
        'student_id': 1,  # Ensure this student_id exists in your test database
        'chat_question': 'What is AI?',
        'response': 'AI stands for Artificial Intelligence.'
    }

    response = test_client.post('/Chatbot/add', json=data, headers=auth_header)

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['status'] == 200
    assert response_json['message'] == 'Chat created successfully'
    
def test_chatbot_delete_success(test_client, auth_header):
    # Assuming `seed_data` returns a chat_data_id
   
    
    
    response = test_client.delete(f'/Chatbot/delete/{seed_ids['chat_data_id']}', headers=auth_header)

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['status'] == 200
    assert response_json['message'] == 'Chatbot activated successfully'

def test_chatbot_activate_success(test_client, auth_header):
    # First, create a chat entry that will be used for activation
    data = {
        'student_id': 1,  # Ensure this student_id exists in your test database
        'chat_question': 'What is AI?',
        'response': 'AI stands for Artificial Intelligence.'
    }

    response = test_client.post('/Chatbot/add', json=data, headers=auth_header)

    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['status'] == 200
    assert response_json['message'] == 'Chat created successfully'
    
    activate_response = test_client.put(f'/Chatbot/activate/{seed_ids['chat_data_id']}', headers=auth_header)
    
    assert activate_response.status_code == 200
    


def test_chatbot_deactivate_success(test_client, auth_header):
    # Assuming `seed_data` returns a chat_data_id
    create_response = test_client.post('/Chatbot/add', json={
        'student_id': 1, 
        'chat_question': 'What is AI?',
        'response': 'AI stands for Artificial Intelligence.'
    }, headers=auth_header)

    assert create_response.status_code == 200

    response = test_client.put(f'/Chatbot/deactivate/{seed_ids['chat_data_id']}', headers=auth_header)

    assert response.status_code == 200

def test_chat_data_store_success(test_client, auth_header):
    data = {
        'student_id': 1,  # Ensure this student_id exists in your test database
        'chat_title': 'Test Chat Title',
        'chat_conversation': 'This is a test chat conversation.',
        'flagged': True
    }

    response = test_client.post('/Chatbot/chat_data_store', json=data, headers=auth_header)

    assert response.status_code == 200
def test_chatbot_add_missing_student_id(test_client, auth_header):
    response = test_client.post('/chatbot/add', json={
        'chat_question': 'What is the weather today?',
        'response': 'It is sunny today.'
    }, headers=auth_header)

    
    
    assert response.status_code == 404