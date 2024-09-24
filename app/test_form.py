import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.role import FormMasterData, MenuMasterData, SubMenuMasterData
from app.models.student import StudentLogin
from app.models.log import LoginLog

import time
from faker import Faker

faker = Faker()

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            global seed_ids
            seed_ids = seed_data()  # Seed once for the module
        yield testing_client
        with app.app_context():
            cleanup_seed_data()  # Cleanup after all tests
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
    student_id = data['data']['id']  # Extracting student ID
    yield {'Authorization': access_token, 'student_id': student_id}
    user_to_delete = StudentLogin.query.filter_by(userid=unique_email).first()
    if user_to_delete:
        db.session.query(LoginLog).filter_by(student_id=user_to_delete.student_id).delete()
        db.session.delete(user_to_delete)
        db.session.commit()

def seed_data():
    """Seeds random data for testing."""
    # Seed menu data
    menu = MenuMasterData(
        menu_name=faker.word(),
        priority=faker.random_int(min=1, max=100),
        created_by=faker.random_int(min=1, max=1000),  # Use a random integer for created_by
        updated_by=faker.random_int(min=1, max=1000),
        is_active=1
    )
    db.session.add(menu)
    db.session.commit()

    # Seed submenu data
    submenu = SubMenuMasterData(
        menu_master_id=menu.menu_master_id,
        menu_name=faker.word(),
        priority=faker.random_int(min=1, max=100),
        created_by=faker.random_int(min=1, max=1000),  # Use a random integer for created_by
    updated_by=faker.random_int(min=1, max=1000),
        is_active=1
    )
    db.session.add(submenu)
    db.session.commit()

    # Seed form data
    form = FormMasterData(
        form_name=faker.word(),
        menu_master_id=menu.menu_master_id,
        sub_menu_master_id=submenu.submenu_master_id,
        form_url=faker.url(),
        form_description=faker.sentence(),
        is_menu_visible=True,
        is_active=1,
        created_by=faker.random_int(min=1, max=1000),  # Use a random integer for created_by
    
    )
    db.session.add(form)
    db.session.commit()

    return {
        'form_master_id': form.form_master_id,
        'menu_master_id': menu.menu_master_id,
        'submenu_master_id': submenu.submenu_master_id
    }

def cleanup_seed_data():
    """Cleanup the seeded data after the tests."""
    # Delete dependent records first
    form_records = FormMasterData.query.filter_by(sub_menu_master_id=seed_ids['submenu_master_id']).all()
    for form in form_records:
        db.session.delete(form)
    db.session.commit()  # Commit the deletion of dependent records

    # Now delete the submenu
    submenu = SubMenuMasterData.query.filter_by(submenu_master_id=seed_ids['submenu_master_id']).first()
    if submenu:
        db.session.delete(submenu)
        db.session.commit()

    # Delete the form master if it exists
    form = FormMasterData.query.filter_by(form_master_id=seed_ids['form_master_id']).first()
    if form:
        db.session.delete(form)
        db.session.commit()

    # Finally, delete the menu
    menu = MenuMasterData.query.filter_by(menu_master_id=seed_ids['menu_master_id']).first()
    if menu:
        db.session.delete(menu)
        db.session.commit()


def test_form_list(test_client, auth_header):
    """Test listing forms"""
    response = test_client.get('/form/list', headers=auth_header)
    assert response.status_code == 200
    


def test_form_add(test_client, auth_header):
    """Test adding a form with random data"""
    data = {
        'form_name': faker.word(),
        'menu_master_id': seed_ids['menu_master_id'],
        'sub_menu_master_id': seed_ids['submenu_master_id'],
        'form_url': faker.url(),
        'form_description': faker.sentence(),
        'is_menu_visible': True
    }

    response = test_client.post('/form/add', headers=auth_header, json=data)
    
    assert response.status_code == 200

def test_form_edit(test_client, auth_header):
    """Test editing a form"""
    new_form_name = faker.word()
    data = {
        'form_name': new_form_name,
        'menu_master_id': seed_ids['menu_master_id'],
        'sub_menu_master_id': seed_ids['submenu_master_id'],
        'form_url': faker.url(),
        'form_description': faker.sentence(),
        'is_menu_visible': True
    }

    response = test_client.put(f'/form/edit/{seed_ids["form_master_id"]}', headers=auth_header, json=data)
    assert response.status_code == 200
    assert 'Form updated successfully' in response.json['message']

