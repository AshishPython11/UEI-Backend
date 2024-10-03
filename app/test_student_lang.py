import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.student import LanguageKnown,StudentLogin,LanguageMaster
from app.models.log import LoginLog
from faker import Faker
import random

faker = Faker()

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
              # Seed data once for the module
        yield testing_client
        with app.app_context():
            cleanup_seed_data()  # Cleanup after all tests
            db.session.remove()

@pytest.fixture
def auth_header(test_client):
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

def seed_data(student_id):
    # Create a language in LanguageMaster
    language_master = LanguageMaster(
        language_name=faker.word()  # Adjust as per your LanguageMaster model's fields
    )
    db.session.add(language_master)
    db.session.commit()

    # Proceed with the student login
    student_login = StudentLogin.query.filter_by(student_id=student_id).first()
    if not student_login:
        raise ValueError("Student login with userid '1' not found")

    student_id = student_login.student_id
    
    # Create a single LanguageKnown record
    language_known = LanguageKnown(
        student_id=student_id,
        language_id=language_master.language_id,  # Use the newly created language_id
        proficiency=faker.word(),
        is_active=1,
        created_by='1'
    )
    db.session.add(language_known)
    db.session.commit()

    return {
        'student_id':student_id,
        'language_known_id': language_known.language_known_id,
        'language_master_id': language_master.language_id  # Returning the language_master_id for cleanup
    }

    # First, create a language in LanguageMaster
    

def cleanup_seed_data():
    
    student_id = seed_ids['student_id']
    
    # Delete related entries in tbl_login_log
    LoginLog.query.filter_by(student_id=student_id).delete()

    # Delete related entries in tbl_admin_language_known
    LanguageKnown.query.filter_by(student_id=student_id).delete()
    
    LanguageMaster.query.filter_by(language_id=seed_ids['language_master_id']).delete()
    # Finally, delete the AdminLogin entry
    user_to_delete = StudentLogin.query.filter_by(student_id=student_id).first()
    if user_to_delete:
        db.session.delete(user_to_delete)

    # Commit all deletions
    db.session.commit()
    # Cleanup the specific LanguageKnown record created
    # LanguageKnown.query.filter_by(language_known_id=seed_ids['language_known_id']).delete()
    # db.session.commit()

    # # Cleanup the specific LanguageMaster record created
    # LanguageMaster.query.filter_by(language_id=seed_ids['language_master_id']).delete()
    # db.session.commit()


def test_language_known_list(test_client, auth_header):
    response = test_client.get('/student_language_known/list', headers=auth_header)
    assert response.status_code == 200
    assert 'Student Language Known found Successfully' in response.json['message']

def test_language_known_all_data(test_client, auth_header):
    response = test_client.get('/student_language_known/alldata', headers=auth_header)
    assert response.status_code == 200
    assert 'Student Language Known found Successfully' in response.json['message']

def test_language_known_add(test_client, auth_header):
    response = test_client.post('/student_language_known/add', headers=auth_header, json={
        "student_id": auth_header['student_id'],  # Fix key here
        "language_id": seed_ids['language_known_id'],  # Use first seeded ID
        "proficiency": faker.word()
    })
    assert response.status_code == 200
    assert 'Student language Known created successfully' in response.json['message']

def test_language_known_edit(test_client, auth_header):
    record_id = seed_ids['language_known_id']  # Use the first seeded ID
    response = test_client.put(f'/student_language_known/edit/{record_id}', headers=auth_header, json={
        "student_id": auth_header['student_id'],  # Fix key here
        "language_id": seed_ids['language_known_id'],  # Use first seeded ID
        "proficiency": faker.word()
    })
    assert response.status_code == 200
    assert 'Student language Known updated successfully' in response.json['message']

