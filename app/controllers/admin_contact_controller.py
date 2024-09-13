from datetime import datetime
import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.adminuser import AdminContact

class AdminContactController:
    def __init__(self,api):
        self.api = api
        self.admin_contact_model = api.model('AdminContact', {
            'admin_id': fields.String(required=True, description='Admin Id'),
            'mobile_isd_call': fields.String(required=True, description='Admin Mobile ISD'),
            'mobile_no_call': fields.String(required=True, description='Admin Mobile No'),
            'mobile_isd_watsapp': fields.String(required=True, description='Admin Whatsapp ISD'),
            'mobile_no_watsapp': fields.String(required=True, description='Admin Whatsapp No'),
            'email_id': fields.String(required=True, description='Admin Email Id')
        })
        self.required_fields = ['admin_id', 'mobile_isd_call', 'mobile_no_call', 'mobile_isd_watsapp', 'mobile_no_watsapp', 'email_id']
        self.admin_contact_bp = Blueprint('admin_contact', __name__)
        self.admin_contact_ns = Namespace('admin_contact', description='Admin Contact Details', authorizations=authorizations)
        
        
        self.register_routes()
    def calculate_completion_percentage(self, data):
        filled_fields = sum(1 for field in self.required_fields if field in data and data[field])
        total_required_fields = len(self.required_fields)
        return (filled_fields / total_required_fields) * 100 if total_required_fields > 0 else 0
        
    def register_routes(self):
        @self.admin_contact_ns.route('/list')
        class AdminContactList(Resource):
            @self.admin_contact_ns.doc('admin_contact/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    admin_contactes = AdminContact.query.filter_by(is_active=1).all()
                    admin_contactes_data = []
                    
                    for admin_contact in admin_contactes:
                        admin_contact_data = {
                            'id': admin_contact.admin_contact_id,
                            'admin_id': admin_contact.admin_id,
                            'mobile_isd_call': admin_contact.mobile_isd_call,
                            'mobile_no_call': admin_contact.mobile_no_call,
                            'mobile_isd_watsapp': admin_contact.mobile_isd_watsapp,
                            'mobile_no_watsapp': admin_contact.mobile_no_watsapp,
                            'is_active': admin_contact.is_active
                        }
                        admin_contactes_data.append(admin_contact_data)
                    
                    if not admin_contactes_data:
                        return jsonify({'message': 'No Admin Contact found', 'status': 404})
                    else:
                        return jsonify({'message': 'Admin Contact found Successfully', 'status': 200, 'data': admin_contactes_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
                    
        @self.admin_contact_ns.route('/alldata')
        class AdminContactList(Resource):
            @self.admin_contact_ns.doc('admin_contact/alldata', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    admin_contactes = AdminContact.query.all()
                    admin_contactes_data = []
                    
                    for admin_contact in admin_contactes:
                        admin_contact_data = {
                            'id': admin_contact.admin_contact_id,
                            'admin_id': admin_contact.admin_id,
                            'mobile_isd_call': admin_contact.mobile_isd_call,
                            'mobile_no_call': admin_contact.mobile_no_call,
                            'mobile_isd_watsapp': admin_contact.mobile_isd_watsapp,
                            'mobile_no_watsapp': admin_contact.mobile_no_watsapp,
                            'is_active': admin_contact.is_active
                        }
                        admin_contactes_data.append(admin_contact_data)
                    
                    if not admin_contactes_data:
                        return jsonify({'message': 'No Admin Contact found', 'status': 404})
                    else:                  
                        return jsonify({'message': 'Admin Contact found Successfully', 'status': 200, 'data': admin_contactes_data})
                except Exception as e:
                    return jsonify({'message': str(e), 'status': 500})
        @self.admin_contact_ns.route('/add')
        class AdminContactAdd(Resource):
            @self.admin_contact_ns.doc('admin_contact/add', security='jwt')
            @self.api.expect(self.admin_contact_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    admin_id = data.get('admin_id')
                    mobile_isd_call = data.get('mobile_isd_call')
                    mobile_no_call = data.get('mobile_no_call')
                    mobile_isd_watsapp = data.get('mobile_isd_watsapp')
                    mobile_no_watsapp = data.get('mobile_no_watsapp')
                    email_id = data.get('email_id')
                    
                    current_user_id = get_jwt_identity()
                    if not admin_id :             
                        return jsonify({'message': 'Please Provide Admin Id', 'status': 201})
                    if not mobile_isd_call :              
                        return jsonify({'message': 'Please Provide Mobile ISD', 'status': 201})
                    if not mobile_no_call :               
                        return jsonify({'message': 'Please Provide Mobile No', 'status': 201})
                    if not mobile_isd_watsapp :            
                        return jsonify({'message': 'Please Provide Whatsapp mobile ISD', 'status': 201})                   
                    if not email_id :                  
                        return jsonify({'message': 'Please Provide Email Id', 'status': 201})
                    else:
                        admin_contact = AdminContact(admin_id=admin_id,mobile_isd_call=mobile_isd_call,mobile_no_call=mobile_no_call,mobile_isd_watsapp=mobile_isd_watsapp,mobile_no_watsapp=mobile_no_watsapp,email_id=email_id,is_active = 1,created_by=current_user_id)
                        db.session.add(admin_contact)
                        db.session.commit()                     
                        return jsonify({'message': 'Admin Contact created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()               
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.admin_contact_ns.route('/edit/<int:id>')
        class AdminContactEdit(Resource):
            @self.admin_contact_ns.doc('admin_contact/edit', security='jwt')
            @api.expect(self.admin_contact_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    admin_id = data.get('admin_id')
                    mobile_isd_call = data.get('mobile_isd_call')
                    mobile_no_call = data.get('mobile_no_call')
                    mobile_isd_watsapp = data.get('mobile_isd_watsapp')
                    mobile_no_watsapp = data.get('mobile_no_watsapp')
                    email_id = data.get('email_id')
                    
                    current_user_id = get_jwt_identity()
                    if not admin_id :                    
                        return jsonify({'message': 'Please Provide Admin Id', 'status': 201})
                    if not mobile_isd_call :                 
                        return jsonify({'message': 'Please Provide Mobile ISD', 'status': 201})
                    if not mobile_no_call :                  
                        return jsonify({'message': 'Please Provide Mobile No', 'status': 201})
                    if not mobile_isd_watsapp :                       
                        return jsonify({'message': 'Please Provide Whatsapp mobile ISD', 'status': 201})
                   
                    else:                       
                        admin_contact = AdminContact.query.filter_by(admin_id=id).first()
                        if not admin_contact:                            
                            return jsonify({'message': 'Admin Contact not found', 'status': 404})
                        else:
                            admin_contact.admin_id = admin_id
                            admin_contact.mobile_isd_call = mobile_isd_call
                            admin_contact.mobile_no_call = mobile_no_call
                            admin_contact.mobile_isd_watsapp = mobile_isd_watsapp
                            admin_contact.mobile_no_watsapp = mobile_no_watsapp
                            admin_contact.is_active = 1
                          
                            admin_contact.updated_by=current_user_id
                            db.session.commit()                          
                            return jsonify({'message': 'Admin Contact updated successfully', 'status': 200})
                except Exception as e:
                        db.session.rollback()
                    
                        return jsonify({'message': str(e), 'status': 500})
                    
            @self.admin_contact_ns.doc('admin_contact/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
               
                    admin_contact = AdminContact.query.filter_by(admin_id=id).first()
                    if not admin_contact:
                      
                        return jsonify({'message': 'Admin Contact not found', 'status': 404})
                    else:
                        admin_contact_data = {
                            'id': admin_contact.admin_contact_id,
                            'admin_id': admin_contact.admin_id,
                            'mobile_isd_call': admin_contact.mobile_isd_call,
                            'mobile_no_call': admin_contact.mobile_no_call,
                            'mobile_isd_watsapp': admin_contact.mobile_isd_watsapp,
                            'mobile_no_watsapp': admin_contact.mobile_no_watsapp,
                            'email_id': admin_contact.email_id,
                            'is_active': admin_contact.is_active
                            
                        }
                        print(admin_contact_data)
                      
                        return jsonify({'message': 'Admin Contact found Successfully', 'status': 200,'data':admin_contact_data})
                except Exception as e:
                    
             
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.admin_contact_ns.route('/activate/<int:id>')
        class AdminContactActivate(Resource):
            @self.admin_contact_ns.doc('admin_contact/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    admin_contact = AdminContact.query.get(id)
                    if not admin_contact:
                  
                        return jsonify({'message': 'Admin Contact not found', 'status': 404})
                    else:
                        admin_contact.is_active = 1
                        db.session.commit()
        
                        return jsonify({'message': 'Admin Contact activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
        
                    return jsonify({'message': str(e), 'status': 500})

        @self.admin_contact_ns.route('/deactivate/<int:id>')
        class AdminContactDeactivate(Resource):
            @self.admin_contact_ns.doc('admin_contact/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    admin_contact = AdminContact.query.get(id)
                    if not admin_contact:
                  
                        return jsonify({'message': 'Admin Contact not found', 'status': 404})
                    else:
                        admin_contact.is_active = 0
                        db.session.commit()
               
                        return jsonify({'message': 'Admin Contact deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                 
                    return jsonify({'message': str(e), 'status': 500})

            
        self.api.add_namespace(self.admin_contact_ns)