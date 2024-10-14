from datetime import datetime
import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations
from app.controllers.admin_profession_controller import AdminProfessionController
from app.controllers.admin_language_known_controller import AdminLanguageKnownController
from app.controllers.admin_contact_controller import AdminContactController
from app.controllers.admin_basicinfo_controller import AdminBasicInformationController
from flask_restx import Api, Namespace, Resource, fields
from app.controllers import admin_address_controller,admin_contact_controller,admin_basicinfo_controller,admin_language_known_controller,admin_profession_controller
from app.controllers.admin_address_controller import AdminAddressController
from app.models.adminuser import *
from app.models.student import *
class CalculateCompletion:
    def __init__(self,api):
        self.api = api
        
        
        self.calculate_completion_bp = Blueprint('calculate_completion', __name__)
        self.calculate_completion_ns = Namespace('calculate_completion', description='completion Details', authorizations=authorizations)
        
        self.register_routes()
    
    def register_routes(self):
        @self.calculate_completion_ns.route('/list')
        class CalculateCompletionList(Resource):       
            @self.calculate_completion_ns.doc('calculate-completion/list', security='jwt')
            @jwt_required()
            def calculate_completion_percentage(self, admin_id):
       
                admin_addresses = AdminAddress.query.filter_by(admin_id=admin_id).all()
                self.required_fields = ['admin_id', 'address1', 'address2', 'country', 'state', 'city', 'district', 'pincode', 'address_type']
                if not admin_addresses:
                    return []

                results = []
                total_required_fields = len(self.required_fields)

                for admin_address in admin_addresses:
                    filled_fields = sum(1 for field in self.required_fields if getattr(admin_address, field, None))
                    
                    if total_required_fields > 0:
                        percentage_filled = (filled_fields / total_required_fields) * 100
                        adjusted_percentage = (percentage_filled / 100) * 26.47  # Adjusted based on total required fields
                        results.append(round(adjusted_percentage, 2))
                    else:
                        results.append(0)
             
                return results
            def required_fld(self):
                self.required_fields = ['admin_id', 'address1', 'address2', 'country', 'state', 'city', 'district', 'pincode', 'address_type']
                total_required_fields = len(self.required_fields)
                return total_required_fields
            def csp_for_basicinfo(self, admin_id):
                self.required_fields = ['department_id', 'first_name', 'last_name', 'gender', 'dob', 'father_name', 'mother_name', 'guardian_name', 'pic_path', 'admin_login_id']
                
                admin_basic_infos = AdminBasicInformation.query.filter_by(admin_id=admin_id).all()
                
                if not admin_basic_infos:
                    return []

                results = []
                total_required_fields = len(self.required_fields)

                for admin_basic_info in admin_basic_infos:
                    filled_fields = sum(1 for field in self.required_fields if getattr(admin_basic_info, field, None))
                    
                    if total_required_fields > 0:
                        percentage_filled = (filled_fields / total_required_fields) * 100
                        adjusted_percentage = (percentage_filled / 100) * 29.41  # Adjusted based on total required fields
                        results.append(round(adjusted_percentage, 2))
                    else:
                        results.append(0)

                return results
            def bsicinfo_rf(self):
                self.required_fields = ['department_id', 'first_name', 'last_name', 'gender', 'dob', 'father_name', 'mother_name', 'guardian_name', 'pic_path', 'admin_login_id']
                total_required_fields = len(self.required_fields)
                return total_required_fields
            def csp_for_contact(self, admin_id):
                required_fields = ['admin_id', 'mobile_isd_call', 'mobile_no_call', 'mobile_isd_watsapp', 'mobile_no_watsapp', 'email_id']
                admin_contacts = AdminContact.query.filter_by(admin_id=admin_id).all()
                
                if not admin_contacts:
                    return []

                results = []
                total_required_fields = len(required_fields)

                for admin_contact in admin_contacts:
                    filled_fields = sum(1 for field in required_fields if getattr(admin_contact, field, None))
                    
                    if total_required_fields > 0:
                        percentage_filled = (filled_fields / total_required_fields) * 100
                        adjusted_percentage = (percentage_filled / 100) * 17.64  # Adjusted weight for AdminContactController
                        results.append(round(adjusted_percentage, 2))
                    else:
                        results.append(0)

                return results
            def contact_rf(self):
                required_fields = ['admin_id', 'mobile_isd_call', 'mobile_no_call', 'mobile_isd_watsapp', 'mobile_no_watsapp', 'email_id']
                total_required_fields = len(required_fields)
                return total_required_fields
            def csp_for_language_known(self, admin_id):
                required_fields = ['admin_id', 'language_id', 'proficiency']
                admin_languages = AdminLanguageKnown.query.filter_by(admin_id=admin_id).all()
                
                if not admin_languages:
                    return []

                results = []
                total_required_fields = len(required_fields)

                for admin_language in admin_languages:
                    filled_fields = sum(1 for field in required_fields if getattr(admin_language, field, None))
                    
                    if total_required_fields > 0:
                        percentage_filled = (filled_fields / total_required_fields) * 100
                        adjusted_percentage = (percentage_filled / 100) *  8.82  # Adjusted weight for AdminLanguageKnownController
                        results.append(round(adjusted_percentage, 2))
                    else:
                        results.append(0)

                return results
            
            
            def lang_known_rf(self):
                required_fields = ['admin_id', 'language_id', 'proficiency']
                total_required_fields = len(required_fields)
                return total_required_fields
            def csp_for_profession(self, admin_id):
                required_fields = ['admin_id', 'institution_id', 'course_id', 'subject_id']
                admin_professions = AdminProfession.query.filter_by(admin_id=admin_id).all()
                
                if not admin_professions:
                    return []

                results = []
                total_required_fields = len(required_fields)

                for admin_profession in admin_professions:
                    filled_fields = sum(1 for field in required_fields if getattr(admin_profession, field, None))
                    
                    if total_required_fields > 0:
                        percentage_filled = (filled_fields / total_required_fields) * 100
                        adjusted_percentage = (percentage_filled / 100) *  11.76 # Adjusted weight for AdminProfessionController
                        results.append(round(adjusted_percentage, 2))
                    else:
                        results.append(0)

                return results
            
            def profession_rf(self):
                required_fields = ['admin_id', 'institution_id', 'course_id', 'subject_id']
                total_required_fields = len(required_fields)
                return total_required_fields
            def csp_for_description(self, admin_id):
                required_fields = ['admin_id', 'description']
                admin_description = AdminDescription.query.filter_by(admin_id=admin_id).all()
                
                if not admin_description:
                    return []

                results = []
                total_required_fields = len(required_fields)

                for admin_profession in admin_description:
                    filled_fields = sum(1 for field in required_fields if getattr(admin_profession, field, None))
                    
                    if total_required_fields > 0:
                        percentage_filled = (filled_fields / total_required_fields) * 100
                        adjusted_percentage = (percentage_filled / 100) *  5.88 # Adjusted weight for AdminProfessionController
                        results.append(round(adjusted_percentage, 2))
                    else:
                        results.append(0)

                return results
            
            def description_rf(self):
                required_fields = ['admin_id', 'description']
                total_required_fields = len(required_fields)
                return total_required_fields
            @jwt_required()
            def get(self):
                try:
                    required_fields = {
                        'AdminAddressController': self.required_fld(),
                        'AdminBasicInformationController': self.bsicinfo_rf(),
                        'AdminLanguageKnownController': self.lang_known_rf(),
                        'AdminContactController': self.contact_rf(),
                        'AdminProfessionController': self.profession_rf(),
                        'AdminDescription':self.description_rf()
                    }

                    total_required_fields = sum(required_fields.values())

                    controller_weights = {}

                    for controller, count in required_fields.items():
                        weight = (count / total_required_fields) * 100
                        controller_weights[controller] = weight

                    for controller, weight in controller_weights.items():
                        print(f"{controller}: {weight}%")
                
                    
                    current_admin_id = get_jwt_identity() 
          
                    results = {
                        'AdminAddressController': self.calculate_completion_percentage(current_admin_id),
                        'AdminBasicInformationController': self.csp_for_basicinfo(current_admin_id),
                        'AdminContactController': self.csp_for_contact(current_admin_id),
                        'AdminLanguageKnownController': self.csp_for_language_known(current_admin_id),
                        'AdminProfessionController': self.csp_for_profession(current_admin_id),
                        'AdminDescriptionController': self.csp_for_description(current_admin_id)
                    }
                    
                    overall_percentage = [value[0] for value in results.values() if value]

                    print(overall_percentage)
                    sum_results = 0
                    for percentage in overall_percentage:
                        sum_results = sum_results + percentage

                    print("Overall percentage:", sum_results)

                    return jsonify({
                        'results': results,
                        'overall_percentage': sum_results
                    })
                except Exception as e:
                   
                    return jsonify({'message': str(e), 'status': 500})

                
        @self.calculate_completion_ns.route('/student-list')
        class StudentCalculateCompletionList(Resource):       
            @self.calculate_completion_ns.doc('calculate-completion-for-student/student-list', security='jwt')
            @jwt_required()
            def csp_for_basicinfo(self, student_id):
                required_fields = [
                        'first_name',
                        'last_name',
                        'gender',
                        'dob',
                        'father_name',
                        'mother_name',
                        'is_kyc_verified',
                        'student_login_id'
                    ]
                student_basicinfo = Student.query.filter_by(student_id=student_id).all()
                
                if not student_basicinfo:
                    return []

                results = []
                total_required_fields = len(required_fields)

                for admin_profession in student_basicinfo:
                    filled_fields = sum(1 for field in required_fields if getattr(admin_profession, field, None))
                    
                    if total_required_fields > 0:
                        percentage_filled = (filled_fields / total_required_fields) * 100
                        adjusted_percentage = (percentage_filled / 100) *  21.052631578947366 # Adjusted weight for AdminProfessionController
                        results.append(round(adjusted_percentage, 2))
                    else:
                        results.append(0)

                return results
            
            def studentinfo_rf(self):
                required_fields = [
                        'first_name',
                        'last_name',
                        'gender',
                        'dob',
                        'father_name',
                        'mother_name',
                        'is_kyc_verified',
                        'student_login_id'
                    ]
                total_required_fields = len(required_fields)
                return total_required_fields
            def csp_for_contact(self, student_id):
                required_fields = [
                        'student_id',
                        'mobile_isd_call',
                        'mobile_no_call',
                        'mobile_isd_watsapp',
                        'email_id'
                    ]
                student_contact = Contact.query.filter_by(student_id=student_id).all()
                
                if not student_contact:
                    return []

                results = []
                total_required_fields = len(required_fields)

                for admin_profession in student_contact:
                    filled_fields = sum(1 for field in required_fields if getattr(admin_profession, field, None))
                    
                    if total_required_fields > 0:
                        percentage_filled = (filled_fields / total_required_fields) * 100
                        adjusted_percentage = (percentage_filled / 100) *  13.157894736842104 
                        results.append(round(adjusted_percentage, 2))
                    else:
                        results.append(0)

                return results
            
            def contact_rf(self):
                required_fields = [
                        'student_id',
                        'mobile_isd_call',
                        'mobile_no_call',
                        'mobile_isd_watsapp',
                        'email_id'
                    ]
                total_required_fields = len(required_fields)
                return total_required_fields
            def csp_for_hobby(self, student_id):
                required_fields = [
                    'student_id',
                    'hobby_id'
                ]
                student_hobby = StudentHobby.query.filter_by(student_id=student_id).all()
                
                if not student_hobby:
                    return []

                results = []
                total_required_fields = len(required_fields)

                for admin_profession in student_hobby:
                    filled_fields = sum(1 for field in required_fields if getattr(admin_profession, field, None))
                    
                    if total_required_fields > 0:
                        percentage_filled = (filled_fields / total_required_fields) * 100
                        adjusted_percentage = (percentage_filled / 100) *  5.263157894736842 
                        results.append(round(adjusted_percentage, 2))
                    else:
                        results.append(0)

                return results
            
            def hobby_rf(self):
                required_fields = [
                    'student_id',
                    'hobby_id'
                ]
                total_required_fields = len(required_fields)
                return total_required_fields
            def csp_for_subject_preference(self, student_id):
                required_fields= [
                    'student_id',
                    'course_id',
                    'subject_id',
                    'preference',
                    'score_in_percentage'
                ]
                student_subject = SubjectPreference.query.filter_by(student_id=student_id).all()
                
                if not student_subject:
                    return []

                results = []
                total_required_fields = len(required_fields)

                for admin_profession in student_subject:
                    filled_fields = sum(1 for field in required_fields if getattr(admin_profession, field, None))
                    
                    if total_required_fields > 0:
                        percentage_filled = (filled_fields / total_required_fields) * 100
                        adjusted_percentage = (percentage_filled / 100) *  13.157894736842104 
                        results.append(round(adjusted_percentage, 2))
                    else:
                        results.append(0)

                return results
            
            def studentsubject_rf(self):
                required_fields= [
                    'student_id',
                    'course_id',
                    'subject_id',
                    'preference',
                    'score_in_percentage'
                ]
                total_required_fields = len(required_fields)
                return total_required_fields
            def csp_for_acedemic(self, student_id):
                required_fields= [
                    'student_id',
                    'institution_id',
                    'course_id',
                    'starting_date',
                    'ending_date',
                    'learning_style'
                ]
                student_acedemic = AcademicHistory.query.filter_by(student_id=student_id).all()
                
                if not student_acedemic:
                    return []

                results = []
                total_required_fields = len(required_fields)

                for admin_profession in student_acedemic:
                    filled_fields = sum(1 for field in required_fields if getattr(admin_profession, field, None))
                    
                    if total_required_fields > 0:
                        percentage_filled = (filled_fields / total_required_fields) * 100
                        adjusted_percentage = (percentage_filled / 100) *  15.789473684210526 
                        results.append(round(adjusted_percentage, 2))
                    else:
                        results.append(0)

                return results
            
            def acedemic_rf(self):
                required_fields= [
                    'student_id',
                    'institution_id',
                    'course_id',
                    'starting_date',
                    'ending_date',
                    'learning_style'
                ]
                total_required_fields = len(required_fields)
                return total_required_fields
            def csp_for_address(self, student_id):
                required_fields= [
                        'student_id',
                        'address1',
                        'address2',
                        'country',
                        'state',
                        'city',
                        'district',
                        'pincode',
                        'address_type'
                    ]
                student_address = StudentAddress.query.filter_by(student_id=student_id).all()
                
                if not student_address:
                    return []

                results = []
                total_required_fields = len(required_fields)

                for admin_profession in student_address:
                    filled_fields = sum(1 for field in required_fields if getattr(admin_profession, field, None))
                    
                    if total_required_fields > 0:
                        percentage_filled = (filled_fields / total_required_fields) * 100
                        adjusted_percentage = (percentage_filled / 100) * 23.684210526315788 
                        results.append(round(adjusted_percentage, 2))
                    else:
                        results.append(0)

                return results
            
            def address_rf(self):
                required_fields= [
                        'student_id',
                        'address1',
                        'address2',
                        'country',
                        'state',
                        'city',
                        'district',
                        'pincode',
                        'address_type'
                    ]
                total_required_fields = len(required_fields)
                return total_required_fields
            def csp_for_langknown(self, student_id):
                required_fields = [
                    'student_id',
                    'language_id',
                    'proficiency'
                ]
                student_language = LanguageKnown.query.filter_by(student_id=student_id).all()
                
                if not student_language:
                    return []

                results = []
                total_required_fields = len(required_fields)

                for admin_profession in student_language:
                    filled_fields = sum(1 for field in required_fields if getattr(admin_profession, field, None))
                    
                    if total_required_fields > 0:
                        percentage_filled = (filled_fields / total_required_fields) * 100
                        adjusted_percentage = (percentage_filled / 100) *  7.894736842105263 
                        results.append(round(adjusted_percentage, 2))
                    else:
                        results.append(0)

                return results
            
            def langknown_rf(self):
                required_fields = [
                    'student_id',
                    'language_id',
                    'proficiency'
                ]
                total_required_fields = len(required_fields)
                return total_required_fields
            @jwt_required()
            def get(self):
                try:
                    required_fields = {
                        'StudentController': self.studentinfo_rf(),
                        'StudentContactController': self.contact_rf(),
                        'StudentHobby': self.hobby_rf(),
                        'StudentLangknown': self.langknown_rf(),
                        'StudentPreference': self.studentsubject_rf(),
                        'StudentAcademicHistory': self.acedemic_rf(),
                        'StudentAddress': self.address_rf(),
                    }

                    total_required_fields = sum(required_fields.values())

                    controller_weights = {}

                    for controller, count in required_fields.items():
                        weight = (count / total_required_fields) * 100
                        controller_weights[controller] = weight

                    for controller, weight in controller_weights.items():
                        print(f"{controller}: {weight}%")
                
                    
                    current_admin_id = get_jwt_identity() 

                    results = {
                        'StudentAddressController': self.csp_for_address(current_admin_id),
                        'StudentBasicInformationController': self.csp_for_basicinfo(current_admin_id),
                        'StudentContactController': self.csp_for_contact(current_admin_id),
                        'StudentLanguageKnownController': self.csp_for_langknown(current_admin_id),
                        'SubjectProfessionController': self.csp_for_subject_preference(current_admin_id),
                        'StudentAcedemicHistory': self.csp_for_acedemic(current_admin_id),
                        'StudentHobby': self.csp_for_hobby(current_admin_id)
                    }
                    
                    overall_percentage = [value[0] for value in results.values() if value]

                    print(overall_percentage)
                    sum_results = 0
                    for percentage in overall_percentage:
                        sum_results = sum_results + percentage

                    print("Overall percentage:", sum_results)

                  
                    return jsonify({
                        'results': results,
                        'overall_percentage': sum_results
                    })
                except Exception as e:
                   
           
                    return jsonify({'message': str(e), 'status': 500})
        


        self.api.add_namespace(self.calculate_completion_ns)