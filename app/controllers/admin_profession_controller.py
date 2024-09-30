from datetime import datetime
import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.adminuser import AdminProfession

class AdminProfessionController:
    def __init__(self,api):
        self.api = api
        self.admin_profession_model = api.model('AdminProfession', {
            'admin_id': fields.String(required=True, description='Admin Id'),
            'institution_id': fields.String(required=True, description='Institute Id'),
            'course_id': fields.String(required=True, description='Course Id'),
            'subject_id': fields.String(required=True, description='Subject Id')
        })
        self.required_fields = ['admin_id', 'institution_id', 'course_id', 'subject_id']
        self.admin_profession_bp = Blueprint('admin_profession', __name__)
        self.admin_profession_ns = Namespace('admin_profession', description='Admin Profession Details', authorizations=authorizations)
        
       
        self.register_routes()
    
   
    def register_routes(self):
        @self.admin_profession_ns.route('/list')
        class AdminProfessionList(Resource):
            @self.admin_profession_ns.doc('admin_profession/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    admin_professiones = AdminProfession.query.filter_by(is_active=1).all()
                    admin_professiones_data = []
                    
                    for admin_profession in admin_professiones:
                        admin_profession_data = {
                            'id': admin_profession.id,
                            'admin_id': admin_profession.admin_id,
                            'institution_id': admin_profession.institution_id,
                            'course_id':admin_profession.course_id,
                            'subject_id': admin_profession.subject_id, 
                            'is_active': admin_profession.is_active  
                        }
                        admin_professiones_data.append(admin_profession_data)
                    
                    if not admin_professiones_data:
                        
                        return jsonify({'message': 'No Admin Profession found', 'status': 404})
                    else:
            
                        return jsonify({'message': 'Admin Professions found Successfully', 'status': 200, 'data': admin_professiones_data})
                except Exception as e:
 
                    return jsonify({'message': str(e), 'status': 500})
        @self.admin_profession_ns.route('/alldata')
        class AdminProfessionList(Resource):       
            @self.admin_profession_ns.doc('admin_profession/alldata', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    admin_professiones = AdminProfession.query.all()
                    admin_professiones_data = []
                    
                    for admin_profession in admin_professiones:
                        admin_profession_data = {
                            'id': admin_profession.id,
                            'admin_id': admin_profession.admin_id,
                            'institution_id': admin_profession.institution_id,
                            'course_id':admin_profession.course_id,
                            'subject_id': admin_profession.subject_id, 
                            'is_active': admin_profession.is_active  
                        }
                        admin_professiones_data.append(admin_profession_data)
                    
                    if not admin_professiones_data:
                      
                        return jsonify({'message': 'No Admin Profession found', 'status': 404})
                    else:
           
                        return jsonify({'message': 'Admin Professions found Successfully', 'status': 200, 'data': admin_professiones_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
        @self.admin_profession_ns.route('/add')
        class AdminProfessionAdd(Resource):
            @self.admin_profession_ns.doc('admin_profession/add', security='jwt')
            @self.api.expect(self.admin_profession_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    admin_id = data.get('admin_id')
                    institution_id = data.get('institution_id')
                    course_id = data.get('course_id')
                    subject_id = data.get('subject_id')
                    current_user_id = get_jwt_identity()
                    if not admin_id :
                 
                        return jsonify({'message': 'Please Provide Admin Id', 'status': 201})
                    if not institution_id :
                     
                        return jsonify({'message': 'Please Provide Institute Id', 'status': 201})
                    if not course_id :
                  
                        return jsonify({'message': 'Please Provide Course Id', 'status': 201})
                    if not subject_id :
                    
                        return jsonify({'message': 'Please Provide Subject Id', 'status': 201})
                    else:
                        admin_profession = AdminProfession(admin_id=admin_id,institution_id=institution_id,course_id=course_id,subject_id=subject_id,is_active=1,created_by=current_user_id)
                        db.session.add(admin_profession)
                        db.session.commit()
                 
                        return jsonify({'message': 'Admin Profession created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
       
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.admin_profession_ns.route('/edit/<string:id>')
        class AdminProfessionEdit(Resource):
            @self.admin_profession_ns.doc('admin_profession/edit', security='jwt')
            @api.expect(self.admin_profession_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    admin_id = data.get('admin_id')
                    institution_id = data.get('institution_id')
                    course_id = data.get('course_id')
                    subject_id = data.get('subject_id')
                    current_user_id = get_jwt_identity()
                    if not admin_id :
                
                        return jsonify({'message': 'Please Provide Admin Id', 'status': 201})
                    if not institution_id :
                       
                        return jsonify({'message': 'Please Provide Institute Id', 'status': 201})
                    if not course_id :
                      
                        return jsonify({'message': 'Please Provide Course Id', 'status': 201})
                    if not subject_id :
                       
                        return jsonify({'message': 'Please Provide Subject Id', 'status': 201})
                    else:
                   
                        admin_profession = AdminProfession.query.filter_by(admin_id=id).first()
                        if not admin_profession:
                            return jsonify({'message': 'Admin Profession not found', 'status': 404})
                        else:
                            admin_profession.admin_id = admin_id
                            admin_profession.institution_id = institution_id
                            admin_profession.course_id = course_id
                            admin_profession.subject_id = subject_id
                            admin_profession.updated_by=current_user_id
                            db.session.commit()
                        
                            return jsonify({'message': 'Admin Profession updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    
                    return jsonify({'message': str(e), 'status': 500})
            
                    
            @self.admin_profession_ns.doc('admin_profession/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
              
                    admin_profession = AdminProfession.query.filter_by(admin_id=id).first()
                    if not admin_profession:
                      
                        return jsonify({'message': 'Admin Profession not found', 'status': 404})
                    else:
                        admin_profession_data = {
                            'id': admin_profession.id,
                            'admin_id': admin_profession.admin_id,
                            'institution_id': admin_profession.institution_id,
                            'course_id':admin_profession.course_id,
                            'subject_id': admin_profession.subject_id,
                            'is_active': admin_profession.is_active,

                        }
                        print(admin_profession_data)
                       
                        return jsonify({'message': 'Admin Profession found Successfully', 'status': 200,'data':admin_profession_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
                    
        @self.admin_profession_ns.route('/activate/<string:id>')
        class ActivateAdminProfession(Resource):
            @self.admin_profession_ns.doc('admin_profession/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    admin_profession = AdminProfession.query.get(id)
                    if not admin_profession:
                        return jsonify({'message': 'Admin Profession not found', 'status': 404})

                    admin_profession.is_active = 1
                    db.session.commit()
             
                    return jsonify({'message': 'Admin Profession activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
 
                    return jsonify({'message': str(e), 'status': 500})

        @self.admin_profession_ns.route('/deactivate/<string:id>')
        class DeactivateAdminProfession(Resource):
            @self.admin_profession_ns.doc('admin_profession/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
               
                    admin_profession = AdminProfession.query.get(id)
                    if not admin_profession:
                        return jsonify({'message': 'Admin Profession not found', 'status': 404})

                    admin_profession.is_active = 0
                    db.session.commit()


                    return jsonify({'message': 'Admin Profession deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()

                    return jsonify({'message': str(e), 'status': 500})


        
        self.api.add_namespace(self.admin_profession_ns)