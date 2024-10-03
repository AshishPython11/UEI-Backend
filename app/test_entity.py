import pytest
from app import app, db
from app.models.log import *
from app.models.adminuser import EntityType, AdminBasicInformation
import time
from faker import Faker
faker=Faker()
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
    # You can seed user data here if needed for login
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
    student_id = data['data']['id'] 
      # Extracting student ID
    yield {'Authorization': access_token, 'student_id': student_id}
    

def seed_data():
    entity = EntityType(entity_type=faker.word(), is_active=1, is_deleted=False, created_by='1')
    db.session.add(entity)
    db.session.commit()
    return {'entity_id': entity.entity_id}

def cleanup_seed_data():
    EntityType.query.filter_by(entity_id=seed_ids['entity_id']).delete()
    db.session.commit()

# Test cases

def test_entity_list(test_client, auth_header):
    response = test_client.get('/entity/list', headers=auth_header)
    assert response.status_code == 200
    assert 'Entities found Successfully' in response.json['message']

def test_entity_add(test_client, auth_header):
    base_class_name = 'Unique Class Name'
    unique_suffix = str(int(time.time())) 
    unique_entity_name = f"{base_class_name}_{unique_suffix}"
    response = test_client.post('/entity/add', headers=auth_header, json={
        "entity_type": unique_entity_name
    })
    assert response.status_code == 200
    assert 'Entity created successfully' in response.json['message']
    

def test_entity_edit(test_client, auth_header):
    base_class_name = 'Unique Class Name'
    unique_suffix = str(int(time.time())) 
    updated_entity_name = f"{base_class_name}_{unique_suffix}"
    entity_id = seed_ids['entity_id']
    response = test_client.put(f'/entity/edit/{entity_id}', headers=auth_header, json={
        "entity_type": updated_entity_name
    })
    assert response.status_code == 200
    assert 'Entity updated successfully' in response.json['message']

def test_entity_get(test_client, auth_header):
    entity_id = seed_ids['entity_id']
    response = test_client.get(f'/entity/edit/{entity_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Entity found Successfully' in response.json['message']

def test_entity_delete(test_client, auth_header):
    entity_id = seed_ids['entity_id']
    response = test_client.delete(f'/entitydelete/{entity_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Entity deleted successfully' in response.json['message']

def test_entity_activate(test_client, auth_header):
    entity_id = seed_ids['entity_id']
    response = test_client.put(f'/entity/activate/{entity_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Entity activated successfully' in response.json['message']

def test_entity_deactivate(test_client, auth_header):
    entity_id = seed_ids['entity_id']
    response = test_client.put(f'/entity/deactivate/{entity_id}', headers=auth_header)
    assert response.status_code == 200
    assert 'Entity deactivated successfully' in response.json['message']
def test_add_entity_missing_entity_type(test_client, auth_header):
    response = test_client.post('/entity/add', json={}, headers=auth_header)
    
    assert response.is_json
    assert response.json['message'] == 'Please Provide Entity type'


def test_edit_entity_missing_entity_type(test_client, auth_header):
    response = test_client.put(f'/entity/edit/{seed_ids['entity_id']}', json={}, headers=auth_header)
    
    assert response.is_json
    assert response.json['message'] == 'Please provide entity type'




def test_entity_edit_invalid(test_client, auth_header):
    base_class_name = 'Unique Class Name'
    unique_suffix = str(int(time.time())) 
    updated_entity_name = f"{base_class_name}_{unique_suffix}"
    
    response = test_client.put('/entity/edit/888859', headers=auth_header, json={
        "entity_type": updated_entity_name
    })
 
    assert 'Entity not found' in response.json['message']

def test_entity_get_invalid(test_client, auth_header):
   
    response = test_client.get('/entity/edit/888569', headers=auth_header)
    
    assert 'Entity not found' in response.json['message']

def test_entity_delete_invalid(test_client, auth_header):
  
    response = test_client.delete('/entitydelete/8888569', headers=auth_header)

    assert 'entity not found' in response.json['message']

def test_entity_activate_invalid(test_client, auth_header):
  
    response = test_client.put(f'/entity/activate/888785', headers=auth_header)
  
    assert 'Entity not found' in response.json['message']

def test_entity_deactivate_invalid(test_client, auth_header):
   
    response = test_client.put('/entity/deactivate/888965', headers=auth_header)
    
    assert 'Entity not found' in response.json['message']