def test_language_known_get(test_client, auth_header):
    record_id = auth_header['student_id']# Use the first seeded ID
    response = test_client.get(f'/student_language_known/edit/{record_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Student language Known found Successfully' in response.json['message']

def test_language_known_delete(test_client, auth_header):
    record_id = seed_ids['language_known_id'] # Use the first seeded ID
    response = test_client.delete(f'/student_language_knowndelete/{record_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Student language Known deleted successfully' in response.json['message']

def test_language_known_activate(test_client, auth_header):
    record_id = seed_ids['language_known_id']  # Use the first seeded ID
    response = test_client.put(f'/student_language_known/activate/{record_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Student language Known activated successfully' in response.json['message']

def test_language_known_deactivate(test_client, auth_header):
    record_id = seed_ids['language_known_id'] # Use the first seeded ID
    response = test_client.put(f'/student_language_known/deactivate/{record_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Student language Known deactivated successfully' in response.json['message']


def test_student_multiple_language_known_add(test_client, auth_header):
    # Prepare a payload with multiple languages
    languages_payload = [
        {
            "student_id": str(auth_header['student_id']),
            "language_id": str(seed_ids['language_known_id']),  # Use the first seeded ID
            "proficiency": faker.word()
        },
        {
            "student_id": str(auth_header['student_id']),
            "language_id": str(seed_ids['language_known_id']),  # Reuse for testing
            "proficiency": faker.word()
        }
    ]
    
    response = test_client.post('/student_language_known/multiple/add', headers=auth_header, json={
        "languages": languages_payload
    })
    assert response.status_code == 200
    
 

def test_student_multiple_language_known_edit(test_client, auth_header):
    # Prepare a payload to edit the existing language known
    languages_payload = [
        {
            "id": str(seed_ids['language_known_id']),  # Existing record
            "student_id": str(auth_header['student_id']),
            "language_id": str(seed_ids['language_known_id']),  # Reuse for testing
            "proficiency": faker.word()
        }
    ]
    
    response = test_client.put('/student_language_known/multiple_language/edit', headers=auth_header, json={
        "languages": languages_payload
    })
    assert response.status_code == 200
    # assert 'Student Languages Updated successfully' in response.json[-1]['message']
     # One for success message



def test_add_student_language_missing_student_id(test_client, auth_header):
    response = test_client.post(
        '/student_language_known/add',
        json={
            'language_id': seed_ids['language_master_id'],
            'proficiency': 'Fluent'
        },
        headers=auth_header
    )

    assert response.json['message'] == 'Please Provide Student Id'
   

def test_add_student_language_missing_language_id(test_client, auth_header):
    response = test_client.post(
        '/student_language_known/add',
        json={
            'student_id': auth_header['student_id'],
            'proficiency': 'Fluent'
        },
        headers=auth_header
    )

    assert response.json['message'] == 'Please Provide Language Id'
   

def test_add_student_language_missing_proficiency(test_client, auth_header):
    response = test_client.post(
        '/student_language_known/add',
        json={
            'student_id': auth_header['student_id'],
            'language_id': seed_ids['language_master_id']
        },
        headers=auth_header
    )

    assert response.json['message'] == 'Please Provide Proficiency'
   
def test_edit_multiple_languages_payload_not_array(test_client, auth_header):
    response = test_client.put(
        '/student_language_known/multiple_language/edit',
        json={"languages": "not an array"},
        headers=auth_header
    )

    assert response.is_json
    # assert response.status_code == 400
    assert response.json['message'] == 'Input payload validation failed' 










def test_edit_student_language_known_missing_student_id(test_client, auth_header):
    response = test_client.put(f'/student_language_known/edit/{seed_ids['language_known_id']}', json={
        'language_id': seed_ids['language_master_id'],
        'proficiency': 'Fluent'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Student Id'


def test_edit_student_language_known_missing_language_id(test_client, auth_header):
    response = test_client.put(f'/student_language_known/edit/{seed_ids['language_known_id']}', json={
        'student_id': auth_header['student_id'],
        'proficiency': 'Fluent'
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Language Id'


def test_edit_student_language_known_missing_proficiency(test_client, auth_header):
    response = test_client.put(f'/student_language_known/edit/{seed_ids['language_known_id']}', json={
        'student_id': auth_header['student_id'],
        'language_id': seed_ids['language_master_id']
    }, headers=auth_header)

    assert response.json['message'] == 'Please Provide Proficiency'


def test_edit_student_multiple_language_known_missing_record_id(test_client, auth_header):
    response = test_client.put('/student_language_known/multiple_language/edit', json={
        'languages': [
            {
                'student_id': auth_header['student_id'],
                'language_id': seed_ids['language_master_id'],
                'proficiency': 'Fluent'
            }
        ]
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Input payload validation failed'


def test_edit_student_multiple_language_known_missing_student_id(test_client, auth_header):
    response = test_client.put('/student_language_known/multiple_language/edit', json={
        'languages': [
            {
                'id': 1,
                'language_id': seed_ids['language_master_id'],
                'proficiency': 'Fluent'
            }
        ]
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Input payload validation failed'


def test_edit_student_multiple_language_known_missing_language_id(test_client, auth_header):
    response = test_client.put('/student_language_known/multiple_language/edit', json={
        'languages': [
            {
                'id': 1,
                'student_id': auth_header['student_id'],
                'proficiency': 'Fluent'
            }
        ]
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Input payload validation failed'


def test_edit_student_multiple_language_known_missing_proficiency(test_client, auth_header):
    response = test_client.put('/student_language_known/multiple_language/edit', json={
        'languages': [
            {
                'id': 1,
                'student_id': auth_header['student_id'],
                'language_id': seed_ids['language_master_id']
            }
        ]
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Input payload validation failed'


def test_edit_student_multiple_language_known_invalid_payload(test_client, auth_header):
    response = test_client.put('/student_language_known/multiple_language/edit', json={
        'languages': 'invalid_payload'  # not a list
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Input payload validation failed'


def test_add_student_multiple_language_known_missing_record_id(test_client, auth_header):
    response = test_client.post('/student_language_known/multiple/add', json={
        'languages': [
            {
                'student_id': auth_header['student_id'],
                'language_id': seed_ids['language_master_id'],
                'proficiency': 'Fluent'
            }
        ]
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Input payload validation failed'


def test_add_student_multiple_language_known_missing_student_id(test_client, auth_header):
    response = test_client.post('/student_language_known/multiple/add', json={
        'languages': [
            {
                'id': 1,
                'language_id': seed_ids['language_master_id'],
                'proficiency': 'Fluent'
            }
        ]
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Input payload validation failed'


def test_add_student_multiple_language_known_missing_language_id(test_client, auth_header):
    response = test_client.post('/student_language_known/multiple/add', json={
        'languages': [
            {
                'id': 1,
                'student_id': auth_header['student_id'],
                'proficiency': 'Fluent'
            }
        ]
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Input payload validation failed'


def test_add_student_multiple_language_known_missing_proficiency(test_client, auth_header):
    response = test_client.post('/student_language_known/multiple/add', json={
        'languages': [
            {
                'id': 1,
                'student_id': auth_header['student_id'],
                'language_id': seed_ids['language_master_id']
            }
        ]
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Input payload validation failed'


def test_add_student_multiple_language_known_invalid_payload(test_client, auth_header):
    response = test_client.post('/student_language_known/multiple/add', json={
        'languages': 'invalid_payload'  # not a list
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Input payload validation failed'

def test_language_known_edit_invalid(test_client, auth_header):
     # Use the first seeded ID
    response = test_client.put('/student_language_known/edit/8885695', headers=auth_header, json={
        "student_id": auth_header['student_id'],  # Fix key here
        "language_id": seed_ids['language_known_id'],  # Use first seeded ID
        "proficiency": faker.word()
    })
    assert response.status_code == 200
    assert 'Student language Known not found' in response.json['message']

def test_language_known_get_invalid(test_client, auth_header):
    # Use the first seeded ID
    response = test_client.get('/student_language_known/edit/8885695', headers=auth_header)
  
    assert 'Student language Known not found' in response.json['message']

def test_language_known_delete_invalid(test_client, auth_header):
     # Use the first seeded ID
    response = test_client.delete('/student_language_knowndelete/8889659', headers=auth_header)
    
    assert 'Student language Known not found' in response.json['message']

def test_language_known_activate_invalid(test_client, auth_header):
 # Use the first seeded ID
    response = test_client.put('/student_language_known/activate/8889659', headers=auth_header)

    assert 'Student language Known not found' in response.json['message']

def test_language_known_deactivate_invalid(test_client, auth_header):
     # Use the first seeded ID
    response = test_client.put('/student_language_known/deactivate/8896598', headers=auth_header)
    
    assert 'Student language Known not found' in response.json['message']