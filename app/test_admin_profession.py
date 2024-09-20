import pytest
from flask import Flask
from flask_jwt_extended import create_access_token
from app import app, db
from app.models.adminuser import AdminContact,CourseMaster,SubjectMaster,EntityType,Institution

@pytest.fixture(scope='module')
def test_client():
    app.config['TESTING'] = True
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            global seed_ids
            seed_ids = seed_data()  
        yield testing_client
        with app.app_context():
            db.session.remove()

@pytest.fixture
def auth_header(test_client):
#     test_client.post('/auth/signup', json={
#   "userid": "admin123",
#   "password": "admin123",
#   "user_type": "admin"
# })
    response = test_client.post('/auth/login', json={
  "userid": "admin123",
  "password": "admin123",
  "user_type": "admin"
})

    print("Login response status code:", response.status_code)
    print("Login response data:", response.json)
    
    assert response.status_code == 200, f"Login failed with status code {response.status_code}"
    
    data = response.json
    if 'token' not in data:
        pytest.fail(f"Login response missing 'token': {data}")
    
    access_token = data['token']
    admin_id=data['data']['id']
    return {'Authorization': access_token,'admin_id':admin_id}
def seed_data():
    entity_type = EntityType(entity_type='Admin', is_active=1)
    db.session.add(entity_type)
    db.session.commit()

    institution = Institution(
        institution_name='Test Institution',
        entity_id=entity_type.entity_id,  
        address='123 Test St',
        country='Testland',
        state='Test State',
        city='Test City',
        district='Test District',
        pincode='12345',
        website_url='http://testinstitution.com',
        mobile_no='1234567890',
        email_id='test@test.com'
    )
    db.session.add(institution)
    db.session.commit()

    course = CourseMaster(
        course_name='Test Course',
        is_active=1
    )
    db.session.add(course)
    db.session.commit()

    subject = SubjectMaster(
        subject_name='Test Subject',
        is_active=1
    )
    db.session.add(subject)
    db.session.commit()

    return {
        'entity_type_id': entity_type.entity_id,
        'institution_id': institution.institution_id,
        'course_id': course.course_id,
        'subject_id': subject.subject_id
    }

def test_add_admin_profession(test_client, auth_header):
    response = test_client.post('/admin_profession/add', json={
        'admin_id': auth_header['admin_id'],
        'institution_id': seed_ids['institution_id'],  
        'course_id': seed_ids['course_id'],            
        'subject_id': seed_ids['subject_id']            
    }, headers=auth_header)   
    assert response.status_code in [200, 201]   
    data = response.json
    if response.status_code == 200:
        assert data['message'] == 'Admin Profession created successfully'
    elif response.status_code == 201:
        assert data['message'] in [
            'Please Provide Admin Id',
            'Please Provide Institute Id',
            'Please Provide Course Id',
            'Please Provide Subject Id'
        ]


def test_get_admin_professions_list(test_client, auth_header):
    response = test_client.get('/admin_profession/list', headers=auth_header)
    assert response.status_code in [200, 404]    
    data = response.json
    if response.status_code == 200:
        assert data['message'] == 'Admin Professions found Successfully'
        assert 'data' in data
        assert isinstance(data['data'], list)
    elif response.status_code == 404:
        assert data['message'] == 'No Admin Profession found'


def test_get_all_admin_professions(test_client, auth_header):
    response = test_client.get('/admin_profession/alldata', headers=auth_header)
    assert response.status_code in [200, 404]   
    data = response.json
    if response.status_code == 200:
        assert data['message'] == 'Admin Professions found Successfully'
        assert 'data' in data
        assert isinstance(data['data'], list)
    elif response.status_code == 404:
        assert data['message'] == 'No Admin Profession found'
    

def test_edit_admin_profession(test_client, auth_header):
    add_response = test_client.post('/admin_profession/add', json={
        'admin_id': auth_header['admin_id'],
        'institution_id': seed_ids['institution_id'],  # Use the seeded institution_id
        'course_id': seed_ids['course_id'],             # Use the seeded course_id
        'subject_id': seed_ids['subject_id']
    }, headers=auth_header)   
    assert add_response.status_code == 200
    response = test_client.put(f'/admin_profession/edit/{auth_header["admin_id"]}', json={
        'admin_id': auth_header['admin_id'],
        'institution_id': seed_ids['institution_id'],  # Use the seeded institution_id
        'course_id': seed_ids['course_id'],             # Use the seeded course_id
        'subject_id': seed_ids['subject_id']
    }, headers=auth_header)   
    assert response.status_code in [200, 201, 404]
    data = response.json
    if response.status_code == 200:
        assert data['message'] == 'Admin Profession updated successfully'
    elif response.status_code == 201:
        assert data['message'] in [
            'Please Provide Admin Id',
            'Please Provide Institute Id',
            'Please Provide Course Id',
            'Please Provide Subject Id'
        ]
    elif response.status_code == 404:
        assert data['message'] == 'Admin Profession not found'


def test_get_admin_profession_by_id(test_client, auth_header):
    add_response = test_client.post('/admin_profession/add', json={
        'admin_id': auth_header['admin_id'],
        'institution_id': seed_ids['institution_id'],  # Use the seeded institution_id
        'course_id': seed_ids['course_id'],             # Use the seeded course_id
        'subject_id': seed_ids['subject_id']
    }, headers=auth_header)    
    assert add_response.status_code == 200
    response = test_client.get(f'/admin_profession/edit/{auth_header["admin_id"]}', headers=auth_header)   
    assert response.status_code in [200, 404]   
    data = response.json
    if response.status_code == 200:
        assert data['message'] == 'Admin Profession found Successfully'
        assert 'data' in data
        assert data['data']['admin_id'] == auth_header["admin_id"]
    elif response.status_code == 404:
        assert data['message'] == 'Admin Profession not found'


def test_activate_admin_profession(test_client, auth_header):
    add_response = test_client.post('/admin_profession/add', json={
        'admin_id': auth_header['admin_id'],
       'institution_id': seed_ids['institution_id'],  # Use the seeded institution_id
        'course_id': seed_ids['course_id'],             # Use the seeded course_id
        'subject_id': seed_ids['subject_id']
    }, headers=auth_header)    
    assert add_response.status_code == 200  
    response = test_client.get(f'/admin_profession/edit/{auth_header["admin_id"]}', headers=auth_header)    
    assert response.status_code ==200   
    data = response.json     
    activate_id=data['data']['id'] 
    test_client.put(f'/admin_profession/deactivate/{activate_id}', headers=auth_header)
    response = test_client.put(f'/admin_profession/activate/{activate_id}', headers=auth_header)    
    assert response.status_code == 200
    assert response.json['message'] == 'Admin Profession activated successfully'


def test_deactivate_admin_profession(test_client, auth_header):
    add_response = test_client.post('/admin_profession/add', json={
        'admin_id': auth_header['admin_id'],
        'institution_id': seed_ids['institution_id'],  
        'course_id': seed_ids['course_id'],             
        'subject_id': seed_ids['subject_id']
    }, headers=auth_header)   
    assert add_response.status_code == 200
    response = test_client.get(f'/admin_profession/edit/{auth_header["admin_id"]}', headers=auth_header)    
    assert response.status_code ==200   
    data = response.json       
    activate_id=data['data']['id']    
    response = test_client.put(f'/admin_profession/deactivate/{activate_id}', headers=auth_header)   
    assert response.status_code == 200
    assert response.json['message'] == 'Admin Profession deactivated successfully'
