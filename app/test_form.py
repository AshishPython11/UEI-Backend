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

def test_add_form_missing_form_name(test_client, auth_header):
    response = test_client.post('/form/add', json={
        "menu_master_id": seed_ids['menu_master_id'],
        "form_url": "http://example.com"
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Please Provide Form name'


def test_add_form_missing_menu_master_id(test_client, auth_header):
    response = test_client.post('/form/add', json={
        "form_name": "Test Form",
        "form_url": "http://example.com"
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Please Provide Menu Id'


def test_add_form_missing_form_url(test_client, auth_header):
    response = test_client.post('/form/add', json={
        "form_name": "Test Form",
        "menu_master_id": seed_ids['menu_master_id']
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Please Provide Form Url'








def test_edit_form_missing_name(test_client, auth_header):
    # Create a sample form for testing
     # Assuming the API returns the form ID

    # Attempt to update the form without the form name
    response = test_client.put(f'/form/edit/{seed_ids["form_master_id"]}', json={
        'menu_master_id': seed_ids['menu_master_id'],
        'form_url': 'http://example.com/updated_form',
        'form_description': 'Updated description of test form',
        'is_menu_visible': False
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Please Provide Form name'
    


def test_edit_form_missing_menu_id(test_client, auth_header):
    # Create a sample form for testing
      # Assuming the API returns the form ID

    # Attempt to update the form without the menu ID
    response = test_client.put(f'/form/edit/{seed_ids["form_master_id"]}', json={
        'form_name': 'Updated Test Form',
        'form_url': 'http://example.com/updated_form',
        'form_description': 'Updated description of test form',
        'is_menu_visible': False
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Please Provide Menu Id'
   


def test_edit_form_missing_form_url(test_client, auth_header):
    # Create a sample form for testing
     # Assuming the API returns the form ID

    # Attempt to update the form without the form URL
    response = test_client.put(f'/form/edit/{seed_ids["form_master_id"]}', json={
        'form_name': 'Updated Test Form',
        'menu_master_id': seed_ids['menu_master_id'],
        'form_description': 'Updated description of test form',
        'is_menu_visible': False
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Please Provide Form Url'
    

def test_form_edit_invalid(test_client, auth_header):
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

    response = test_client.put('/form/edit/8889659', headers=auth_header, json=data)
   
    assert 'Form not found' in response.json['message']



def test_form_delete_invalid(test_client, auth_header):
    """Test deleting a form"""
    response = test_client.delete('/formdelete/8889659', headers=auth_header)

    assert 'form not found' in response.json['message']


def test_entity_activate_invalid(test_client, auth_header):
    
    response = test_client.put('/form/activate/774589', headers=auth_header)
    
    assert 'Form not found' in response.json['message']

def test_entity_deactivate_invalid(test_client, auth_header):
   
    

    
    response = test_client.put('/form/deactivate/888596', headers=auth_header)
    
    
   
    assert response.json['message'].strip() == 'Form not found'