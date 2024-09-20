import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.student import StudentLogin

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            global seed_ids
            seed_ids = seed_data()  
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
    response = test_client.post('/auth/login', json={
  "userid": "1",
  "password": "111",
  "user_type": "student"
})

    print("Login response status code:", response.status_code)
    print("Login response data:", response.json)
    
    assert response.status_code == 200, f"Login failed with status code {response.status_code}"
    
    data = response.json
    if 'token' not in data:
        pytest.fail(f"Login response missing 'token': {data}")
    
    access_token = data['token']
    student_id=data['data']['id']
    return {'Authorization': access_token,'student_id':student_id}

def seed_data():
    student_login = StudentLogin.query.filter_by(userid='1').first()
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
    
   

def test_chatconversation_post_success(test_client, auth_header):
    # Define the JSON payload
    payload = {
        'question': 'What is computer?',
        'prompt': 'Please answer the following question:'
    }
    
    # Send POST request to the /chatconversation endpoint
    response = test_client.post('/chat/chatconversation', json=payload, headers=auth_header)

    # Check if the status code is 200 OK
    assert response.status_code == 200

    # Optionally, check if the response contains the expected keys
    response_json = response.get_json()
    assert 'message' in response_json
    assert 'data' in response_json
    assert 'question' in response_json['data']
    assert 'answer' in response_json['data']
    assert 'prompt' in response_json['data']

    # Optionally, check if the 'message' key has the expected value
    assert response_json['message'] == 'Answer stored successfully'
    
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



    
    # Restore the original method
