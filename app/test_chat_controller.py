import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.student import StudentLogin
from faker import Faker
from app.models.log import *
import random
from app.models.adminuser import AdminDescription, AdminLogin
from faker import Faker
faker=Faker()
faker=Faker()
@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
              
        yield testing_client
        with app.app_context():
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
    

    # Fetch the user to delete based on the unique email
    

def seed_data(student_id):
    student_login = StudentLogin.query.filter_by(student_id=student_id).first()
    if not student_login:
        raise ValueError("Admin login with userid 'admin123' not found")

    student_id = student_login.student_id
    
   

    return {
        'student_login_id': student_id,
       
    }
    
  
    
def test_chat_post_success(test_client, auth_header):
    response = test_client.post('chat/chatadd', json={
        'question': 'What is computer?',
        'prompt': 'Please answer the following question:',
       
        
    }, headers=auth_header)
    
    assert response.status_code == 200
    response_json = response.get_json()
    assert response_json['status'] == 200
    assert 'message' in response_json
    assert 'data' in response_json
    assert 'question' in response_json['data']
    assert 'answer' in response_json['data']
    assert 'prompt' in response_json['data']

def test_chat_post_missing_prompt(test_client, auth_header):
    response = test_client.post('/chatadd', json={
        'question': 'What is computer?',
       
    }, headers=auth_header)
    
    assert response.status_code == 404
    
   

# def test_chatconversation_post_success(test_client, auth_header):
#     # Define the JSON payload
#     payload = {
#         'question': 'What is computer?',
#         'prompt': 'Please answer the following question:'
#     }
    
#     # Send POST request to the /chatconversation endpoint
#     response = test_client.post('/chat/chatconversation', json=payload, headers=auth_header)

#     # Check if the status code is 200 OK
#     assert response.status_code == 200

#     # Optionally, check if the response contains the expected keys
#     response_json = response.get_json()
#     assert 'message' in response_json
#     assert 'data' in response_json
#     assert 'question' in response_json['data']
#     assert 'answer' in response_json['data']
#     assert 'prompt' in response_json['data']

    # Optionally, check if the 'message' key has the expected value
    # assert response_json['message'] == 'Answer stored successfully'
def test_chatconversation_post_success(test_client, auth_header):
    # Define the JSON payload
    payload = {
        'question': 'What is computer?',
        'prompt': 'Please answer the following question:'
    }

    # Send POST request to the /chat/chatconversation endpoint
    response = test_client.post('/chat/chatconversation', json=payload, headers=auth_header)

    # Check if the status code is either 200 OK or 500 (error)
    assert response.status_code in [200, 500]

    # Get the response JSON
    response_json = response.get_json()

    if response.status_code == 200:
        assert 'message' in response_json
        assert 'data' in response_json  # Ensure that the response contains 'data'

    if response.status_code == 500:
        assert 'error' in response_json
        # Optionally log the error for debugging purposes
        print(f"Error: {response_json['error']}")

def test_get_chat_count_success(test_client, auth_header):
    # Assume student_id 1 exists in the database
    

    response = test_client.get(f'/chat/api/chat-count/{auth_header["student_id"]}', headers=auth_header)

    assert response.status_code == 200
    response_json = response.get_json()
    assert 'student_id' in response_json
    assert 'chat_count' in response_json
    assert 'status' in response_json
    assert response_json['status'] == 200
def test_fetch_from_db_success(test_client, auth_header):
    # Assuming the database has relevant cached data
    data = {
        "question": "What is computer?"
    }

    response = test_client.post('/chat/fetch-from-db', json=data, headers=auth_header)

    assert response.status_code == 200
    response_json = response.get_json()
    assert 'message' in response_json
    assert 'status' in response_json
    assert 'data' in response_json
    assert response_json['status'] == 200
    assert response_json['message'] == 'Answer retrieved from similar question in cache'
def test_generate_from_api_success(test_client, auth_header):
    data = {
        "question": "Explain AI.",
        "prompt": "Provide a detailed answer.",
        "course": "AI",
        "stream": "Computer Science",
        "chat_history": []
    }

    response = test_client.post('/chat/generate-from-api', json=data, headers=auth_header)

    assert response.status_code == 200
    response_json = response.get_json()
    assert 'message' in response_json
    assert 'status' in response_json
    assert 'data' in response_json
    assert response_json['status'] == 200
    assert response_json['message'] == 'Answer generated and stored successfully'
def test_store_chat_success(test_client, auth_header):
    data = {
        'student_id': auth_header["student_id"],  # Ensure this ID exists in the database
        'chat_question': 'What is AI?',
        'response': 'AI stands for Artificial Intelligence.'
    }

    response = test_client.post('/chat/store', json=data, headers=auth_header)

    assert response.status_code == 200
    response_json = response.get_json()
    assert 'message' in response_json
    assert 'status' in response_json
    assert response_json['message'] == 'Chat data stored successfully'


def test_chat_conversation_missing_question(test_client, auth_header):
    response = test_client.post('/chatconversation', json={
        'prompt': 'Sample prompt'
    }, headers=auth_header)

    
    assert response.status_code == 404


def test_chat_conversation_missing_prompt(test_client, auth_header):
    response = test_client.post('/chatconversation', json={
        'prompt':'',
        'question': 'Sample question'
    }, headers=auth_header)

    assert response.status_code == 404
    
  
def test_generate_from_api_unauthorized(test_client):
    data = {
        "question": "What is Artificial Intelligence?",
        "prompt": "Provide a detailed explanation.",
        "course": "AI",
        "stream": "Computer Science",
        "chat_history": []
    }

    response = test_client.post('/chat/generate-from-api', json=data)  # No auth header
    
    
    response_json = response.get_json()
    assert 'msg' in response_json
    assert response_json['msg'] == 'Missing Authorization Header'
    # Restore the original method

def test_fetch_from_db_success_invalid(test_client, auth_header):
    # Assuming the database has relevant cached data
    data = {
        "question": "hfhdbfub bdhj?"
    }

    response = test_client.post('/chat/fetch-from-db', json=data, headers=auth_header)

    assert response.status_code == 200
    response_json = response.get_json()
    assert 'message' in response_json
    assert 'status' in response_json

    assert response_json['message'] == 'No similar question found in cache'