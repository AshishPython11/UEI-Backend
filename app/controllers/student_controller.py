import base64
from datetime import datetime
import json
import os
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations,logger
from flask_restx import Api, Namespace, Resource, fields
from app.models.adminuser import CourseMaster, Institution, SubjectMaster,EntityType,LanguageMaster
from app.models.student import AcademicHistory, Contact,NewStudentAcademicHistory, LanguageKnown, Student, StudentAddress, StudentHobby, StudentLogin,ClassMaster, SubjectPreference,Hobby

# UPLOAD_FOLDER = 'uploads/student'
UPLOAD_FOLDER = '/home/ubuntu/UEI-Backend/uploads/student'
current_path = os.getcwd()
full_path = os.path.join(current_path, UPLOAD_FOLDER)
class StudentController:
    def __init__(self,api):
        self.api = api
        self.student_model = api.model('Student', {
            'aim': fields.String(required=False, description='Aim'),
            'first_name': fields.String(required=True, description='Admin First Name'),
            'last_name': fields.String(required=True, description='Admin Last Name'),
            'gender': fields.String(required=True, description='Admin Gender'),
            'dob': fields.Date(required=True, description='Admin Date of Birth'),
            'father_name': fields.String(required=True, description='Admin Father Name'),
            'mother_name': fields.String(required=True, description='Admin Mother Name'),
            'guardian_name': fields.String(required=False, description='Admin Gaurdian Name'),
            'is_kyc_verified': fields.Boolean(required=True, description='Admin KYC verified'),
            'pic_path': fields.String(required=False, description='Admin Pic path'),
            'student_login_id': fields.String(required=True, description='Student Login Id')
        })
        
        
        self.student_bp = Blueprint('student', __name__)
        self.student_ns = Namespace('student', description='Student Details', authorizations=authorizations)

        self.register_routes()

        
    def register_routes(self):
        @self.student_ns.route('/list')
        class StudentList(Resource):
            def read_and_encode_file(self,file_path):
                if os.path.isfile(file_path):
                    with open(file_path, 'rb') as f:
                        encoded_bytes = base64.b64encode(f.read())
                        encoded_string = encoded_bytes.decode('utf-8')
                    return encoded_string
                else:
                    return None  
            @self.student_ns.doc('student/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    students = Student.query.filter_by().all()
                    students_data = []
                    if full_path is None:
                            raise ValueError("Full path is not set.")
                    for student in students:
                        file_path = os.path.join(full_path, student.pic_path)
                        if student.pic_path:
                            file_content = self.read_and_encode_file(file_path)
                            if file_content:
                                file_content_with_prefix = f"data:image/png;base64,{file_content}"
                            else:
                                file_content_with_prefix =''
                        
                        contact = Contact.query.filter_by(student_id=student.student_id).first()
                        

                        student_data = {
                            'id': student.student_id,
                            'first_name': student.first_name,
                            'last_name': student.last_name,
                            'gender': student.gender,
                            'dob': student.dob,
                            'father_name': student.father_name,
                            'mother_name': student.mother_name,
                            'guardian_name': student.guardian_name,
                            'is_kyc_verified': student.is_kyc_verified,
                            'pic_path': file_content_with_prefix,
                            'image_name': student.pic_path,
                            'student_registration_no': student.student_registration_no,
                            'last_modified_datetime': student.last_modified_datetime,
                            'aim': student.aim,
                            'is_active': student.is_active,
                           
                        }
                        if contact:
                            student_data['mobile_isd_call'] = contact.mobile_isd_call
                            student_data['mobile_no_call'] = contact.mobile_no_call
                            student_data['mobile_isd_watsapp'] = contact.mobile_isd_watsapp
                            student_data['mobile_no_watsapp'] = contact.mobile_no_watsapp
                            student_data['email_id'] = contact.email_id
                            student_data['contact_is_active'] = contact.is_active
                        else:
                            
                            student_data['mobile_isd_call'] = None
                            student_data['mobile_no_call'] = None
                            student_data['mobile_isd_watsapp'] = None
                            student_data['mobile_no_watsapp'] = None
                            student_data['email_id'] = None
                            student_data['contact_is_active'] = None

                        students_data.append(student_data)
                    
                    if not students_data:
                        logger.warning("No Student found")
                        return jsonify({'message': 'No Student found', 'status': 404})
                    else:
                        logger.info("Students found Successfully")
                        return jsonify({'message': 'Students found Successfully', 'status': 200, 'data': students_data})
                    
            
                    return jsonify({'message': 'Profile picture path stored successfully', 'status': 200})
                except Exception as e:
                   
                    logger.error(f"Error fetching student information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        @self.student_ns.route('/add')
        class StudentAdd(Resource):
            @self.student_ns.doc('student/add', security='jwt')
            @self.api.expect(self.student_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    last_data = Student.query.order_by(Student.student_id.desc()).first()
                    last_id = last_data.student_id if last_data else 0

                    aim = data.get('aim')
                    first_name = data.get('first_name')
                    last_name = data.get('last_name')
                    gender = data.get('gender')
                    dob = data.get('dob')
                    father_name = data.get('father_name')
                    mother_name = data.get('mother_name')
                    guardian_name = data.get('guardian_name')
                    is_kyc_verified = data.get('is_kyc_verified')
                    pic_path = data.get('pic_path')
                    student_login_id = data.get('student_login_id')

                    today_date = datetime.now().strftime('%Y%m%d')
                    series_number = f"{today_date}{last_id + 1:06d}"
                    student_registration_no = series_number
                    current_user_id = get_jwt_identity()

                   
                    if not first_name:
                        logger.warning("No first_name found")
                        return jsonify({'message': 'Please Provide First Name', 'status': 201})
                    if not last_name:
                        logger.warning("No last_name found")
                        return jsonify({'message': 'Please Provide Last Name', 'status': 201})
                    if not gender:
                        logger.warning("No gender found")
                        return jsonify({'message': 'Please Provide Gender', 'status': 201})
                    if not dob:
                        logger.warning("No dob found")
                        return jsonify({'message': 'Please Provide Date of Birth', 'status': 201})
                    if not father_name:
                        logger.warning("No father_name found")
                        return jsonify({'message': 'Please Provide Father Name', 'status': 201})
                    if not mother_name:
                        logger.warning("No mother_name found")
                        return jsonify({'message': 'Please Provide Mother Name', 'status': 201})

                
                    student = Student.query.filter_by(student_login_id=student_login_id).first()
                    
                    if student:
                        student.aim=aim
                        student.first_name = first_name
                        student.last_name = last_name
                        student.gender = gender
                        student.dob = dob
                        student.father_name = father_name
                        student.mother_name = mother_name
                        student.guardian_name = guardian_name
                        student.is_kyc_verified = is_kyc_verified
                        student.pic_path = pic_path if pic_path else student.pic_path  # Update pic_path if provided
                        student.last_modified_datetime = datetime.now()
                        student.system_datetime = datetime.now()
                        student.updated_by = current_user_id
                                
                    else:
                    
                        student = Student(
                            aim=aim,
                            first_name=first_name,
                            last_name=last_name,
                            gender=gender,
                            dob=dob,
                            father_name=father_name,
                            mother_name=mother_name,
                            guardian_name=guardian_name,
                            is_kyc_verified=is_kyc_verified,
                            pic_path=pic_path,
                          
                            student_registration_no=student_registration_no,
                            last_modified_datetime=datetime.now(),
                            system_datetime=datetime.now(),
                            student_login_id=student_login_id,
                            is_active=1,
                            created_by=current_user_id
                        )
                        db.session.add(student)

                    db.session.commit()
                    logger.info("Students processed Successfully")
                    return jsonify({'message': 'Student record processed successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error adding student information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.student_ns.route('/add/store_profile_picture')
        class StoreProfilePicture(Resource):
            @self.student_ns.doc('store_profile_picture', security='jwt')
            @self.api.expect(self.student_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    student_login_id = data.get('student_login_id')
                    pic_path = data.get('pic_path')
                    current_user_id = get_jwt_identity()
                    if not student_login_id:
                        logger.warning("No student_login_id found")
                        return jsonify({'message': 'Student Login ID is required', 'status': 400})
                    if not pic_path:
                        logger.warning("No pic_path found")
                        return jsonify({'message': 'Picture Path is required', 'status': 400})

                    student = StudentLogin.query.filter_by(student_id=student_login_id).first()
                    if not student:
                        logger.warning("No Student found")
                        return jsonify({'message': 'Student not found', 'status': 404})
                    newstudent = Student.query.filter_by(student_login_id=student_login_id).first()
                    
                    newstudent.pic_path = pic_path
                    db.session.commit()
                    logger.info("Profile picture path stored successfully")
                    return jsonify({
                        'message': 'Profile picture path stored successfully',
                        'status': 200,
                    
                    })
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error adding student information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.student_ns.route('/get/<int:id>')
        class StudentGetByLoginId(Resource):
            @self.student_ns.doc('student/getbyloginId', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    student = Student.query.filter_by(student_login_id=id).first()
                    if not student:
                        logger.warning("No Student found")
                        return jsonify({'message': 'Student not found', 'status': 404})
                    else:
                        student_data = {
                            'id': student.student_id,
                            'first_name': student.first_name,
                            'last_name': student.last_name,
                            'gender': student.gender,
                            'dob': student.dob,
                            'father_name': student.father_name,
                            'mother_name': student.mother_name,
                            'guardian_name': student.guardian_name,
                            'is_kyc_verified': student.is_kyc_verified,
                            'pic_path': student.pic_path,
                            'student_registration_no': student.student_registration_no,
                            'last_modified_datetime': student.last_modified_datetime,
                            'aim': student.aim,
                            'is_active': student.is_active,
                            
                        }
                        logger.info("Student found Successfully")
                        return jsonify({'message': 'Student found Successfully', 'status': 200,'data':student_data}) 
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error editing student information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
            @self.student_ns.route('/getProfile/<int:id>')
            class StudentGetProfile(Resource):
                @self.student_ns.doc('student/getProfile', security='jwt')
                @jwt_required()
                def get(self, id):
                    try:
                        student_login = StudentLogin.query.get(id)
                        student = Student.query.filter_by(student_login_id=id).first()
                        if not student:
                            logger.warning("No Student found")
                            prompt = "**question** in Educational term"
                            return jsonify({'message': 'Student not found', 'status': 404, 'data': {'prompt': prompt, 'user_id': student_login.userid}})
                        
                        student_academic_history = NewStudentAcademicHistory.query.filter_by(student_id=id, is_active=True).order_by(NewStudentAcademicHistory.id.desc()).first()
                        student_address = StudentAddress.query.filter_by(student_id=id, is_active=1).order_by(StudentAddress.address_id.desc()).first()
                        student_subject_preference = SubjectPreference.query.filter_by(student_id=id, is_active=1).order_by(SubjectPreference.subject_preference_id.desc()).first()
                        student_hobby = StudentHobby.query.filter_by(student_id=id, is_active=1).order_by(StudentHobby.id.desc()).first()
                        student_language_known = LanguageKnown.query.filter_by(student_id=id, is_active=1).order_by(LanguageKnown.language_known_id.desc()).first()
                        student_contact = Contact.query.filter_by(student_id=id).order_by(Contact.contact_id.desc()).first()

                      
                        institution_name = entity_name = course_name = subject_name = class_name = None
                        class_id = None

                        if student_academic_history:
                            institution = Institution.query.filter_by(institution_id=student_academic_history.institute_id, is_deleted=False).first()
                            institution_name = institution.institution_name if institution else None
                            if institution:
                                entity = EntityType.query.filter_by(entity_id=institution.entity_id).first()
                                entity_name = entity.entity_type if entity else None
                            class_id = student_academic_history.class_id if student_academic_history else None
                            class_data = ClassMaster.query.filter_by(class_id=class_id, is_deleted=False).first()
                            class_name = class_data.class_name if class_data else None

                        if student_subject_preference:
                            course = CourseMaster.query.filter_by(course_id=student_subject_preference.course_id, is_deleted=False).first()
                            course_name = course.course_name if course else None
                            subject = SubjectMaster.query.filter_by(subject_id=student_subject_preference.subject_id, is_deleted=False).first()
                            subject_name = subject.subject_name if subject else None

                        student_data = {
                            'basic_info': {
                                'id': student.student_id,
                                'first_name': student.first_name,
                                'last_name': student.last_name,
                                'gender': student.gender,
                                'dob': student.dob,
                                'father_name': student.father_name,
                                'mother_name': student.mother_name,
                                'guardian_name': student.guardian_name,
                                'is_kyc_verified': student.is_kyc_verified,
                                'pic_path': student.pic_path,
                                'student_registration_no': student.student_registration_no,
                                'last_modified_datetime': student.last_modified_datetime,
                                'aim': student.aim,
                                'is_active': student.is_active,
                            },
                            'academic_history': {
                                'id': student_academic_history.id if student_academic_history else None,
                                'institution_name': institution_name,
                                'course_id': student_academic_history.course_id if student_academic_history else None,
                                'learning_style': student_academic_history.learning_style if student_academic_history else None,
                                'is_active': student_academic_history.is_active if student_academic_history else None,
                                'institution_type': student_academic_history.institution_type if student_academic_history else None,
                                'institute_id': student_academic_history.institute_id if student_academic_history else None,
                                'board': student_academic_history.board if student_academic_history else None,
                                'state_for_stateboard': student_academic_history.state_for_stateboard if student_academic_history else None,
                                'class_id': student_academic_history.class_id if student_academic_history else None,
                                'year': student_academic_history.year_or_semester if student_academic_history else None,
                                'university_name': student_academic_history.university_name if student_academic_history else None,
                            },
                            'address': {
                                'id': student_address.address_id if student_address else None,
                                'address1': student_address.address1 if student_address else None,
                                'address2': student_address.address2 if student_address else None,
                                'country': student_address.country if student_address else None,
                                'state': student_address.state if student_address else None,
                                'city': student_address.city if student_address else None,
                                'district': student_address.district if student_address else None,
                                'pincode': student_address.pincode if student_address else None,
                                'address_type': student_address.address_type if student_address else None,
                                'is_active': student_address.is_active if student_address else None,
                            },
                            'subject_preference': {
                                'id': student_subject_preference.subject_preference_id if student_subject_preference else None,
                                'course_name': course_name,
                                'subject_name': subject_name,
                                'preference': student_subject_preference.preference if student_subject_preference else None,
                                'score_in_percentage': student_subject_preference.score_in_percentage if student_subject_preference else None,
                                'is_active': student_subject_preference.is_active if student_subject_preference else None
                            },
                            'hobby': {
                                'id': student_hobby.id if student_hobby else None,
                                'hobby_id': student_hobby.hobby_id if student_hobby else None,
                                'is_active': student_hobby.is_active if student_hobby else None
                            },
                            'language_known': {
                                'id': student_language_known.language_known_id if student_language_known else None,
                                'language_id': student_language_known.language_id if student_language_known else None,
                                'proficiency': student_language_known.proficiency if student_language_known else None,
                                'is_active': student_language_known.is_active if student_language_known else None
                            },
                            'contact': {
                                'id': student_contact.contact_id if student_contact else None,
                                'mobile_isd_call': student_contact.mobile_isd_call if student_contact else None,
                                'mobile_no_call': student_contact.mobile_no_call if student_contact else None,
                                'mobile_isd_watsapp': student_contact.mobile_isd_watsapp if student_contact else None,
                                'mobile_no_watsapp': student_contact.mobile_no_watsapp if student_contact else None,
                                'email_id': student_contact.email_id if student_contact else None,
                                'is_active': student_contact.is_active if student_contact else None
                            },
                            'institution': institution_name,
                            'course': course_name,
                            'subject': subject_name,
                            'class': {'id': class_id, 'name': class_name},
                            'entity_name': entity_name,
                            'user_id': student_login.userid
                        }

                        prompt = "Hi I am **first_name** **last_name**. Currently I am studying at **institution** at **address1**, **address2**, **city**, **district**, **state**, **country**, **pincode** in **course** "
                        for key, data in student_data.items():
                            if key in prompt and key not in ['address', 'id']:
                                prompt = prompt.replace(f'**{key}**', str(data))

                        for key, data in student_data.get('address', {}).items():
                            if key in prompt:
                                prompt = prompt.replace(f'**{key}**', str(data))

                        student_data['prompt'] = prompt
                        logger.info("Student found Successfully")
                        return jsonify({'message': 'Student found Successfully', 'status': 200, 'data': student_data}) 
                    except Exception as e:
                    
                            logger.error(f"Error fetching student information: {str(e)}")
                            return jsonify({'message': str(e), 'status': 500})        
        @self.student_ns.route('/edit/<int:id>')
        class StudentEdit(Resource):
            @self.student_ns.doc('student/edit', security='jwt')
            @api.expect(self.student_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    aim = data.get('aim')
                    first_name = data.get('first_name')
                    last_name = data.get('last_name')
                    gender = data.get('gender')
                    dob = data.get('dob')
                    father_name = data.get('father_name')
                    mother_name = data.get('mother_name')
                    guardian_name = data.get('guardian_name')
                    is_kyc_verified = data.get('is_kyc_verified')
                    student_login_id = data.get('student_login_id')
                    current_user_id = get_jwt_identity()
                    pic_path = data.get('pic_path')
                    mobile_no_call = data.get('mobile_no_call')

                    
                    if not first_name:
                        logger.warning("No first_name found")
                        return jsonify({'message': 'Please Provide First Name', 'status': 400})
                    if not last_name:
                        logger.warning("No last_name found")
                        return jsonify({'message': 'Please Provide Last Name', 'status': 400})
                    if not gender:
                        logger.warning("No gender found")
                        return jsonify({'message': 'Please Provide Gender', 'status': 400})
                    if not dob:
                        logger.warning("No dob found")
                        return jsonify({'message': 'Please Provide Date of Birth', 'status': 400})
                    if not father_name:
                        logger.warning("No father_name found")
                        return jsonify({'message': 'Please Provide Father Name', 'status': 400})
                    if not mother_name:
                        logger.warning("No mother_name found")
                        return jsonify({'message': 'Please Provide Mother Name', 'status': 400})

                    
                    student = Student.query.filter_by(student_login_id=id).first()
                    if not student:
                        logger.warning("No Student found")
                        return jsonify({'message': 'Student not found', 'status': 404})
                
                
                    student.aim = aim
                    student.first_name = first_name
                    student.last_name = last_name
                    student.gender = gender
                    student.dob = dob
                    student.father_name = father_name
                    student.mother_name = mother_name
                    student.guardian_name = guardian_name
                    student.is_kyc_verified = is_kyc_verified 
                    student.pic_path = pic_path
                    student.student_login_id = student_login_id
                    student.updated_by = current_user_id
                    student.updated_at = datetime.now()

                    db.session.commit()
                    logger.info("Student updated Successfully")
                    return jsonify({'message': 'Student updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error edting student information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                        
            @self.student_ns.doc('student/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    student = Student.query.get(id)
                    if not student:
                        logger.warning("No Student found")
                        return jsonify({'message': 'Student not found', 'status': 404})
                    else:
                        student_data = {
                            'id': student.student_id,
                            'first_name': student.first_name,
                            'last_name': student.last_name,
                            'gender': student.gender,
                            'dob': student.dob,
                            'father_name': student.father_name,
                            'mother_name': student.mother_name,
                            'guardian_name': student.guardian_name,
                            'is_kyc_verified': student.is_kyc_verified,
                            'pic_path': student.pic_path,
                            'student_registration_no': student.student_registration_no,
                            'last_modified_datetime': student.last_modified_datetime,
                            'aim': student.aim,
                            'is_active': student.is_active,
                            
                        }
                        print(student_data)
                        logger.info("Student found Successfully")
                        return jsonify({'message': 'Student found Successfully', 'status': 200,'data':student_data})
                except Exception as e:
                  
                    logger.error(f"Error fetching student information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                    
                
        @self.student_ns.route('/editstudent/<int:id>')
        class StudentEdit(Resource):
            @self.student_ns.doc('student/editeditstudent', security='jwt')
            @api.expect(self.student_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    aim = data.get('aim')
                    first_name = data.get('first_name')
                    last_name = data.get('last_name')
                    gender = data.get('gender')
                    dob = data.get('dob')
                    father_name = data.get('father_name')
                    mother_name = data.get('mother_name')
                    guardian_name = data.get('guardian_name')
                    is_kyc_verified = data.get('is_kyc_verified')
                    student_login_id = data.get('student_login_id')
                    current_user_id = get_jwt_identity()
                    pic_path = data.get('pic_path')
                    mobile_no_call = data.get('mobile_no_call')

                    if not first_name:
                        logger.warning("No first_name found")
                        return jsonify({'message': 'Please Provide First Name', 'status': 201})
                    if not last_name:
                        logger.warning("No last_name found")
                        return jsonify({'message': 'Please Provide Last Name', 'status': 201})
                    if not gender:
                        logger.warning("No v found")
                        return jsonify({'message': 'Please Provide Gender', 'status': 201})
                    if not dob:
                        logger.warning("No dob found")
                        return jsonify({'message': 'Please Provide Date of Birth', 'status': 201})
                    if not father_name:
                        logger.warning("No v found")
                        return jsonify({'message': 'Please Provide Father Name', 'status': 201})
                    if not mother_name:
                        logger.warning("No mother_name found")
                        return jsonify({'message': 'Please Provide Mother Name', 'status': 201})
                    else:
                        student = Student.query.filter_by(student_id=id).first()
                        if not student:
                            logger.warning("No Student found")
                            return jsonify({'message': 'Student not found', 'status': 404})
                        else:
                            student.aim = aim
                            student.first_name = first_name
                            student.last_name = last_name
                            student.gender = gender
                            student.dob = dob
                            student.father_name = father_name
                            student.mother_name = mother_name
                            student.guardian_name = guardian_name
                            student.is_kyc_verified = False  
                            student.pic_path = pic_path
                            student.student_login_id = student_login_id
                            student.updated_by = current_user_id
                            student.updated_at = datetime.now() 

                            if mobile_no_call:
                                contact = Contact.query.filter_by(student_id=id).first()
                                if not contact:
                                
                                    
                                    contact = Contact(student_id=student.student_id, mobile_no_call=mobile_no_call)
                                    db.session.add(contact)
                                else:
   
                                    contact.mobile_no_call = mobile_no_call
                            db.session.commit()
                            logger.info("Student updated Successfully")
                            return jsonify({'message': 'Student updated successfully', 'status': 200})
                except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error editing student information: {str(e)}")
                        return jsonify({'message': str(e), 'status': 500})
        @self.student_ns.route('delete/<int:id>')
        class StudentDelete(Resource):
            @self.student_ns.doc('student/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        student = Student.query.get(id)
                        if not student:
                            logger.warning("No Student found")
                            return jsonify({'message': 'Student not found', 'status': 404})
                        else:
             
                            student.is_deleted=True
                            db.session.commit()
                            logger.info("Student deleted Successfully")
                            return jsonify({'message': 'Student deleted successfully', 'status': 200})
                    except Exception as e:
                        
                        logger.error(f"Error deleting student information: {str(e)}")
                        return jsonify({'message': str(e), 'status': 500})
                    
        @self.student_ns.route('/activate/<int:id>')
        class StudentActivate(Resource):
            @self.student_ns.doc('student/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    student = Student.query.get(id)
                    if not student:
                        logger.warning("No Student found")
                        return jsonify({'message': 'Student not found', 'status': 404})
                    else:
                        student.is_active = 1
                        db.session.commit()
                        logger.info("Student activated Successfully")
                        return jsonify({'message': 'Student activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error activating student information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.student_ns.route('/deactivate/<int:id>')
        class StudentDeactivate(Resource):
            @self.student_ns.doc('student/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    student = Student.query.get(id)
                    if not student:
                        logger.warning("No Student found")
                        return jsonify({'message': 'Student not found', 'status': 404})
                    else:
                        student.is_active = 0
                        db.session.commit()
                        logger.info("Student deactivated Successfully")
                        return jsonify({'message': 'Student deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error deactivating student information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                    
        @self.student_ns.route('/profile-completion/<int:id>')
        class StudentProfileCompletion(Resource):
            @self.student_ns.doc('student/profile-completion', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    student = Student.query.get(id)
                    if not student:
                        logger.warning("No Student found")
                        return jsonify({'message': 'Student not found', 'status': 404})
                    
                    required_fields = ['first_name', 'last_name', 'gender', 'dob', 'father_name', 'mother_name', 'pic_path']
                    
                    filled_required_fields = sum(1 for field in required_fields if getattr(student, field, None))
                    total_required_fields = len(required_fields)
                    
                    if total_required_fields == 0:
                        return jsonify({'message': 'No required fields defined', 'status': 500}), 500
                    
                    completion_percentage = (filled_required_fields / total_required_fields) * 100
                    logger.info("Profile completion percentage calculated successfully")
                    return jsonify({'message': 'Profile completion percentage calculated successfully', 'status': 200, 'completion_percentage': completion_percentage})
                except Exception as e:
             
                    logger.error(f"Error fetching student profile information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        self.api.add_namespace(self.student_ns)
