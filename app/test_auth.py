import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.adminuser import AdminLogin
from app.models.student import StudentLogin
from app.models.log import *
from faker import Faker

faker = Faker()

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
    unique_email = faker.unique.email()

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
    user_id=data['data']['userid']  # Extracting student ID
    yield {'Authorization': access_token, 'student_id': student_id,'user_id':user_id}
    user_to_delete = StudentLogin.query.filter_by(userid=unique_email).first()
    if user_to_delete:
        db.session.query(ChangePwdLog).filter_by(student_id=user_to_delete.student_id).delete()  # Delete related logs
        db.session.query(LoginLog).filter_by(student_id=user_to_delete.student_id).delete()  # Delete login logs
        db.session.delete(user_to_delete)  # Now delete the student login
        db.session.commit()

def test_logout(auth_header, test_client):
    response = test_client.post('/auth/logout', headers=auth_header)
    # print(response)
    # print(auth_header['Authorization'])
    # print(test_client)
    assert response.status_code == 200
    data = response.get_json()
    # print(f"Data{data}")
    assert data['message'] == 'User logged out successfully'

def test_activate_student(test_client, auth_header):
    student_id = auth_header['user_id']  # Use an existing student ID for testing
    response = test_client.put(f'/auth/activate/{student_id}', headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'User activated successfully'



def test_deactivate_student(test_client, auth_header):
    student_id = auth_header['user_id']  # Use an existing student ID for testing
    response = test_client.put(f'/auth/deactivate/{student_id}', headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'User deactivated successfully'
def test_forgot_password_without_mail_setup(test_client, auth_header):
    # Extracting user_id from the header for the logged-in student
    user_email = auth_header['user_id']
    print(user_email)
    response = test_client.post('/auth/forgotpassword', json={
        'email': user_email,
        'user_type': 'student'
    })

    assert response.status_code == 200
    assert response.json['message'] == 'Failed to send reset password email'

def test_change_password(test_client, auth_header):
    user_email = auth_header['user_id']
    
    # Change the password
    response = test_client.post('/auth/changepassword', json={
        'email': user_email,
        'old_password': 'password',  # Original password
        'new_password': 'newpassword123',  # New password
        'user_type': 'student'
    })

    assert response.status_code == 200
    assert response.json['message'] == 'Password changed successfully'

    # Now try to log in with the new password
    login_response = test_client.post('/auth/login', json={
        'userid': user_email,
        'password': 'newpassword123',  # New password
        'user_type': 'student'
    })
    
    assert login_response.status_code == 200

def test_reset_password(test_client, auth_header):
    user_email = auth_header['user_id']
    
    response = test_client.post('/auth/resetpassword', json={
        'email': user_email,
        'new_password': 'resetpassword123',  # New password
        'conf_password': 'resetpassword123',  # Confirm password
        'user_type': 'student'
    })

    assert response.status_code == 200
    assert response.json['message'] == 'Password changed successfully'

    # Optional: Log in with the reset password to verify
    login_response = test_client.post('/auth/login', json={
        'userid': user_email,
        'password': 'resetpassword123',  # Use reset password
        'user_type': 'student'
    })
    
    assert login_response.status_code == 200
# import pytest
# from unittest.mock import patch
# from flask import jsonify

# def test_forgot_password_success(test_client, auth_header):
#     user_email = auth_header['user_id']  # Use a registered email for testing
    
#     # Mock the send_reset_email method to avoid sending actual emails
#     with patch('app.controllers.auth_controller.AuthController.ForgotPassword.send_reset_email') as mock_send_reset_email:
#         mock_send_reset_email.return_value = None  # Mocked method does nothing
        
#         response = test_client.post('/auth/forgotpassword', json={
#             'email': user_email,
#             'user_type': 'student'
#         })
        
#         assert response.status_code == 200
#         assert response.json['message'] == 'Reset password instructions sent to email'

