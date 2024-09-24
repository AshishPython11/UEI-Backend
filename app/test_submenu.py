import pytest
from faker import Faker
from app import db,app
from app.models.adminuser import AdminLogin
from app.models.role import MenuMasterData,SubMenuMasterData
from flask_jwt_extended import create_access_token
from datetime import datetime
from app.models.log import *
faker = Faker()
@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
              # Seed once for the module
        yield testing_client
        with app.app_context():
            cleanup_seed_data()  # Cleanup after all tests
            db.session.remove()
@pytest.fixture
def auth_header(test_client):
#     test_client.post('/auth/signup', json={
#   "userid": "admin123",
#   "password": "admin123",
#   "user_type": "admin"
# })
    unique_email = faker.unique.email()

    # First, sign up a new user
    signup_response = test_client.post('/auth/signup', json={
        "userid": unique_email,  # Unique email for signup
        "password": "password",  # Assuming a fixed password
        "user_type": "admin"
    })

    assert signup_response.status_code == 200, f"Signup failed with status code {signup_response.status_code}"
    assert signup_response.json['status'] == 200, f"Signup error: {signup_response.json['message']}"

    # Now, attempt to log in using the unique email directly
    login_response = test_client.post('/auth/login', json={
        "userid": unique_email,  # Use the same unique email
        "password": "password",  # Same password
        "user_type": "admin"
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
    admin_id = data['data']['id'] 
    global seed_ids
    seed_ids = seed_data(admin_id)  # Extracting student ID
    yield {'Authorization': access_token, 'admin_id': admin_id}
    cleanup_seed_data()

    # Fetch the user to delete based on the unique email
    user_to_delete = StudentLogin.query.filter_by(userid=unique_email).first()
    if user_to_delete:
        # First, delete any logs related to the user from LoginLog
        db.session.query(LoginLog).filter_by(admin_id=user_to_delete.admin_id).delete()

        # Delete any addresses related to the user from tbl_student_address
        # db.session.query(Contact).filter_by(student_id=user_to_delete.student_id).delete()

        # Delete related subject preferences before deleting the student login
        

        # Now delete the student login itself
        db.session.delete(user_to_delete)

        # Commit the changes to reflect the deletions
        db.session.commit()

def seed_data(admin_id):
    admin_login = AdminLogin.query.filter_by(admin_id=admin_id).first()
    if not admin_login:
        raise ValueError("Admin login with userid 'admin123' not found")
    
    admin_id = admin_login.admin_id
    menu_name = faker.unique.word()
    
    menu = MenuMasterData(menu_name=menu_name, priority=1, is_active=1, created_by=admin_id)
    db.session.add(menu)
    db.session.commit()

    submenu = SubMenuMasterData(menu_name=faker.unique.word(), priority=1, is_active=1, menu_master_id=menu.menu_master_id, created_by=admin_id)
    db.session.add(submenu)
    db.session.commit()

    return {
        'submenu_id': submenu.submenu_master_id,
        'menu_id': menu.menu_master_id,
    }

def cleanup_seed_data():
    SubMenuMasterData.query.filter_by(menu_master_id=seed_ids['menu_id']).delete()
    MenuMasterData.query.filter_by(menu_master_id=seed_ids['menu_id']).delete()
    db.session.commit()

def test_list_submenus(test_client, auth_header):
    response = test_client.get('/submenu/list', headers=auth_header)
    assert response.status_code == 200
    

def test_add_submenu(test_client, auth_header):
    data = {
        'menu_name': faker.unique.word(),
        'menu_master_id': seed_ids['menu_id'],
        'priority': 2
    }
    response = test_client.post('/submenu/add', json=data, headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'SubMenu created successfully'

def test_edit_submenu(test_client, auth_header):
    data = {
        'menu_name': faker.unique.word(),
        'menu_master_id': seed_ids['menu_id'],
        'priority': 3
    }
    response = test_client.put(f'/submenu/edit/{seed_ids["submenu_id"]}', json=data, headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'SubMenu updated successfully'

def test_get_submenu(test_client, auth_header):
    response = test_client.get(f'/submenu/edit/{seed_ids["submenu_id"]}', headers=auth_header)
    assert response.status_code == 200
    assert response.json['data']['id'] == seed_ids['submenu_id']

def test_delete_submenu(test_client, auth_header):
    response = test_client.delete(f'/submenudelete/{seed_ids["submenu_id"]}', headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'SubMenu deleted successfully'

def test_activate_submenu(test_client, auth_header):
    response = test_client.put(f'/submenu/activate/{seed_ids["submenu_id"]}', headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'SubMenu activated successfully'

def test_deactivate_submenu(test_client, auth_header):
    response = test_client.put(f'/submenu/deactivate/{seed_ids["submenu_id"]}', headers=auth_header)
    assert response.status_code == 200
    assert response.json['message'] == 'SubMenu deactivated successfully'
