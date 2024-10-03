from datetime import datetime
import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.student import Contact

class StudentContactController:
    def __init__(self,api):
        self.api = api
        self.student_contact_model = api.model('StudentContact', {
            'student_id': fields.String(required=True, description='Student Id'),
            'mobile_isd_call': fields.String(required=True, description='Student Mobile ISD'),
            'mobile_no_call': fields.String(required=True, description='Student Mobile No'),
            'mobile_isd_watsapp': fields.String(required=True, description='Student Whatsapp ISD'),
            'mobile_no_watsapp': fields.String(required=False, description='Student Whatsapp No'),
            'email_id': fields.String(required=True, description='Student Email Id')
        })
        
        self.student_contact_bp = Blueprint('student_contact', __name__)
        self.student_contact_ns = Namespace('student_contact', description='Student Contact Details', authorizations=authorizations)
        
        self.register_routes()

        
    def register_routes(self):
        @self.student_contact_ns.route('/list')
        class StudentContactList(Resource):
            @self.student_contact_ns.doc('student_contact/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    student_contactes = Contact.query.filter_by(is_active=1).all()
                    student_contactes_data = []
                    
                    for student_contact in student_contactes:
                        student_contact_data = {
                            'id': student_contact.contact_id,
                            'student_id': student_contact.student_id,
                            'mobile_isd_call': student_contact.mobile_isd_call,
                            'mobile_no_call': student_contact.mobile_no_call,
                            'mobile_isd_watsapp': student_contact.mobile_isd_watsapp,
                            'mobile_no_watsapp': student_contact.mobile_no_watsapp,
                            'email_id': student_contact.email_id,
                            'is_active': student_contact.is_active
                        }
                        student_contactes_data.append(student_contact_data)
                    
                    if not student_contactes_data:
                
                        return jsonify({'message': 'No StudentContact found', 'status': 404})
                    else:
                   
                        return jsonify({'message': 'StudentContactes found Successfully', 'status': 200, 'data': student_contactes_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
                    
        @self.student_contact_ns.route('/alldata')
        class StudentContactList(Resource):
            @self.student_contact_ns.doc('student_contact/alldata', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    student_contactes = Contact.query.all()
                    student_contactes_data = []
                    
                    for student_contact in student_contactes:
                        student_contact_data = {
                            'id': student_contact.contact_id,
                            'student_id': student_contact.student_id,
                            'mobile_isd_call': student_contact.mobile_isd_call,
                            'mobile_no_call': student_contact.mobile_no_call,
                            'mobile_isd_watsapp': student_contact.mobile_isd_watsapp,
                            'mobile_no_watsapp': student_contact.mobile_no_watsapp,
                            'email_id': student_contact.email_id,
                            'is_active': student_contact.is_active
                        }
                        student_contactes_data.append(student_contact_data)
                    
                    if not student_contactes_data:
          
                        return jsonify({'message': 'No StudentContact found', 'status': 404})
                    else:
                    
                        return jsonify({'message': 'StudentContactes found Successfully', 'status': 200, 'data': student_contactes_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
        @self.student_contact_ns.route('/add')
        class StudentContactAdd(Resource):
            @self.student_contact_ns.doc('student_contact/add', security='jwt')
            @self.api.expect(self.student_contact_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    student_id = data.get('student_id')
                    mobile_isd_call = data.get('mobile_isd_call')
                    mobile_no_call = data.get('mobile_no_call')
                    mobile_isd_watsapp = data.get('mobile_isd_watsapp')
                    mobile_no_watsapp = data.get('mobile_no_watsapp')
                    email_id = data.get('email_id')
                    current_user_id = get_jwt_identity()
                    student_contact = Contact.query.filter_by(email_id=email_id).first()
                    if not student_id :

                        return jsonify({'message': 'Please Provide Student Id', 'status': 201})
                    if not mobile_isd_call :
            
                        return jsonify({'message': 'Please Provide Mobile ISD', 'status': 201})
                    if not mobile_no_call :
                  
                        return jsonify({'message': 'Please Provide Mobile No', 'status': 201})
                    if not mobile_isd_watsapp :
                 
                        return jsonify({'message': 'Please Provide Whatsapp mobile ISD', 'status': 201})
               
                    if not email_id :
                
                        return jsonify({'message': 'Please Provide Email Id', 'status': 201})
                    if student_contact:
                  
                        return jsonify({'message': 'Email Already exist', 'status': 500})
                    else:
                        student_contact = Contact(student_id=student_id,mobile_isd_call=mobile_isd_call,mobile_no_call=mobile_no_call,mobile_isd_watsapp=mobile_isd_watsapp,mobile_no_watsapp=mobile_no_watsapp,email_id=email_id,is_active = 1,created_by=current_user_id)
                        db.session.add(student_contact)
                        db.session.commit()
               
                        return jsonify({'message': 'Student Contact created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
      
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.student_contact_ns.route('/edit/<int:id>')
        class StudentContactEdit(Resource):
            @self.student_contact_ns.doc('student_contact/edit', security='jwt')
            @api.expect(self.student_contact_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    student_id = data.get('student_id')
                    mobile_isd_call = data.get('mobile_isd_call')
                    mobile_no_call = data.get('mobile_no_call')
                    mobile_isd_watsapp = data.get('mobile_isd_watsapp')
                    mobile_no_watsapp = data.get('mobile_no_watsapp')
                    email_id = data.get('email_id')
                    current_user_id = get_jwt_identity()
                    student_contact_data = Contact.query.filter_by(email_id=email_id).first()
                    if not student_id :
                 
                        return jsonify({'message': 'Please Provide Student Id', 'status': 201})
                    if not mobile_isd_call :
                     
                        return jsonify({'message': 'Please Provide Mobile ISD', 'status': 201})
                    if not mobile_no_call :
         
                        return jsonify({'message': 'Please Provide Mobile No', 'status': 201})
                    if not mobile_isd_watsapp :
                    
                        return jsonify({'message': 'Please Provide Whatsapp mobile ISD', 'status': 201})
                
                    else:
                      
                        student_contact = Contact.query.filter_by(student_id=id).first()
                        if not student_contact:
                     
                            return jsonify({'message': 'Student Contact not found', 'status': 404})
                        else:
                            
                            student_contact.student_id = student_id
                            student_contact.mobile_isd_call = mobile_isd_call
                            student_contact.mobile_no_call = mobile_no_call
                            student_contact.mobile_isd_watsapp = mobile_isd_watsapp
                            student_contact.mobile_no_watsapp = mobile_no_watsapp
                          
                            student_contact.is_active = 1
                            student_contact.updated_by = current_user_id
                            db.session.commit()
               
                            return jsonify({'message': 'Student Contact updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
               
                    return jsonify({'message': str(e), 'status': 500})
                        
            @self.student_contact_ns.doc('student_contact/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
        
                    student_contact = Contact.query.filter_by(student_id=id).first()
                    if not student_contact:
                 
                        return jsonify({'message': 'Student Contact not found', 'status': 404})
                    else:
                        student_contact_data = {
                                'id': student_contact.contact_id,
                                'student_id': student_contact.student_id,
                                'mobile_isd_call': student_contact.mobile_isd_call,
                                'mobile_no_call': student_contact.mobile_no_call,
                                'mobile_isd_watsapp': student_contact.mobile_isd_watsapp,
                                'mobile_no_watsapp': student_contact.mobile_no_watsapp,
                                'email_id': student_contact.email_id,
                                'is_active': student_contact.is_active
                                
                            }
                        print(student_contact_data)
               
                        return jsonify({'message': 'Student Contact found Successfully', 'status': 200,'data':student_contact_data})
                except Exception as e:
 
                    return jsonify({'message': str(e), 'status': 500})
        @self.student_contact_ns.route('/activate/<int:id>')
        class StudentConatactActivate(Resource):
            @self.student_contact_ns.doc('student/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    student = Contact.query.get(id)
                    if not student:
     
                        return jsonify({'message': 'Student Contact not found', 'status': 404})
                    else:
                        student.is_active = 1
                        db.session.commit()
  
                        return jsonify({'message': 'Student contact activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()

                    return jsonify({'message': str(e), 'status': 500})

        @self.student_contact_ns.route('/deactivate/<int:id>')
        class StudentConatactDeactivate(Resource):
            @self.student_contact_ns.doc('student/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    student = Contact.query.get(id)
                    if not student:
            
                        return jsonify({'message': 'Student Contact not found', 'status': 404})
                    else:
                        student.is_active = 0
                        db.session.commit()
            
                        return jsonify({'message': 'Student Contact deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
       
                    return jsonify({'message': str(e), 'status': 500})
        self.api.add_namespace(self.student_contact_ns)
                
                

        
        