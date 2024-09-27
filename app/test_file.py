import pytest
from app import app, db
from app.models.student import Feedback, StudentFeedback, StudentLogin
import time
from app.models.log import *
import os
from io import BytesIO
from faker import Faker

faker = Faker()
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
            cleanup_seed_data()
            db.session.remove()
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'student')            

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
    student_id = data['data']['id']  # Extracting student ID
    yield {'Authorization': access_token, 'student_id': student_id}
    user_to_delete = StudentLogin.query.filter_by(userid=unique_email).first()
    if user_to_delete:
        db.session.query(LoginLog).filter_by(student_id=user_to_delete.student_id).delete()
        db.session.delete(user_to_delete)
        db.session.commit()


def seed_data():
    """ Seed data for tests """
    # No specific database seeding required for upload tests, return empty dict
    return {}


def cleanup_seed_data():
    """ Clean up after tests by deleting uploaded files """
    folder = UPLOAD_FOLDER
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


### Test Cases for Upload File

def test_file_upload(test_client, auth_header):
    """ Test the file upload endpoint """
    # Create a sample file for upload
    data = {
        'file': (BytesIO(b'This is a test file.'), 'test_file.txt'),
    }

    response = test_client.post(
        '/upload_file/upload',
        content_type='multipart/form-data',
        headers=auth_header,
        data=data
    )

    assert response.status_code == 200
    json_data = response.json
    assert 'File uploaded successfully' in json_data['message']
    assert 'image_url' in json_data['data']





### Test Cases for File Retrieval

def test_get_uploaded_file(test_client, auth_header):
    """ Test retrieval of the uploaded file """
    
    data = {
        'file': (BytesIO(b'This is a test file for retrieval.'), 'retrieval_file.txt'),
    }
    upload_response = test_client.post(
        '/upload_file/upload',
        content_type='multipart/form-data',
        headers=auth_header,
        data=data
    )
    assert upload_response.status_code == 200
    json_data = upload_response.json
    assert 'image_url' in json_data['data']

    # Now retrieve the uploaded file
    file_name = 'retrieval_file.txt'
    get_response = test_client.get(f'/upload_file/get_image/{file_name}', headers=auth_header)
    
    assert get_response.status_code == 200
    json_data = get_response.json
    assert 'File fetch successfully' in json_data['message']
    assert 'data:image/png;base64,' in json_data['data']


def test_get_file_not_found(test_client, auth_header):
    """ Test retrieval of a non-existing file """
    get_response = test_client.get('/upload_file/get_image/nonexistent_file.txt', headers=auth_header)

    assert get_response.status_code == 200
    json_data = get_response.json
    assert 'error' in json_data
    assert json_data['error'] == 'File not found'

import io
### Cleanup Test



def test_upload_file_no_file_part(test_client, auth_header):
    # Test no file part
    response = test_client.post('/upload_file/upload', headers=auth_header)
    
    # assert response.is_json
    json_data = response.json
    
    assert json_data['message'] == "400 Bad Request: The browser (or proxy) sent a request that this server could not understand."

def test_upload_file_no_selected_file(test_client, auth_header):
    # Test no selected file
    response = test_client.post('/upload_file/upload', data={'file': (io.BytesIO(b""), '')}, headers=auth_header)
    
    # assert response.is_json
    json_data = response.json
    assert 'error' in json_data
    assert json_data['error'] == 'No selected file'
    

def test_upload_file_invalid_file_type(test_client, auth_header):
    # Test invalid file type
    response = test_client.post('/upload_file/upload', data={'file': (io.BytesIO(b"test content"), 'test_image.exe')}, headers=auth_header)
    
    # assert response.is_json
    json_data = response.json
    
    assert json_data['message']== 'Object of type Response is not JSON serializable'
    