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
        db.session.query(LoginLog).filter_by(student_id=user_to_delete.student_id).delete()
        db.session.delete(user_to_delete)
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

# def test_login_with_unregistered_email(test_client):
#     response = test_client.post('/auth/login', json={
#         "userid": "unryiuuiuuyuegistered@example.com",
#         "password": "passiuiyuword",
#         "user_type": "student"
#     })
#     data = response.get_json()
#     print(f"unregistered data{data}")
#     assert data['message'] == "User does not exist"
    



# def test_change_password_incorrect_old_password(auth_header, test_client):
#     response = test_client.post('/auth/changepassword', headers=auth_header, json={
#         "email": "student@example.com",  # Use a valid email for testing
#         "old_password": "wrongpassword",
#         "new_password": "newpassword",
#         "user_type": "student"
#     })

#     data = response.get_json()
#     assert data['message'] == "Incorrect old password"

    
# def seed_data():
#     admin_user = AdminLogin(userid=faker.unique.email(), password='admin123', is_active=1)
#     db.session.add(admin_user)
#     db.session.commit()
    
#     return {
#         'admin_id': admin_user.admin_id,
#         'userid': admin_user.userid,
#         'password':admin_user.password,
#     }

# def test_signup(test_client):
#     payload = {
#         "userid": faker.unique.email(),
#         "password": "admin123",
#         "user_type": "admin"
#     }
    
#     response = test_client.post('/auth/signup', json=payload)
#     assert response.status_code == 200
#     data = response.get_json()
#     assert 'User created successfully' in data['message']


# def test_login(test_client, auth_headers):
#     payload = {
#         "userid": seed_ids['userid'],  
#         "password":seed_ids['password'], 
#         "user_type": "admin"
#     }
    
#     response = test_client.post('/auth/login', json=payload)
#     assert response.status_code == 200
#     data = response.get_json()
#     assert 'User Logged In Successfully' in data['message']
#     assert 'token' in data


# def test_logout(test_client, auth_headers):
#     response = test_client.post('/auth/logout', headers=auth_headers['admin_auth'])
#     assert response.status_code == 200
#     data = response.get_json()
#     assert 'User logged out successfully' in data['message']


# def test_forgot_password(test_client, auth_headers):
#     payload = {
#         "email": seed_ids['userid'], 
#         "user_type": "admin"
#     }
    
#     response = test_client.post('/auth/forgotpassword', json=payload)
#     assert response.status_code == 200
#     data = response.get_json()
#     assert 'Reset password instructions sent to email' in data['message']


# def test_change_password(test_client, auth_headers):
#     payload = {
#         "email": seed_ids['userid'],   
#         "old_password": "admin123",
#         "new_password": "newpassword123",
#         "user_type": "admin"
#     }

#     response = test_client.post('/auth/changepassword', json=payload, headers=auth_headers['admin_auth'])
#     assert response.status_code == 200
#     data = response.get_json()
#     assert 'Password changed successfully' in data['message']

# def test_invalid_login(test_client):
#     payload = {
#         "userid": faker.unique.user_name(),  
#         "password": "wrongpassword",
#         "user_type": "admin"
#     }

#     response = test_client.post('/auth/login', json=payload)
#     assert response.status_code == 404
#     data = response.get_json()
#     assert 'Invalid userid or password' in data['message']

# def test_signup_existing_user(test_client, auth_headers):
#     payload = {
#         "userid": seed_ids['userid'],
#         "password": "admin123",
#         "user_type": "admin"
#     }

#     response = test_client.post('/auth/signup', json=payload)
#     assert response.status_code == 400
#     data = response.get_json()
#     assert 'Userid already exists' in data['message']
