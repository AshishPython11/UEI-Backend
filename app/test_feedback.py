import pytest
from app import app, db
from app.models.student import Feedback, StudentFeedback, StudentLogin,Student
import time
from app.models.log import *
from datetime import datetime
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


def seed_data(student_id):
    student_login = StudentLogin.query.filter_by(student_id=student_id).first()
    if not student_login:
        raise ValueError("Admin login with userid 'admin123' not found")

    student = Student(
        
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        gender='Male',
        dob=faker.date_of_birth(),
        father_name=faker.name(),
        mother_name=faker.name(),
        guardian_name=faker.name(),
        student_login_id=student_login.student_id,
        is_kyc_verified=1,
        system_datetime=datetime.now(),
        pic_path='path/to/test/image.png',
        last_modified_datetime=datetime.now(),
        student_registration_no=faker.uuid4(),
        created_by=1,
        is_active=1
    )
    db.session.add(student)
    db.session.commit()

    student_id = student.student_login_id
    # Seed feedback data
    feedback = Feedback(question="Whats do you think about the course?", 
                        options='["Excellent", "Good", "Average", "Poor"]', 
                        is_active=True, created_by=student_id)
    db.session.add(feedback)
    db.session.commit()
    feedback_id = feedback.id

    # Seed student feedback data
    student_feedback = StudentFeedback(student_id=student_id, 
                                        question="What do you think about the instructor?", 
                                        answer="Great!")
    db.session.add(student_feedback)
    db.session.commit()
    
    return {
        
        'feedback_id': feedback_id,
        'student_feedback_id': student_feedback.id
    }

def cleanup_seed_data():
    Feedback.query.filter_by(is_deleted=True).delete()
    StudentFeedback.query.filter_by(question="What do you think about the instructor?").delete()
    db.session.commit()

# Test cases for Feedback API
def test_feedback_list(test_client, auth_header):
    response = test_client.get('/feedback/list', headers=auth_header)
    assert response.status_code == 200
    assert 'Feedback questions found successfully' in response.json['message']


    


def test_feedback_edit(test_client, auth_header):
    feedback_id = seed_ids['feedback_id']
    response = test_client.put(f'/feedback/edit/{feedback_id}', headers=auth_header, json={
        "question": "How would you rate the course content?",
        "options": ["Poor", "Fair", "Good", "Excellent"]
    })
    assert response.status_code == 200
    assert 'Feedback updated successfully' in response.json['message']

def test_feedback_get(test_client, auth_header):
    feedback_id = seed_ids['feedback_id']
    response = test_client.get(f'/feedback/{feedback_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Feedback Details found successfully' in response.json['message']

def test_feedback_delete(test_client, auth_header):
    feedback_id = seed_ids['feedback_id']
    print(seed_ids['feedback_id'])
    response = test_client.delete(f'/feedback/delete/{feedback_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Feedback deleted successfully' in response.json['message']

# Test cases for Student Feedback API
def test_feedback_add(test_client, auth_header):
    response = test_client.post('/feedback/add', headers=auth_header, json={
        "question": "Rate the overall experience",
        "options": ["1 Star", "2 Stars", "3 Stars", "4 Stars", "5 Stars"]
    })
    assert response.status_code == 200
    assert 'Feedback created successfully' in response.json['message']
    
    Feedback.query.filter_by(question="Rate the overall experience").delete()
    db.session.commit()
    
    # Get the created feedback ID
    

def test_student_feedback_add(test_client, auth_header):
    unique_suffix = str(int(time.time()))
    unique_question = f"How do you rate the learning environment? {unique_suffix}"
    
    response = test_client.post('/feedback/student_feedback', headers=auth_header, json={
        "student_id": auth_header['student_id'],
        "feedbacks": [
            {"question": unique_question, "answer": "Very good"},
        ]
    })
    assert response.status_code == 200
    assert 'Student feedback submitted successfully' in response.json['message']
    



def test_student_feedback_get(test_client, auth_header):
    student_id = auth_header['student_id']
    response = test_client.get(f'/feedback/student_feedback/{student_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Feedback retrieved successfully' in response.json['message']

def test_student_feedback_activate(test_client, auth_header):
    
    response = test_client.put(f'/feedback/student_activate/{seed_ids['student_feedback_id']}', headers=auth_header)
    assert response.status_code == 200
    assert 'Student Feedback activated successfully' in response.json['message']

def test_student_feedback_deactivate(test_client, auth_header):
   
    response = test_client.put(f'/feedback/student_deactivate/{seed_ids['student_feedback_id']}', headers=auth_header)
    assert response.status_code == 200
    assert 'Student Feedback deactivated successfully' in response.json['message']

def test_feedback_activate(test_client, auth_header):
    
    response = test_client.put(f'/feedback/activate/{seed_ids['feedback_id']}', headers=auth_header)
    assert response.status_code == 200
    assert 'Feedback activated successfully' in response.json['message']

def test_feedback_deactivate(test_client, auth_header):
    print(seed_ids['feedback_id'])
    response = test_client.put(f'/feedback/deactivate/{seed_ids['feedback_id']}', headers=auth_header)
    assert response.status_code == 200
    assert 'Feedback deactivated successfully' in response.json['message']


def test_student_feedback_missing_student_id(test_client, auth_header):
    # Test missing student_id
    response = test_client.post('/feedback/student_feedback', json={
  "student_id": 0,
  "feedbacks": [
    {
      "question": faker.word(),
      "answer": faker.word()
    }
  ]
}
        
    , headers=auth_header)
    
    # assert response.status_code == 404
    print(response.data) 
    assert response.json['message'] == 'Please provide student_id and feedbacks'
    
def test_student_feedback_missing_feedbacks(test_client, auth_header):
    # Test missing feedbacks
    response = test_client.post('/feedback/student_feedback', json={
  "student_id": 0,
  "feedbacks": [
    
  ]
}, headers=auth_header)
    
    # assert response.status_code == 404
    print(response.data) 
    assert response.json['message'] == 'Please provide student_id and feedbacks'

def test_student_feedback_missing_question(test_client, auth_header):
    # Test feedback entry missing question
    response = test_client.post('/feedback/student_feedback', json={
  "student_id": auth_header['student_id'],
  "feedbacks": [
    {
      "question": "",
      "answer": "string"
    }
  ]
}, headers=auth_header)
    
    print(response.data) 
    assert response.json['message'] == 'Each feedback entry must include a question'



def test_student_feedback_empty_answer(test_client, auth_header):
    # Test feedback entry with empty answer (still should succeed)
    response = test_client.post('/feedback/student_feedback', json={
  "student_id": auth_header['student_id'],
  "feedbacks": [
    {
      "question": "string",
      "answer": ""
    }
  ]
}, headers=auth_header)

    # assert response.status_code == 404
    print(response.data) 
    assert response.json['message'] == 'Student feedback submitted successfully'

# Test for adding feedback with missing question and options
def test_feedback_add_missing_fields(test_client, auth_header):
    response = test_client.post('/feedback/add', json={}, headers=auth_header)
    
    assert response.is_json
    assert response.json['message'] == 'Please provide question and options'


# Test for successfully adding feedback
 # Verify the creator is the current user


# Test for adding feedback with only a question
def test_feedback_add_only_question(test_client, auth_header):
    response = test_client.post('/feedback/add', json={'question': 'What do you think?'}, headers=auth_header)
   
    assert response.is_json
    assert response.json['message'] == 'Please provide question and options'
