from datetime import datetime
from faker import Faker
import pytest
from faker import Faker
from app import db,app
import random
from app.models.student import  StudentLogin, SubjectMaster,SubjectPreference,CourseMaster
from datetime import datetime
from app.models.student import StudentLogin
from app.models.log import LoginLog
import json
faker = Faker()
@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            # global seed_ids
            # seed_ids = seed_data()  # Seed once for the module
        yield testing_client
        with app.app_context():
            # cleanup_seed_data()  # Cleanup after all tests
            db.session.remove()

@pytest.fixture
def auth_headers(test_client):
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
    seed_ids = seed_data(student_id)# Extracting student ID
    yield {'Authorization': access_token, 'student_id': student_id}
    cleanup_seed_data()

    # Fetch the user to delete based on the unique email
    user_to_delete = StudentLogin.query.filter_by(userid=unique_email).first()
    if user_to_delete:
        # First delete any logs related to the user from LoginLog
        db.session.query(LoginLog).filter_by(student_id=user_to_delete.student_id).delete()

        # Delete related subject preferences before deleting the student login
        db.session.query(SubjectPreference).filter_by(student_id=user_to_delete.student_id).delete()

        # Now delete the student login itself
        db.session.delete(user_to_delete)

        # Commit the changes to reflect the deletions
        db.session.commit()

faker = Faker()

