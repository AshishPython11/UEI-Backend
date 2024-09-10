from datetime import datetime
import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.adminuser import AdminLanguageKnown

class AdminLanguageKnownController:
    def __init__(self,api):
        self.api = api
        self.admin_language_known_model = api.model('AdminLanguageKnown', {
            'admin_id': fields.String(required=True, description='Admin Id'),
            'language_id': fields.String(required=True, description='Language Id'),
            'proficiency': fields.String(required=True, description='Proficiency')
        })
        self.edit_admin_language_known_model = api.model('AdminLanguageKnown', {
            'id':fields.String(required=True,description="Data Id"),
            'admin_id': fields.String(required=True, description='Admin Id'),
            'language_id': fields.String(required=True, description='Language Id'),
            'proficiency': fields.String(required=True, description='Proficiency')
        })
      # Define a model for an array of language known objects
        self.admin_multiple_language_known_model = self.api.model('LanguagesKnown',{
            'languages': fields.List(fields.Nested(self.admin_language_known_model), required=True, description='List of Languages Known')
        })
        self.edit_admin_multiple_language_known_model = self.api.model('LanguagesKnown',{
            'languages': fields.List(fields.Nested(self.edit_admin_language_known_model), required=True, description='List of Languages Known')
        })
        self.required_fields = ['admin_id', 'language_id', 'proficiency']
        self.admin_language_known_bp = Blueprint('admin_language_known', __name__)
        self.admin_language_known_ns = Namespace('admin_language_known', description='Admin language Known Details', authorizations=authorizations)
        
  
        self.register_routes()
    def calculate_completion_percentage(self, data):
        filled_fields = sum(1 for field in self.required_fields if field in data and data[field])
        total_required_fields = len(self.required_fields)
        return (filled_fields / total_required_fields) * 100 if total_required_fields > 0 else 0
        
    def register_routes(self):
        @self.admin_language_known_ns.route('/list')
        class AdminLanguageKnownList(Resource):
            @self.admin_language_known_ns.doc('admin_language_known/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    admin_language_knownes = AdminLanguageKnown.query.filter_by(is_active=1).all()
                    admin_language_knownes_data = []
                    
                    for admin_language_known in admin_language_knownes:
                        admin_language_known_data = {
                            'id': admin_language_known.id,
                            'admin_id': admin_language_known.admin_id,
                            'language_id': admin_language_known.language_id,
                            'proficiency': admin_language_known.proficiency,
                            'is_active': admin_language_known.is_active
                        }
                        admin_language_knownes_data.append(admin_language_known_data)
                    
                    if not admin_language_knownes_data:
           
                        return jsonify({'message': 'No Admin Language Known found', 'status': 404})
                    else:
               
                        return jsonify({'message': 'Admin Language Known found Successfully', 'status': 200, 'data': admin_language_knownes_data})
                except Exception as e:
                   

                    return jsonify({'message': str(e), 'status': 500})
        @self.admin_language_known_ns.route('/alldata')
        class AdminLanguageKnownList(Resource):
            @self.admin_language_known_ns.doc('admin_language_known/alldata', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    admin_language_knownes = AdminLanguageKnown.query.filter_by(is_active=1).first()
                    # admin_language_knownes = AdminLanguageKnown.query.all()
                    admin_language_knownes_data = []
                    
                    for admin_language_known in admin_language_knownes:
                        admin_language_known_data = {
                            'id': admin_language_known.id,
                            'admin_id': admin_language_known.admin_id,
                            'language_id': admin_language_known.language_id,
                            'proficiency': admin_language_known.proficiency,
                            'is_active': admin_language_known.is_active
                        }
                        admin_language_knownes_data.append(admin_language_known_data)
                    
                    if not admin_language_knownes_data:
                 
                        return jsonify({'message': 'No Admin Language Known found', 'status': 404})
                    else:
                   
                        return jsonify({'message': 'Admin Language Known found Successfully', 'status': 200, 'data': admin_language_knownes_data})
                except Exception as e:
                    
                    return jsonify({'message': str(e), 'status': 500})
        @self.admin_language_known_ns.route('/add')
        class AdminLanguageKnownAdd(Resource):
            @self.admin_language_known_ns.doc('admin_language_known/add', security='jwt')
            @self.api.expect(self.admin_language_known_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    admin_id = data.get('admin_id')
                    language_id = data.get('language_id')
                    proficiency = data.get('proficiency')
                    current_user_id = get_jwt_identity()
                    if not admin_id :
                
                        return jsonify({'message': 'Please Provide Admin Id', 'status': 201})
                    if not language_id :
              
                        return jsonify({'message': 'Please Provide Language Id', 'status': 201})
                    if not proficiency :
       
                        return jsonify({'message': 'Please Provide Proficiency', 'status': 201})
                    else:
                        admin_language_known = AdminLanguageKnown(admin_id=admin_id,language_id=language_id,proficiency=proficiency,is_active=1,created_by=current_user_id)
                        db.session.add(admin_language_known)
                        db.session.commit()
                       
                        return jsonify({'message': 'Admin language Known created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
          
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.admin_language_known_ns.route('/multiple/add')
        class AdminMultipleLanguageKnownAdd(Resource):
            @self.admin_language_known_ns.doc('admin_multiple_language_known/add', security='jwt')
            @self.api.expect(self.admin_multiple_language_known_model, validate=True)
            @jwt_required()
            def post(self):
                try:
                    data = request.json.get('languages')  # Expecting an array of objects
                    if not isinstance(data, list):
                        return jsonify({'message': 'Payload should be an array of objects', 'status': 400})

                    current_user_id = get_jwt_identity()
                    responses = []

                    for item in data:
                        admin_id = item.get('admin_id')
                        language_id = item.get('language_id')
                        proficiency = item.get('proficiency')

                        if not admin_id:
                        
                            responses.append({'message': 'Please Provide Admin Id', 'status': 201, 'item': item})
                            continue
                        if not language_id:
                        
                            responses.append({'message': 'Please Provide Language Id', 'status': 201, 'item': item})
                            continue
                        if not proficiency:
                        
                            responses.append({'message': 'Please Provide Proficiency', 'status': 201, 'item': item})
                            continue

                        admin_language_known = AdminLanguageKnown(
                            admin_id=admin_id,
                            language_id=language_id,
                            proficiency=proficiency,
                            is_active=1,
                            created_by=current_user_id
                        )
                        db.session.add(admin_language_known)
                    
                    db.session.commit()
            
                    responses.append({'message': 'Admin Languages Added successfully', 'status': 200})

                    return jsonify(responses)
                except Exception as e:
                    db.session.rollback()
               
                    return jsonify({'message': str(e), 'status': 500})

        @self.admin_language_known_ns.route('/multiple_language/edit')
        class AdminMultipleLanguageKnownEdit(Resource):
            @self.admin_language_known_ns.doc('admin_multiple_language_known/edit', security='jwt')
            @self.api.expect(self.edit_admin_multiple_language_known_model, validate=True)
            @jwt_required()
            def put(self):
                try:
                    data = request.json.get('languages')  
                    if not isinstance(data, list):
                        return jsonify({'message': 'Payload should be an array of objects', 'status': 400})

                    current_user_id = get_jwt_identity()
                    responses = []

                    for item in data:
                        record_id = item.get('id')
                        admin_id = item.get('admin_id')
                        language_id = item.get('language_id')
                        proficiency = item.get('proficiency')

                        if not record_id:
                        
                            responses.append({'message': 'Please Provide Record Id', 'status': 201, 'item': item})
                            continue
                        if not admin_id:
                        
                            responses.append({'message': 'Please Provide Admin Id', 'status': 201, 'item': item})
                            continue
                        if not language_id:
                 
                            responses.append({'message': 'Please Provide Language Id', 'status': 201, 'item': item})
                            continue
                        if not proficiency:
                      
                            responses.append({'message': 'Please Provide Proficiency', 'status': 201, 'item': item})
                            continue

                        admin_language_known = AdminLanguageKnown.query.filter_by(id=record_id).first()
                        if not admin_language_known:
             
                            responses.append({'message': f'Admin language Known with id {record_id} not found', 'status': 404, 'item': item})
                            continue

                        admin_language_known.admin_id = admin_id
                        admin_language_known.language_id = language_id
                        admin_language_known.proficiency = proficiency
                        admin_language_known.updated_by = current_user_id
                        db.session.commit()

                    responses.append({'message': 'Admin Languages Updated successfully', 'status': 200})
            
                    return jsonify(responses)
                except Exception as e:
                    db.session.rollback()
                  
                    return jsonify({'message': str(e), 'status': 500})
                                     
        @self.admin_language_known_ns.route('/edit/<int:id>')
        class AdminLanguageKnownEdit(Resource):
            @self.admin_language_known_ns.doc('admin_language_known/edit', security='jwt')
            @api.expect(self.admin_language_known_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    admin_id = data.get('admin_id')
                    language_id = data.get('language_id')
                    proficiency = data.get('proficiency')
                    current_user_id = get_jwt_identity()
                    if not admin_id :
                    
                        return jsonify({'message': 'Please Provide Admin Id', 'status': 201})
                    if not language_id :
            
                        return jsonify({'message': 'Please Provide Language Id', 'status': 201})
                    if not proficiency :
         
                        return jsonify({'message': 'Please Provide Proficiency', 'status': 201})
                    else:
                       
                        admin_language_known = AdminLanguageKnown.query.filter_by(admin_id=admin_id).first()
                        if not admin_language_known:
                    
                            return jsonify({'message': 'Admin language Known not found', 'status': 404})
                        else:
                            admin_language_known.admin_id = admin_id
                            admin_language_known.language_id = language_id
                            admin_language_known.proficiency = proficiency
                            admin_language_known.updated_by = current_user_id
                            db.session.commit()
                       
                            return jsonify({'message': 'Admin language Known updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
            
                    return jsonify({'message': 'Internal Server Error', 'status': 500})
                    
            @self.admin_language_known_ns.doc('admin_language_known/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                
                    admin_language_knowns = AdminLanguageKnown.query.filter_by(admin_id=id,is_active=1).all()
                    if not admin_language_knowns:
         
                        return jsonify({'message': 'Admin language Known not found', 'status': 404})
                    else:
                        admin_language_known_data = []
                        for admin_language_known in admin_language_knowns:  
                            admin_language_known_data.append({
                                'id': admin_language_known.id,
                                'admin_id': admin_language_known.admin_id,
                                'language_id': admin_language_known.language_id,
                                'proficiency': admin_language_known.proficiency,
                                'is_active': admin_language_known.is_active
                            })
                            print(admin_language_known_data)
                  
                        return jsonify({'message': 'Admin Language Known found Successfully', 'status': 200,'data':admin_language_known_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
                
        @self.admin_language_known_ns.route('/delete/<int:id>')
        class LanguageKnownDelete(Resource):
            @self.admin_language_known_ns.doc('admin_language_known/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        admin_language_known = AdminLanguageKnown.query.get(id)
                        if not admin_language_known:
                        
                            return jsonify({'message': 'Admin language Known  not found', 'status': 404})
                        else:
                            admin_language_known.is_active = 0
                            db.session.commit()
                          
                            return jsonify({'message': 'Admin Language Known deleted successfully', 'status': 200})
                    except Exception as e:
                        db.session.rollback()
             
                        return jsonify({'message': str(e), 'status': 500})
                        
        @self.admin_language_known_ns.route('/activate/<int:id>')
        class LanguageKnownActivate(Resource):
            @self.admin_language_known_ns.doc('admin_language_known/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    admin_language_known = AdminLanguageKnown.query.get(id)
                    if not admin_language_known:
                 
                        return jsonify({'message': 'Admin language Known not found', 'status': 404})
                    else:
                        admin_language_known.is_active = 1
                        db.session.commit()
           
                        return jsonify({'message': 'Admin Language Known activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
             
                    return jsonify({'message': str(e), 'status': 500})
        
        @self.admin_language_known_ns.route('/deactivate/<int:id>')
        class LanguageKnownDeactivate(Resource):
            @self.admin_language_known_ns.doc('admin_language_known/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    admin_language_known = AdminLanguageKnown.query.get(id)
                    if not admin_language_known:
                       
                        return jsonify({'message': 'Admin language Known not found', 'status': 404})
                    else:
                        admin_language_known.is_active = 0
                        db.session.commit()
            
                        return jsonify({'message': 'Admin Language Known deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()

                    return jsonify({'message': str(e), 'status': 500})
            
        self.api.add_namespace(self.admin_language_known_ns)