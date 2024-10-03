import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.log import *
from app.models.student import ClassMaster,CourseMaster,NewStudentAcademicHistory,StudentLogin
from app.models.adminuser import Institution
import time
import random
from faker import Faker
import uuid
faker = Faker()

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
    unique_email = f"{faker.unique.email().split('@')[0]}_{random.randint(1000, 9999)}@example.com"

    signup_response = test_client.post('/auth/signup', json={
        "userid": unique_email,  
        "password": "password",  
        "user_type": "student"
    })

    assert signup_response.status_code == 200, f"Signup failed with status code {signup_response.status_code}"
    assert signup_response.json['status'] == 200, f"Signup error: {signup_response.json['message']}"

    login_response = test_client.post('/auth/login', json={
        "userid": unique_email, 
        "password": "password", 
        "user_type": "student"
    })

    assert login_response.status_code == 200, f"Login failed with status code {login_response.status_code}"


    
    data = login_response.json
    if 'token' not in data:
        pytest.fail(f"Login response missing 'token': {data}")
    
    access_token = data['token']
    student_id = data['data']['id'] 
    global seed_ids
    seed_ids = seed_data(student_id) 
    yield {'Authorization': access_token, 'student_id': student_id}
    cleanup_seed_data()

    user_to_delete = StudentLogin.query.filter_by(userid=unique_email).first()
    if user_to_delete:
 
        db.session.query(LoginLog).filter_by(student_id=user_to_delete.student_id).delete()

        db.session.delete(user_to_delete)

        db.session.commit()
def seed_data(student_id):
 
    student_login = StudentLogin.query.filter_by(student_id=student_id).first()
    if not student_login:
        raise ValueError("Admin login with userid 'admin123' not found")
    student_id=student_login.student_id
    institution = Institution(institution_name=f'{faker.unique.company()}-{uuid.uuid4()}', is_active=1)
    course = CourseMaster(course_name=f'{faker.unique.word()}-{uuid.uuid4()}', is_active=1)
    class_master = ClassMaster(class_name=f'{faker.unique.word()}-{uuid.uuid4()}', is_active=True)
    
    db.session.add(institution)
    db.session.add(course)
    db.session.add(class_master)
    db.session.commit()

    academic_history = NewStudentAcademicHistory(
        student_id=student_id, 
        institution_type='School',
        board='CBSE',
        state_for_stateboard='State A',
        institute_id=institution.institution_id,
        course_id=course.course_id,
        class_id=class_master.class_id,
        year_or_semester='2023',
        created_by=student_id, 
        updated_by=student_id,
        learning_style='Visual'
    )
    
    db.session.add(academic_history)
    db.session.commit()

    return {
        'institution_id': institution.institution_id,
        'course_id': course.course_id,
        'class_id': class_master.class_id,
        'academic_history_id': academic_history.id
    }
def cleanup_seed_data():
   
    NewStudentAcademicHistory.query.filter_by(class_id=seed_ids['class_id']).delete()

    ClassMaster.query.filter_by(class_id=seed_ids['class_id']).delete()

    CourseMaster.query.filter_by(course_id=seed_ids['course_id']).delete()

    Institution.query.filter_by(institution_id=seed_ids['institution_id']).delete()
    
    db.session.commit()


