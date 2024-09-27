import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.role import FormMasterData, MenuMasterData,SubMenuMasterData,ManageRole
from app.models.adminuser import AdminLogin
import time
from app.models.student import StudentLogin
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
            # global seed_ids
            # seed_ids = seed_data()  # Seed once for the module
        yield testing_client
        with app.app_context():
            cleanup_seed_data()  # Cleanup after all tests
            db.session.remove()
@pytest.fixture(scope='module')
def auth_header(test_client):
#     test_client.post('/auth/signup', json={
#   "userid": "admin123",
#   "password": "admin123",
#   "user_type": "admin"
# })
    unique_email = f"{faker.unique.email().split('@')[0]}_{random.randint(1000, 9999)}@example.com"

    # First, sign up a new user
    signup_response = test_client.post('/auth/signup', json={
        "userid": unique_email,
        "password": "password",
        "user_type": "admin"
    })

    assert signup_response.status_code == 200, f"Signup failed with status code {signup_response.status_code}"
    assert signup_response.json['status'] == 200, f"Signup error: {signup_response.json['message']}"

    # Now, attempt to log in using the unique email
    login_response = test_client.post('/auth/login', json={
        "userid": unique_email,
        "password": "password",
        "user_type": "admin"
    })

    assert login_response.status_code == 200, f"Login failed with status code {login_response.status_code}"

    data = login_response.json
    if 'token' not in data:
        pytest.fail(f"Login response missing 'token': {data}")

    access_token = data['token']
    admin_id = data['data']['id'] 
    global seed_ids
    seed_ids = seed_data(admin_id) 
     # Extracting admin ID
    yield {'Authorization': access_token, 'admin_id': admin_id}
    user_to_delete = AdminLogin.query.filter_by(userid=unique_email).first()
    if user_to_delete:
        db.session.query(LoginLog).filter_by(admin_id=user_to_delete.admin_id).delete()
        db.session.delete(user_to_delete)
        db.session.commit()


def seed_data(admin_id):
    # Check if the admin login exists
    admin_login = AdminLogin.query.filter_by(admin_id=admin_id).first()
    if not admin_login:
        raise ValueError(f"Admin login with admin_id '{admin_id}' not found")
    admin_id = admin_login.admin_id
    menu_name = faker.unique.word()  
    form_name = faker.unique.word()   
    submenu_name = faker.unique.word()  

    # Create a menu
    menu = MenuMasterData(
        menu_name=menu_name,
        priority=1,
        is_active=1,
        created_by=admin_id  
    )
    db.session.add(menu)
    db.session.commit()

    # Create a form associated with the menu
    form = FormMasterData(
        form_name=form_name,
        form_url='http://example.com',
        form_description=faker.sentence(),
        is_menu_visible=True,
        is_active=1,
        menu_master_id=menu.menu_master_id,
        created_by=admin_id
    )
    db.session.add(form)
    db.session.commit()

    # Create a submenu associated with the menu
    submenu = SubMenuMasterData(
        menu_name=submenu_name,
        priority=1,
        is_active=1,
        menu_master_id=menu.menu_master_id,
        created_by=admin_id
    )
    db.session.add(submenu)
    db.session.commit()

    # Create a manage role for the admin
    manage_role = ManageRole(
        admin_id=admin_id,
        form_master_id=form.form_master_id,  # Associate with a form
        is_search=True,
        is_save=True,
        is_update=True,
        is_active=1
    )
    db.session.add(manage_role)
    db.session.commit()

    return {
        'menu_id': menu.menu_master_id,
        'form_id': form.form_master_id,
        'submenu_id': submenu.submenu_master_id,
        'manage_role_id': manage_role.manage_role_id,
    }


def cleanup_seed_data():
    # Delete submenus associated with the menu
    SubMenuMasterData.query.filter_by(menu_master_id=seed_ids['menu_id']).delete()
    
    # Delete forms associated with the menu
    FormMasterData.query.filter_by(menu_master_id=seed_ids['menu_id']).delete()
    
    # Delete the menu itself
    MenuMasterData.query.filter_by(menu_master_id=seed_ids['menu_id']).delete()
    
    db.session.commit()

def test_menu_routes(test_client, auth_header):
    # Test /menu/list
    response = test_client.get('/menu/list', headers=auth_header)
    assert response.status_code == 200
    