def seed_data(student_id):
    # Fetch the student login
    student_login = StudentLogin.query.filter_by(student_id=student_id).first()
    if not student_login:
        raise ValueError("Student login with userid '1' not found")

    student_id = student_login.student_id

    # Create a unique subject name
    unique_subject_name = faker.unique.word().capitalize() + " Subject"

    # Check if the subject already exists
    subject = SubjectMaster.query.filter_by(subject_name=unique_subject_name).first()
    if not subject:
        subject = SubjectMaster(
            subject_name=unique_subject_name,
            is_active=1,
            created_by=1,  # Assuming 1 is the ID of the admin user
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.session.add(subject)
        db.session.commit()

    # Create or fetch a course
    course_name = faker.unique.word().capitalize() + " Course"
    course = CourseMaster.query.filter_by(course_name=course_name).first()
    if not course:
        course = CourseMaster(
            course_name=course_name,
            is_active=1,
            created_by=1,  # Assuming 1 is the ID of the admin user
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        db.session.add(course)
        db.session.commit()

    # Create a subject preference for the student
    subject_preference = SubjectPreference(
        student_id=student_id,
        course_id=course.course_id,  # Use the ID of the created/fetched course
        subject_id=subject.subject_id,
        preference="Preferred",  # Example preference
        score_in_percentage=90,  # Example score
        is_active=1,
        created_by=1  # Assuming 1 is the ID of the admin user
    )
    db.session.add(subject_preference)
    db.session.commit()

    return {
        'subject_id': subject.subject_id,
        'subject_preference_id': subject_preference.subject_preference_id,
        'course_id': course.course_id,
        'course_name': course.course_name
    }


def cleanup_seed_data():
    # Delete related subject preferences first
    subject_preference = SubjectPreference.query.filter_by(subject_preference_id=seed_ids['subject_preference_id']).first()
    if subject_preference:
        db.session.delete(subject_preference)

    # Delete the seeded course data
    course = CourseMaster.query.filter_by(course_id=seed_ids['course_id']).first()
    if course:
        # First delete any related subject preferences for this course
        SubjectPreference.query.filter_by(course_id=course.course_id).delete()
        db.session.delete(course)

    # Delete the seeded subject data
    subject = SubjectMaster.query.filter_by(subject_id=seed_ids['subject_id']).first()
    if subject:
        db.session.delete(subject)

    # Commit the changes after all deletions
    db.session.commit()





def test_subject_preference_list(test_client,auth_headers):
    # Test case for getting active subject preferences
   # Authenticate to get JWT
    response = test_client.get('/subject_preference/list',headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 200
def test_subject_preference_alldata(test_client,auth_headers):
    # Test case for getting active subject preferences
   # Authenticate to get JWT
    response = test_client.get('/subject_preference/alldata',headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 200

def test_subject_preference_add(test_client,auth_headers):
    # Test case for adding a subject preference
  
    payload = {
        'student_id': auth_headers['student_id'],
        'course_id': seed_ids['course_id'],
        'subject_id': seed_ids['subject_id'],
        'preference': 'Math',
        'score_in_percentage': 85
    }
    response = test_client.post('/subject_preference/add', 
                           headers=auth_headers,
                           data=json.dumps(payload),
                           content_type='application/json')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Subject Preference created successfully'



def test_subject_multiple_preference_add(test_client,auth_headers):
    # Test case for adding multiple subject preferences
    
    payload = {
        'preferences': [
            {
                "id":1,
                'student_id': str(auth_headers['student_id']),
        'course_id': str(seed_ids['course_id']),
        'subject_id': str(seed_ids['subject_id']),
                'preference': 'Math',
                'score_in_percentage': 90
            },
            {
                "id":2,
               'student_id': str(auth_headers['student_id']),
        'course_id': str(seed_ids['course_id']),
        'subject_id': str(seed_ids['subject_id']),
                'preference': 'Science',
                'score_in_percentage': 80
            }
        ]
    }
    response = test_client.post('/subject_preference/multiple_subject/add',
                           headers=auth_headers,
                           data=json.dumps(payload),
                           content_type='application/json')

    assert response.status_code == 200
    data = response.get_json()
    assert data[0]['message'] == 'Subject Preferences Added successfully'
def test_subject_multiple_preference_edit(test_client,auth_headers):
    # Test case for adding multiple subject preferences
    
    payload = {
        'preferences': [
            {
                "id":seed_ids['subject_preference_id'],
                'student_id': str(auth_headers['student_id']),
        'course_id': str(seed_ids['course_id']),
        'subject_id': str(seed_ids['subject_id']),
                'preference': faker.word(),
                'score_in_percentage': 90
            },
          
        ]
    }
    response = test_client.put('/subject_preference/multiple_subject/edit',
                           headers=auth_headers,
                           data=json.dumps(payload),
                           content_type='application/json')

    assert response.status_code == 200
    data = response.get_json()
    assert data[0]['message'] == 'Subject Preferences Updated successfully'

def test_subject_preference_edit(test_client,auth_headers):
    # Test case for editing a subject preference
   
    # Assuming an entry with id=1 exists
    payload = {
       'student_id': str(auth_headers['student_id']),
        'course_id': str(seed_ids['course_id']),
        'subject_id': str(seed_ids['subject_id']),
        'preference': 'Advanced Math',
        'score_in_percentage': 95
    }
    response = test_client.put(f'/subject_preference/edit/{seed_ids['subject_preference_id']}',
                          headers=auth_headers,
                          data=json.dumps(payload),
                          content_type='application/json')

    assert response.status_code == 200
    data = response.get_json()
    # assert data['message'] == 'Subject Preference updated successfully'


def test_subject_preference_get_by_id(test_client,auth_headers):
    # Test case for editing a subject preference
   
    # Assuming an entry with id=1 exists
    
    response = test_client.get(f'/subject_preference/edit/{auth_headers['student_id']}',
                          headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Subject Preference found Successfully'

def test_subject_preference_delete(test_client,auth_headers):
    # Test case for deleting a subject preference
 
    # Assuming an entry with id=1 exists
    response = test_client.delete(f'/subject_preferencedelete/{seed_ids['subject_preference_id']}',
                             headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Student Preference deleted successfully'

def test_subject_preference_activate(test_client,auth_headers):
    # Test case for activating a subject preference
    
    # Assuming an entry with id=1 exists
    response = test_client.put(f'/subject_preference/activate/{seed_ids['subject_preference_id']}',
                          headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Subject Preference activated successfully'

def test_subject_preference_deactivate(test_client,auth_headers):
    # Test case for deactivating a subject preference
    
    # Assuming an entry with id=1 exists
    response = test_client.put(f'/subject_preference/deactivate/{seed_ids['subject_preference_id']}',
                          headers=auth_headers)

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Subject Preference deactivated successfully'

def test_subject_preference_add_missing_student_id(test_client, auth_headers):
    # Test adding subject preference without student_id
    response = test_client.post('/subject_preference/add', json={
        "course_id": seed_ids['course_id'],
        "subject_id": seed_ids['subject_id'],
        "preference": "High",
        "score_in_percentage": 85
    }, headers=auth_headers)

    assert response.is_json
    
    assert response.json['message'] == 'Please Provide Admin Id'


def test_subject_preference_add_missing_course_id(test_client, auth_headers):
    # Test adding subject preference without course_id
    response = test_client.post('/subject_preference/add', json={
        "student_id": auth_headers['student_id'],
        "subject_id": seed_ids['subject_id'],
        "preference": "High",
        "score_in_percentage": 85
    }, headers=auth_headers)

    assert response.is_json
    
    assert response.json['message'] == 'Please Provide Course Id'


def test_subject_preference_add_missing_subject_id(test_client, auth_headers):
    # Test adding subject preference without subject_id
    response = test_client.post('/subject_preference/add', json={
        "student_id": auth_headers['student_id'],
        "course_id": seed_ids['course_id'],
        "preference": "High",
        "score_in_percentage": 85
    }, headers=auth_headers)

    assert response.is_json
    
    assert response.json['message'] == 'Please Provide Subject Id'


def test_subject_preference_add_missing_preference(test_client, auth_headers):
    # Test adding subject preference without preference
    response = test_client.post('/subject_preference/add', json={
        "student_id": auth_headers['student_id'],
        "course_id": seed_ids['course_id'],
        "subject_id": seed_ids['subject_id'],
        "score_in_percentage": 85
    }, headers=auth_headers)

    assert response.is_json
    
    assert response.json['message'] == 'Please Provide Preference'


def test_subject_preference_add_missing_score_in_percentage(test_client, auth_headers):
    # Test adding subject preference without score_in_percentage
    response = test_client.post('/subject_preference/add', json={
        "student_id": auth_headers['student_id'],
        "course_id": seed_ids['course_id'],
        "subject_id": seed_ids['subject_id'],
        "preference": "High"
    }, headers=auth_headers)

    assert response.is_json
    
    assert response.json['message'] == 'Please Provide Score in percentage'
def test_multiple_subject_preference_add_with_non_array_payload(test_client, auth_headers):
    response = test_client.post('/subject_preference/multiple_subject/add', json={"preferences": "not an array"}, headers=auth_headers)
    assert response.is_json
    # assert response.status_code == 400
    assert response.json['message'] == 'Input payload validation failed'  # Adjust based on your actual validation logic
    # assert 'preferences' in response.json['errors'] 
def test_multiple_subject_preference_edit_with_non_array_payload(test_client, auth_headers):
    response = test_client.put('/subject_preference/multiple_subject/edit', json={"preferences": "not an array"}, headers=auth_headers)
    assert response.is_json
    # assert response.status_code == 400
    assert response.json['message'] == 'Input payload validation failed' 


def test_subject_preference_edit_missing_subject_preference_id(test_client, auth_headers):
    # Test editing subject preference without subject_preference_id
    response = test_client.put(f'/subject_preference/edit/{seed_ids['subject_preference_id']}', json={
        "student_id": auth_headers['student_id'],
        "course_id": seed_ids['course_id'],
        "subject_id": seed_ids['subject_id'],
        "preference": "High",
        "score_in_percentage": 85
    }, headers=auth_headers)

    assert response.is_json
    assert response.json['message'] == 'Subject Preference updated successfully'


def test_subject_preference_edit_missing_student_id(test_client, auth_headers):
    # Test editing subject preference without student_id
    response = test_client.put(f'/subject_preference/edit/{seed_ids['subject_preference_id']}', json={
        "course_id": seed_ids['course_id'],
        "subject_id": seed_ids['subject_id'],
        "preference": "High",
        "score_in_percentage": 85
    }, headers=auth_headers)

    assert response.is_json
    assert response.json['message'] == 'Please Provide Admin Id'


def test_subject_preference_edit_missing_course_id(test_client, auth_headers):
    # Test editing subject preference without course_id
    response = test_client.put(f'/subject_preference/edit/{seed_ids['subject_preference_id']}', json={
        "student_id": auth_headers['student_id'],
        "subject_id": seed_ids['subject_id'],
        "preference": "High",
        "score_in_percentage": 85
    }, headers=auth_headers)

    assert response.is_json
    assert response.json['message'] == 'Please Provide Course Id'


def test_subject_preference_edit_missing_subject_id(test_client, auth_headers):
    # Test editing subject preference without subject_id
    response = test_client.put(f'/subject_preference/edit/{seed_ids['subject_preference_id']}', json={
        "student_id": auth_headers['student_id'],
        "course_id": seed_ids['course_id'],
        "preference": "High",
        "score_in_percentage": 85
    }, headers=auth_headers)

    assert response.is_json
    assert response.json['message'] == 'Please Provide Subject Id'


def test_subject_preference_edit_missing_preference(test_client, auth_headers):
    # Test editing subject preference without preference
    response = test_client.put(f'/subject_preference/edit/{seed_ids['subject_preference_id']}', json={
        "student_id": auth_headers['student_id'],
        "course_id": seed_ids['course_id'],
        "subject_id": seed_ids['subject_id'],
        "score_in_percentage": 85
    }, headers=auth_headers)

    assert response.is_json
    assert response.json['message'] == 'Please Provide Preference'


def test_subject_preference_edit_missing_score_in_percentage(test_client, auth_headers):
    # Test editing subject preference without score_in_percentage
    response = test_client.put(f'/subject_preference/edit/{seed_ids['subject_preference_id']}', json={
        "student_id": auth_headers['student_id'],
        "course_id": seed_ids['course_id'],
        "subject_id": seed_ids['subject_id'],
        "preference": "High"
    }, headers=auth_headers)

    assert response.is_json
    assert response.json['message'] == 'Please Provide Score in percentage'