def test_list_student_academic_histories(test_client, auth_header):
    response = test_client.get('/new_student_academic_history/list', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 200
    assert isinstance(data['data'], list)



def test_add_academic_history(test_client, auth_header):
    new_history = {
        'student_id': auth_header['student_id'],
        'institution_type': 'School',
        'board': 'CBSE',
        'state_for_stateboard': 'State',
        'institute_id': seed_ids['institution_id'],
        'course_id': seed_ids['course_id'],
        'class_id': seed_ids['class_id'],
        'year': '2023',
        'learning_style': 'Visual'
    }
    response = test_client.post('/new_student_academic_history/add', headers=auth_header, json=new_history)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Academic History created successfully'



def test_add_multiple_academic_histories(test_client, auth_header):
    histories = {
        'histories': [
            {
                'student_id': str(auth_header['student_id']), 
                'institution_type': 'College',
                'board': 'ICSE',
                'state_for_stateboard': 'State',
                'institute_id': str(seed_ids['institution_id']), 
                'course_id': str(seed_ids['course_id']),  
                'class_id': str(seed_ids['class_id']),  
                'year': '2023',
                'learning_style': 'Auditory'
            },
            {
                'student_id': str(auth_header['student_id']), 
                'institution_type': 'School',
                'board': 'CBSE',
                'state_for_stateboard': 'State',
                'institute_id': str(seed_ids['institution_id']),  
                'course_id': str(seed_ids['course_id']),  
                'class_id': str(seed_ids['class_id']),  
                'year': '2024',
                'learning_style': 'Visual'
            }
        ]
    }
    response = test_client.post('/new_student_academic_history/multiple_academic_history/add', headers=auth_header, json=histories)
    
    # Debugging output
    print(response.status_code)
    print(response.get_json())

    assert response.status_code == 200

def test_edit_multiple_academic_histories(test_client, auth_header):
    histories = {     
        'histories': [
            {
                'id': seed_ids['academic_history_id'],  
                'student_id': str(auth_header['student_id']),  
                'institution_type': 'College',
                'board': 'ICSE',
                'state_for_stateboard': 'State',
                'institute_id': str(seed_ids['institution_id']),  
                'course_id': str(seed_ids['course_id']),  
                'class_id': str(seed_ids['class_id']),  
                'year': '2023',
                'learning_style': 'Auditory'
            },
            {
                'id': seed_ids['academic_history_id'],  
                'student_id': str(auth_header['student_id']),  
                'institution_type': 'School',
                'board': 'CBSE',
                'state_for_stateboard': 'State',
                'institute_id': str(seed_ids['institution_id']),
                'course_id': str(seed_ids['course_id']),
                'class_id': str(seed_ids['class_id']),
                'year': '2024',
                'learning_style': 'Visual'
            }
        ]
    }
    response = test_client.put('/new_student_academic_history/multiple_academic_history/edit', headers=auth_header, json=histories)
    
   
    print(response.get_data(as_text=True))  
    assert response.status_code == 200



def test_edit_academic_history(test_client, auth_header):
    academic_history_id = seed_ids['academic_history_id'] 
    updated_data = {
        'student_id': str(auth_header['student_id']),
        'institution_type': 'School',
        'board': 'CBSE',
        'state_for_stateboard': 'Updated State',
        'institute_id': str(seed_ids['institution_id']), 
        'course_id': str(seed_ids['course_id']),  
        'learning_style': 'Visual',
        'class_id': str(seed_ids['class_id']),
        'year': '2023'
    }
    response = test_client.put(f'/new_student_academic_history/edit/{academic_history_id}', headers=auth_header, json=updated_data)
    assert response.status_code == 200
    
    data = response.get_json()
    print(data)
    assert data['message'] == 'Academic History updated successfully'

def test_get_academic_history(test_client, auth_header):
    student_id=auth_header['student_id']
    response = test_client.get(f'/new_student_academic_history/get/{student_id}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 200
    assert isinstance(data['data'], list)

def test_delete_academic_history(test_client, auth_header):
    academic_history_id = seed_ids['academic_history_id'] 
    response = test_client.delete(f'/new_student_academic_history/delete/{academic_history_id}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Academic History deleted successfully'

def test_activate_academic_history(test_client, auth_header):
    academic_history_id = seed_ids['academic_history_id'] 
    response = test_client.put(f'/new_student_academic_history/activate/{academic_history_id}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Academic History activated successfully'

def test_deactivate_academic_history(test_client, auth_header):
    academic_history_id = seed_ids['academic_history_id'] 
    response = test_client.put(f'/new_student_academic_history/deactivate/{academic_history_id}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Academic History deactivated successfully'

def test_add_academic_history_missing_student_id(test_client, auth_header):
    response = test_client.post('/new_student_academic_history/add', json={
        'institution_type': 'School',
        'board': 'CBSE',
        'state_for_stateboard': 'State',
        'class_id': seed_ids['class_id'],
        'year': '2024',
        'institute_id': seed_ids['institution_id'],
        'course_id': seed_ids['course_id'],
        'learning_style': 'Visual'
    }, headers=auth_header)

    assert response.json['message'] == "'student_id'"
    


def test_add_academic_history_missing_institution_type(test_client, auth_header):
    response = test_client.post('/new_student_academic_history/add', json={
        'student_id':  auth_header['student_id'],
        'board': 'CBSE',
        'state_for_stateboard': 'State',
        'class_id': seed_ids['class_id'],
        'year': '2024',
        'institute_id': seed_ids['institution_id'],
        'course_id': seed_ids['course_id'],
        'learning_style': 'Visual'
    }, headers=auth_header)

    assert response.json['message'] == "'institution_type'"
    


def test_add_academic_history_invalid_class_id(test_client, auth_header):
    response = test_client.post('/new_student_academic_history/add', json={
        'student_id': auth_header['student_id'],
        'institution_type': 'School',
        'board': 'CBSE',
        'state_for_stateboard': 'State',
        'class_id': 'invalid_id',  # Invalid class ID
        'year': '2024',
        'institute_id': seed_ids['institution_id'],
        'course_id': seed_ids['course_id'],
        'learning_style': 'Visual'
    }, headers=auth_header)
    print(response.data)
    assert response.json['message'] == 'invalid literal for int() with base 10: \'invalid_id\''
    

def test_add_academic_history_missing_student_id(test_client, auth_header):
    response = test_client.put(f'/new_student_academic_history/edit/{auth_header['student_id']}', json={
        'institution_type': 'School',
        'board': 'CBSE',
        'state_for_stateboard': 'State',
        'class_id': seed_ids['class_id'],
        'year': '2024',
        'institute_id': seed_ids['institution_id'],
        'course_id': seed_ids['course_id'],
        'learning_style': 'Visual'
    }, headers=auth_header)

    assert response.json['message'] == "Input payload validation failed"
    


def test_add_academic_history_missing_institution_type(test_client, auth_header):
    response = test_client.put(f'/new_student_academic_history/edit/{auth_header['student_id']}', json={
        'student_id':  auth_header['student_id'],
        'board': 'CBSE',
        'state_for_stateboard': 'State',
        'class_id': seed_ids['class_id'],
        'year': '2024',
        'institute_id': seed_ids['institution_id'],
        'course_id': seed_ids['course_id'],
        'learning_style': 'Visual'
    }, headers=auth_header)

    assert response.json['message'] == "Input payload validation failed"
    


def test_add_academic_history_invalid_class_id(test_client, auth_header):
    response = test_client.put(f'/new_student_academic_history/edit/{auth_header['student_id']}', json={
        'student_id': auth_header['student_id'],
        'institution_type': 'School',
        'board': 'CBSE',
        'state_for_stateboard': 'State',
        'class_id': 'invalid_id',  
        'year': '2024',
        'institute_id': seed_ids['institution_id'],
        'course_id': seed_ids['course_id'],
        'learning_style': 'Visual'
    }, headers=auth_header)
    print(response.data)
    assert response.json['message'] == 'Input payload validation failed'
 
def test_edit_academic_history_invalid(test_client, auth_header):
    
    updated_data = {
        'student_id': str(auth_header['student_id']),
        'institution_type': 'School',
        'board': 'CBSE',
        'state_for_stateboard': 'Updated State',
        'institute_id': str(seed_ids['institution_id']), 
        'course_id': str(seed_ids['course_id']),  
        'learning_style': 'Visual',
        'class_id': str(seed_ids['class_id']),
        'year': '2023'
    }
    response = test_client.put('/new_student_academic_history/edit/8856598', headers=auth_header, json=updated_data)
 
    
    data = response.get_json()
   
    assert data['message'] == 'Academic History not found'

def test_get_academic_history_invalid(test_client, auth_header):
   
    response = test_client.get('/new_student_academic_history/get/8856959', headers=auth_header)
    
    data = response.get_json()
    assert data['message'] == 'Academic History not found'
  

def test_delete_academic_history_invalid(test_client, auth_header):
 
    response = test_client.delete('/new_student_academic_history/delete/88565965', headers=auth_header)
   
    data = response.get_json()
    assert data['message'] == 'Academic History not found'

def test_activate_academic_history_invalid(test_client, auth_header):
    
    response = test_client.put('/new_student_academic_history/activate/8896598', headers=auth_header)
  
    data = response.get_json()
    assert data['message'] == 'Academic History not found'

def test_deactivate_academic_history_invalid(test_client, auth_header):
    
    response = test_client.put('/new_student_academic_history/deactivate/5585968', headers=auth_header)
    
    data = response.get_json()
    assert data['message'] == 'Academic History not found'