def test_menu_list_by_user_type(test_client, auth_header):
    user_types = ['admin', 'student']  # Example user types to test
    for user_type in user_types:
        response = test_client.get(f'/menu/list/{user_type}', headers=auth_header)
        assert response.status_code in [200, 404], f"Unexpected status code for user type '{user_type}': {response.status_code}"
        
        data = response.get_json()
        assert 'Menus found Successfully' in data['message'] or 'No Menu found' in data['message'], f"Unexpected message for user type '{user_type}': {data['message']}"
        
        if response.status_code == 200:
            # Check that the data structure is correct if menus are found
            menus = data.get('data', [])
            assert isinstance(menus, list), "Expected 'data' to be a list"
            for menu in menus:
                assert 'id' in menu
                assert 'menu_name' in menu
                assert 'submenus' in menu
def test_add_menu(test_client, auth_header):
    payload = {
        "menu_name": faker.unique.word(),  # Using Faker for unique menu name
        "priority": faker.random_int(min=1, max=10)  # Random priority between 1 and 10
    }
    
    response = test_client.post('/menu/add', json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Menu created successfully' in data['message']

    # Cleanup: Retrieve the added menu and delete it
    menu = MenuMasterData.query.filter_by(menu_name=payload["menu_name"]).first()
    if menu:
        db.session.delete(menu)
        db.session.commit()

# Test: Edit Menu
def test_edit_menu(test_client, auth_header):
    payload = {
        "menu_name": faker.unique.word(),  # Faker for new menu name
        "priority": faker.random_int(min=1, max=10)  # New random priority
    }
    response = test_client.put(f'/menu/edit/{seed_ids["menu_id"]}', json=payload, headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Menu updated successfully' in data['message']

# Test: Get Menu by ID
def test_get_menu(test_client, auth_header):
    response = test_client.get(f'/menu/edit/{seed_ids["menu_id"]}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Menu found Successfully' in data['message']

# Test: Activate Menu
def test_activate_menu(test_client, auth_header):
    response = test_client.put(f'/menu/activate/{seed_ids["menu_id"]}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Menu activated successfully' in data['message']

# Test: Deactivate Menu
def test_deactivate_menu(test_client, auth_header):
    response = test_client.put(f'/menu/deactivate/{seed_ids["menu_id"]}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Menu deactivated successfully' in data['message']

# Test: Delete Menu
def test_delete_menu(test_client, auth_header):
    response = test_client.delete(f'/menudelete/{seed_ids["menu_id"]}', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert 'Menu deleted successfully' in data['message']


def test_list_menus_by_admin(test_client, auth_header):
    valid_admin_id = auth_header['admin_id']
    print(f'Received request for admin_id: {valid_admin_id}')

    response = test_client.get(f'/menu/list_by_admin/{valid_admin_id}', headers=auth_header)
    print(f'API response status code: {response.status_code}')

    if response.status_code == 404:
        data = response.get_json()
        if data is not None:
            print(f'Error message: {data.get("message")}')
        else:
            print('No response data received for 404 error.')

    assert response.status_code in [200, 404], f"Expected 200 or 404 but got {response.status_code}"
    if response.status_code == 200:
        data = response.get_json()
        assert 'Menus found successfully' in data['message']
        assert isinstance(data['data'], list)

def test_menu_add_missing_menu_name(test_client, auth_header):
    # Test adding a menu without a menu name
    response = test_client.post('/menu/add', json={
        "priority": 1
    }, headers=auth_header)

    assert response.is_json
   
    assert response.json['message'] == 'Please Provide Menu name'


def test_menu_add_missing_priority(test_client, auth_header):
    # Test adding a menu without a priority
    response = test_client.post('/menu/add', json={
        "menu_name": "Main Menu"
    }, headers=auth_header)

    assert response.is_json
    
    assert response.json['message'] == 'Please Provide Priority'

def test_edit_menu_missing_name(test_client, auth_header):
    # Create a sample menu for testing
      # Assuming the API returns the menu ID

    # Attempt to update the menu without the menu name
    response = test_client.put(f'/menu/edit/{seed_ids["menu_id"]}', json={
        'priority': 2
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Please Provide Menu name'
   


def test_edit_menu_missing_priority(test_client, auth_header):
    # Create a sample menu for testing
   
    # Attempt to update the menu without the priority
    response = test_client.put(f'/menu/edit/{seed_ids["menu_id"]}', json={
        'menu_name': faker.word()
    }, headers=auth_header)

    assert response.is_json
    assert response.json['message'] == 'Please Provide Priority'
    