def test_form_get(test_client, auth_header):
    """Test getting a specific form"""
    response = test_client.get(f'/form/edit/{seed_ids["form_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    assert 'Form found Successfully' in response.json['message']

def test_form_delete(test_client, auth_header):
    """Test deleting a form"""
    response = test_client.delete(f'/formdelete/{seed_ids["form_master_id"]}', headers=auth_header)
    assert response.status_code == 200
    assert 'Form deleted successfully' in response.json['message']


def test_entity_activate(test_client, auth_header):
    entity_id = seed_ids['form_master_id']
    response = test_client.put(f'/form/activate/{entity_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Form activated successfully' in response.json['message']

def test_entity_deactivate(test_client, auth_header):
    entity_id = seed_ids['form_master_id']
    
    print(f"Testing deactivation for entity_id: {entity_id}")
    
    response = test_client.put(f'/form/deactivate/{entity_id}', headers=auth_header)
    
    print(f"Response status code: {response.status_code}")
    print(response.json)  # Output the full response for debugging

    assert response.status_code == 200
    assert response.json['message'].strip() == 'Form deactivated successfully'

# import pytest
# from flask import Flask
# from flask_jwt_extended import create_access_token
# from app import app, db
# from app.models.role import FormMasterData, MenuMasterData, SubMenuMasterData
# from app.models.student import StudentLogin
# import time
# from faker import Faker

# faker = Faker()

# @pytest.fixture(scope='module')
# def test_client():
#     app.config['TESTING'] = True
#     with app.test_client() as testing_client:
#         with app.app_context():
#             db.create_all()
#             global seed_ids
#             seed_ids = seed_data()  # Seed once for the module
#             global student_id
#             student_id = signup_data()  # Create signup data for a student
#         yield testing_client
#         with app.app_context():
#             cleanup_seed_data()  # Cleanup after all tests
#             cleanup_signup_data(student_id)  # Cleanup the signup data
#             db.session.remove()

# @pytest.fixture
# def auth_header(test_client):
#     response = test_client.post('/auth/login', json={
#         "userid": faker.unique.email(),  # Use the unique email created during signup
#         "password": "password",  # Assuming a fixed password
#         "user_type": "student"
#     })

#     assert response.status_code == 200, f"Login failed with status code {response.status_code}"
    
#     data = response.json
#     if 'token' not in data:
#         pytest.fail(f"Login response missing 'token': {data}")
    
#     access_token = data['token']
#     return {'Authorization': access_token, 'student_id': student_id}

# def signup_data():
#     """Create a student user with unique fake data for testing."""
#     userid = faker.unique.email()
#     password = "password"  # Fixed password for testing
#     student = StudentLogin(
#         userid=userid,
#         password=password,
        
#         is_active=1,
#         created_by=faker.random_int(min=1, max=1000),  # Use a random integer for created_by
#         updated_by=faker.random_int(min=1, max=1000)
#     )
#     db.session.add(student)
#     db.session.commit()
#     return student.id  # Return the ID of the created student for cleanup

# def cleanup_signup_data(student_id):
#     """Cleanup the created student data after the tests."""
#     student = StudentLogin.query.filter_by(student_id=student_id).first()
#     if student:
#         db.session.delete(student)
#         db.session.commit()

# def seed_data():
#     """Seeds random data for testing."""
#     # Seed menu data
#     menu = MenuMasterData(
#         menu_name=faker.word(),
#         priority=faker.random_int(min=1, max=100),
#         created_by=faker.random_int(min=1, max=1000),  # Use a random integer for created_by
#         updated_by=faker.random_int(min=1, max=1000),
#         is_active=1
#     )
#     db.session.add(menu)
#     db.session.commit()

#     # Seed submenu data
#     submenu = SubMenuMasterData(
#         menu_master_id=menu.menu_master_id,
#         menu_name=faker.word(),
#         priority=faker.random_int(min=1, max=100),
#         created_by=faker.random_int(min=1, max=1000),  # Use a random integer for created_by
#         updated_by=faker.random_int(min=1, max=1000),
#         is_active=1
#     )
#     db.session.add(submenu)
#     db.session.commit()

#     # Seed form data
#     form = FormMasterData(
#         form_name=faker.word(),
#         menu_master_id=menu.menu_master_id,
#         sub_menu_master_id=submenu.submenu_master_id,
#         form_url=faker.url(),
#         form_description=faker.sentence(),
#         is_menu_visible=True,
#         is_active=1,
#         created_by=faker.random_int(min=1, max=1000),  # Use a random integer for created_by
#     )
#     db.session.add(form)
#     db.session.commit()

#     return {
#         'form_master_id': form.form_master_id,
#         'menu_master_id': menu.menu_master_id,
#         'submenu_master_id': submenu.submenu_master_id
#     }

# def cleanup_seed_data():
#     """Cleanup the seeded data after the tests."""
#     # Delete dependent records first
#     form_records = FormMasterData.query.filter_by(sub_menu_master_id=seed_ids['submenu_master_id']).all()
#     for form in form_records:
#         db.session.delete(form)
#     db.session.commit()  # Commit the deletion of dependent records

#     # Now delete the submenu
#     submenu = SubMenuMasterData.query.filter_by(submenu_master_id=seed_ids['submenu_master_id']).first()
#     if submenu:
#         db.session.delete(submenu)
#         db.session.commit()

#     # Delete the form master if it exists
#     form = FormMasterData.query.filter_by(form_master_id=seed_ids['form_master_id']).first()
#     if form:
#         db.session.delete(form)
#         db.session.commit()

#     # Finally, delete the menu
#     menu = MenuMasterData.query.filter_by(menu_master_id=seed_ids['menu_master_id']).first()
#     if menu:
#         db.session.delete(menu)
#         db.session.commit()

# def test_form_list(test_client, auth_header):
#     """Test listing forms"""
#     response = test_client.get('/form/list', headers=auth_header)
#     assert response.status_code == 200

# def test_form_add(test_client, auth_header):
#     """Test adding a form with random data"""
#     data = {
#         'form_name': faker.word(),
#         'menu_master_id': seed_ids['menu_master_id'],
#         'sub_menu_master_id': seed_ids['submenu_master_id'],
#         'form_url': faker.url(),
#         'form_description': faker.sentence(),
#         'is_menu_visible': True
#     }

#     response = test_client.post('/form/add', headers=auth_header, json=data)
#     assert response.status_code == 200

# def test_form_edit(test_client, auth_header):
#     """Test editing a form"""
#     new_form_name = faker.word()
#     data = {
#         'form_name': new_form_name,
#         'menu_master_id': seed_ids['menu_master_id'],
#         'sub_menu_master_id': seed_ids['submenu_master_id'],
#         'form_url': faker.url(),
#         'form_description': faker.sentence(),
#         'is_menu_visible': True
#     }

#     response = test_client.put(f'/form/edit/{seed_ids["form_master_id"]}', headers=auth_header, json=data)
#     assert response.status_code == 200
#     assert 'Form updated successfully' in response.json['message']

# def test_form_get(test_client, auth_header):
#     """Test getting a specific form"""
#     response = test_client.get(f'/form/edit/{seed_ids["form_master_id"]}', headers=auth_header)
#     assert response.status_code == 200
#     assert 'Form found Successfully' in response.json['message']

# def test_form_delete(test_client, auth_header):
#     """Test deleting a form"""
#     response = test_client.delete(f'/formdelete/{seed_ids["form_master_id"]}', headers=auth_header)
#     assert response.status_code == 200
#     assert 'Form deleted successfully' in response.json['message']

# def test_entity_activate(test_client, auth_header):
#     entity_id = seed_ids['form_master_id']
#     response = test_client.put(f'/form/activate/{entity_id}', headers=auth_header)
#     assert response.status_code == 200
#     assert 'Form activated successfully' in response.json['message']

# def test_entity_deactivate(test_client, auth_header):
#     entity_id = seed_ids['form_master_id']
    
#     print(f"Testing deactivation for entity_id: {entity_id}")
    
#     response = test_client.put(f'/form/deactivate/{entity_id}', headers=auth_header)
    
#     print(f"Response status code: {response.status_code}")
#     print(response.json)  # Output the full response for debugging

#     assert response.status_code == 200
#     assert response.json['message'].strip() == 'Form deactivated successfully'
