# import pytest
# from flask import Flask, jsonify
# from flask_jwt_extended import create_access_token
# from app import app, db
# from app.models.student import Contact, StudentAddress, Student, StudentLogin, StudentHobby, SubjectPreference, NewStudentAcademicHistory, LanguageKnown,LanguageMaster
# from faker import Faker
# from datetime import datetime
# from sqlalchemy import func

# faker = Faker()

# @pytest.fixture(scope='module')
# def test_client():
#     app.config['TESTING'] = True
#     with app.test_client() as testing_client:
#         with app.app_context():
#             db.create_all()
#         yield testing_client
#         with app.app_context():
#             db.session.remove()

# @pytest.fixture
# def auth_header(test_client):
#     unique_email = faker.unique.email()

#     # Sign up a new user
#     signup_response = test_client.post('/auth/signup', json={
#         "userid": unique_email,
#         "password": "password",
#         "user_type": "student"
#     })
#     assert signup_response.status_code == 200, f"Signup failed with status code {signup_response.status_code}"

#     # Log in using the unique email
#     login_response = test_client.post('/auth/login', json={
#         "userid": unique_email,
#         "password": "password",
#         "user_type": "student"
#     })
#     assert login_response.status_code == 200, f"Login failed with status code {login_response.status_code}"

#     data = login_response.json
#     assert 'token' in data, f"Login response missing 'token': {data}"

#     access_token = data['token']
#     student_id = data['data']['id']
#     global seed_ids
#     seed_ids = seed_data(student_id)  # Seed data for the student
#     yield {'Authorization': f'Bearer {access_token}', 'student_id': student_id}
#     cleanup_seed_data()

# def seed_data(student_id):
#     """ Seed random data for the student. """
#     # Seed Contact data
#     contact = Contact(
#         student_id=student_id,
#         mobile_isd_call=faker.country_code(),
#         mobile_no_call=faker.phone_number(),
#         mobile_isd_watsapp=faker.country_code(),
#         email_id=faker.email()
#     )
#     db.session.add(contact)

#     # Seed Address data
#     address = StudentAddress(
#         student_id=student_id,
#         address1=faker.address(),
#         address2=faker.address(),
#         country=faker.country(),
#         state=faker.state(),
#         city=faker.city(),
#         district=faker.city(),
#         pincode=faker.postcode(),
#         address_type='home'
#     )
#     db.session.add(address)

#     # Seed Academic history
#     academic = NewStudentAcademicHistory(
#         student_id=student_id,
#         institution_type=faker.word(),
#         course_id=faker.random_int(),  # Ensure this is a valid course_id in your tests
#         learning_style="visual",
#         created_by=faker.name(),
#         updated_by=faker.name(),
#     )
#     db.session.add(academic)

#     # Seed Hobby
#     hobby = StudentHobby(student_id=student_id, hobby_id=faker.random_int())
#     db.session.add(hobby)

#     # Seed Subject Preference
#     subject_pref = SubjectPreference(
#         student_id=student_id,
#         course_id=faker.random_int(),
#         subject_id=faker.random_int(),
#         preference="high",
#         score_in_percentage=faker.random_int(min=50, max=100)
#     )
#     db.session.add(subject_pref)

#     # Seed Language Known
#     # Fetch a valid language_id from the tbl_language_master
#     language_id = db.session.query(LanguageMaster.language_id).order_by(func.random()).first()
#     if language_id:
#         language = LanguageKnown(
#             student_id=student_id,
#             language_id=language_id[0],  # Extracting the id from the tuple
#             proficiency="fluent"
#         )
#         db.session.add(language)
#     else:
#         print("No valid language found. Skipping Language Known seeding.")

#     db.session.commit()
#     return {
#         "contact": contact.id,
#         "address": address.id,
#         "academic": academic.id,
#         "hobby": hobby.id,
#         "subject_pref": subject_pref.id,
#         "language": language.id if 'language' in locals() else None  # Include only if language was added
#     }

# def cleanup_seed_data():
#     """ Clean up the seeded data. """
#     db.session.query(Contact).filter(Contact.id.in_(seed_ids.values())).delete(synchronize_session=False)
#     db.session.query(StudentAddress).filter(StudentAddress.id.in_(seed_ids.values())).delete(synchronize_session=False)
#     db.session.query(NewStudentAcademicHistory).filter(NewStudentAcademicHistory.id.in_(seed_ids.values())).delete(synchronize_session=False)
#     db.session.query(StudentHobby).filter(StudentHobby.id.in_(seed_ids.values())).delete(synchronize_session=False)
#     db.session.query(SubjectPreference).filter(SubjectPreference.id.in_(seed_ids.values())).delete(synchronize_session=False)
#     db.session.query(LanguageKnown).filter(LanguageKnown.id.in_(seed_ids.values())).delete(synchronize_session=False)
#     db.session.commit()

# def test_student_list_completion(test_client, auth_header):
#     """ Test the /student-list API for completion calculation. """
#     response = test_client.get('/student-list', headers=auth_header)
    
#     assert response.status_code == 200, f"Expected status code 200 but got {response.status_code}"
    
#     data = response.json
#     assert 'results' in data, "Response missing 'results'"
#     assert 'overall_percentage' in data, "Response missing 'overall_percentage'"

#     print(f"Results: {data['results']}")
#     print(f"Overall Percentage: {data['overall_percentage']}")

