from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.student import Contact, StudentAddress, Student, AcademicHistory  # Adjust the import based on your model location
from sqlalchemy import desc

class ProfileController:
    def __init__(self, api):
        self.api = api
        self.profile_ns = Namespace('profile', description='Student Profile Data', authorizations=authorizations)
        self.profile_bp = Blueprint('profile', __name__)
        self.register_routes()
        
    def register_routes(self):
        @self.profile_ns.route('/check_profile')
        class CheckProfile(Resource):
            @self.profile_ns.doc('profile/check', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    current_user_id = get_jwt_identity()  
                    
                    student = Student.query.filter_by(student_login_id=current_user_id, is_deleted=False).first()
                    if not student:
               
                        return jsonify({'message': 'Student not found', 'status': 404})
                    
                    
                    basic_info_complete = all([
                        student.first_name,
                        student.last_name,
                        student.gender,
                        student.dob,
                        student.father_name,
                        student.mother_name,
                        student.is_kyc_verified is not None
                    ])
                    print("Basic Info Complete:", basic_info_complete)

                
                    contact = Contact.query.filter_by(student_id=current_user_id, is_active=1).first()
                    contact_complete = contact and all([
                        contact.email_id,
                        contact.mobile_isd_call,
                        contact.mobile_no_call,
                        contact.mobile_isd_watsapp,
                        contact.mobile_no_watsapp
                    ])
                    print("Contact Complete:", contact_complete)

                
                    address = StudentAddress.query.filter_by(student_id=current_user_id, is_active=1).all()
                    address_complete = len(address) > 0 and all([
                        addr.address1 and addr.country and addr.state and addr.city and addr.district and addr.pincode
                        for addr in address
                    ])
                    print("Address Complete:", address_complete)

                
                    academic_history = AcademicHistory.query.filter_by(student_id=current_user_id, is_active=1).all()
                    academic_history_complete = len(academic_history) > 0 and all([
                        hist.institution_id and hist.course_id and hist.starting_date and hist.ending_date and hist.learning_style
                        for hist in academic_history
                    ])
                    print("Academic History Complete:", academic_history_complete)

                
                    profile_complete = basic_info_complete and contact_complete and address_complete and academic_history_complete
                    print("Profile Complete:", profile_complete)

                    if profile_complete:
                       
                        return jsonify({'message': 'Profile is complete','status': 200,'is_complete': True})
                    else:
             
                        return jsonify({'message': 'Profile is incomplete', 'status': 400,'is_complete': False})
                except Exception as e:
                    db.session.rollback()
           
                    return jsonify({'message': str(e), 'status': 500})
        self.api.add_namespace(self.profile_ns)