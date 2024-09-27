import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.student import Contact, StudentAddress, Student, ClassMaster,CourseMaster,NewStudentAcademicHistory,StudentLogin
from faker import Faker
import random
from app.models.adminuser import Institution
from app.models.log import *
from datetime import datetime
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
             # Cleanup after all tests
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
    cleanup_seed_data()

    # Fetch the user to delete based on the unique email
    user_to_delete = StudentLogin.query.filter_by(userid=unique_email).first()
    if user_to_delete:
        # First, delete any logs related to the user from LoginLog
        db.session.query(LoginLog).filter_by(student_id=user_to_delete.student_id).delete()

        # Delete any addresses related to the user from tbl_student_address
        # db.session.query(Contact).filter_by(student_id=user_to_delete.student_id).delete()

        # Delete related subject preferences before deleting the student login
        

        # Now delete the student login itself
        db.session.delete(user_to_delete)

        # Commit the changes to reflect the deletions
        db.session.commit()

def seed_data(student_id):
    student_login = StudentLogin.query.filter_by(student_id=student_id).first()
    if not student_login:
        raise ValueError("Student login with userid '1' not found")

    # Create a student
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

    # Create a contact
    contact = Contact(
        student_id=student_id,
        mobile_isd_call=faker.phone_number(),
        mobile_no_call=faker.phone_number(),
        mobile_isd_watsapp=faker.phone_number(),
        mobile_no_watsapp=faker.phone_number(),
        email_id=faker.email(),
        is_active=1
    )
    db.session.add(contact)
    
    # Create an address
    student_address = StudentAddress(
        student_id=student_id,
        address1=faker.address(),
        address2=faker.address(),
        country=faker.country(),
        state=faker.state(),
        city=faker.city(),
        district=faker.city(),
        pincode=faker.postcode(),
        address_type=faker.word(),
        is_active=1,
        created_by=student_id  # Assuming 'admin' is the admin ID or email
    )
    db.session.add(student_address)
    institution = Institution(institution_name=faker.unique.company(), is_active=1)
    course = CourseMaster(course_name=faker.unique.word(), is_active=1)
    class_master = ClassMaster(class_name=faker.unique.word(), is_active=True)
    
    db.session.add(institution)
    db.session.add(course)
    db.session.add(class_master)
    db.session.commit()
    
    # Create academic history
    academic_history = NewStudentAcademicHistory(
        student_id=student_id,  # Assuming a valid student ID exists
        institution_type='School',
        board='CBSE',
        state_for_stateboard='State A',
        institute_id=institution.institution_id,
        course_id=course.course_id,
        class_id=class_master.class_id,
        year_or_semester='2023',
        created_by=student_id,  # Replace with the admin ID as needed
        updated_by=student_id,
        learning_style='Visual'
    )
    
    db.session.add(academic_history)
    
    db.session.commit()

    return {
        'student_id': student_id,
        'contact_id': contact.contact_id,  # Assuming contact has an ID field
        'address_id': student_address.address_id,  # Assuming address has an ID field
        'academic_history_id': academic_history.id   # Returning the student ID
    }

def cleanup_seed_data():
    # Cleanup the seeded profile data
    Student.query.filter_by(student_login_id=seed_ids['student_id']).delete()
    Contact.query.filter_by(student_id=seed_ids['student_id']).delete()
    StudentAddress.query.filter_by(student_id=seed_ids['student_id']).delete()
    NewStudentAcademicHistory.query.filter_by(student_id=seed_ids['student_id']).delete()
    db.session.commit()

def test_check_profile_complete(test_client, auth_header):
    response = test_client.get('/profile/check_profile', headers=auth_header)
    assert response.status_code == 200
    

# def test_check_profile_incomplete(test_client, auth_header):
#     # Modify data to make the profile incomplete
#     student = Student.query.first()
#     student.guardian_name = None
#     db.session.commit()

#     response = test_client.get('/profile/check_profile', headers=auth_header)
#     assert response.status_code == 400
    
