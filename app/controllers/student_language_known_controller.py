from datetime import datetime
import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.student import LanguageKnown

class StudentLanguageKnownController:
    def __init__(self,api):
        self.api = api
        self.student_language_known_model = api.model('StudentLanguageKnown', {
            'student_id': fields.String(required=True, description='Student Id'),
            'language_id': fields.String(required=True, description='Language Id'),
            'proficiency': fields.String(required=True, description='Proficiency')
        }) 
        self.edit_student_language_known_model = api.model('LanguageKnown', {
            'id':fields.String(required=True,description="Data Id"),
            'student_id': fields.String(required=True, description='Student Id'),
            'language_id': fields.String(required=True, description='Language Id'),
            'proficiency': fields.String(required=True, description='Proficiency')
        })
    
        self.student_multiple_language_known_model = self.api.model('LanguagesKnown',{
            'languages': fields.List(fields.Nested(self.student_language_known_model), required=True, description='List of Languages Known')
        })
        self.edit_student_multiple_language_known_model = self.api.model('LanguagesKnown',{
            'languages': fields.List(fields.Nested(self.edit_student_language_known_model), required=True, description='List of Languages Known')
        })
        
        self.student_language_known_bp = Blueprint('student_language_known', __name__)
        self.student_language_known_ns = Namespace('student_language_known', description='Student language Known Details', authorizations=authorizations)
    
        self.register_routes()

        
    def register_routes(self):
        @self.student_language_known_ns.route('/list')
        class StudentLanguageKnownList(Resource):
            @self.student_language_known_ns.doc('student_language_known/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    student_language_knowns = LanguageKnown.query.filter_by(is_active=1).all()
                    student_language_knowns_data = []
                    
                    for student_language_known in student_language_knowns:
                        student_language_known_data = {
                            'id': student_language_known.language_known_id,
                            'student_id': student_language_known.student_id,
                            'language_id': student_language_known.language_id,
                            'proficiency': student_language_known.proficiency,
                            'is_active': student_language_known.is_active
                        }
                        student_language_knowns_data.append(student_language_known_data)
                    
                    if not student_language_knowns_data:

                        return jsonify({'message': 'No Student Language Known found', 'status': 404})
                    else:

                        return jsonify({'message': 'Student Language Known  found Successfully', 'status': 200, 'data': student_language_knowns_data})
                except Exception as e:
    
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.student_language_known_ns.route('/alldata')
        class StudentLanguageKnownList(Resource):
            @self.student_language_known_ns.doc('student_language_known/alldata', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    student_language_knowns = LanguageKnown.query.all()
                    student_language_knowns_data = []
                    
                    for student_language_known in student_language_knowns:
                        student_language_known_data = {
                            'id': student_language_known.language_known_id,
                            'student_id': student_language_known.student_id,
                            'language_id': student_language_known.language_id,
                            'proficiency': student_language_known.proficiency,
                            'is_active': student_language_known.is_active
                        }
                        student_language_knowns_data.append(student_language_known_data)
                    
                    if not student_language_knowns_data:
             
                        return jsonify({'message': 'No Student Language Known found', 'status': 404})
                    else:
               
                        return jsonify({'message': 'Student Language Known  found Successfully', 'status': 200, 'data': student_language_knowns_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
        @self.student_language_known_ns.route('/add')
        class StudentLanguageKnownAdd(Resource):
            @self.student_language_known_ns.doc('student_language_known/add', security='jwt')
            @self.api.expect(self.student_language_known_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    student_id = data.get('student_id')
                    language_id = data.get('language_id')
                    proficiency = data.get('proficiency')
                    current_user_id = get_jwt_identity()
                    if not student_id :
                  
                        return jsonify({'message': 'Please Provide Student Id', 'status': 201})
                    if not language_id :
                      
                        return jsonify({'message': 'Please Provide Language Id', 'status': 201})
                    if not proficiency :
                        
                        return jsonify({'message': 'Please Provide Proficiency', 'status': 201})
                    else:
                        student_language_known = LanguageKnown(student_id=student_id,language_id=language_id,proficiency=proficiency,is_active =1,created_by=current_user_id)
                        db.session.add(student_language_known)
                        db.session.commit()
                     
                        return jsonify({'message': 'Student language Known created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
        
                    return jsonify({'message': str(e), 'status': 500})

        @self.student_language_known_ns.route('/multiple/add')
        class StudentyMultipleLanguageKnownAdd(Resource):
            @self.student_language_known_ns.doc('student_multiple_language_known/add', security='jwt')
            @self.api.expect(self.student_multiple_language_known_model, validate=True)
            @jwt_required()
            def post(self):
                try:
                    data = request.json.get('languages') 
                    if not isinstance(data, list):
         
                        return jsonify({'message': 'Payload should be an array of objects', 'status': 400})

                    current_user_id = get_jwt_identity()
                    responses = []

                    for item in data:
                        student_id = item.get('student_id')
                        language_id = item.get('language_id')
                        proficiency = item.get('proficiency')

                        if not student_id:
                       
                            responses.append({'message': 'Please Provide Student Id', 'status': 201, 'item': item})
                            continue
                        if not language_id:
                     
                            responses.append({'message': 'Please Provide Language Id', 'status': 201, 'item': item})
                            continue
                        if not proficiency:
                   
                            responses.append({'message': 'Please Provide Proficiency', 'status': 201, 'item': item})
                            continue

                        admin_language_known = LanguageKnown(
                            student_id=student_id,
                            language_id=language_id,
                            proficiency=proficiency,
                            is_active=1,
                            created_by=current_user_id
                        )
                        db.session.add(admin_language_known)
                    
                    db.session.commit()
                 
                    responses.append({'message': 'Student Languages Added successfully', 'status': 200})

                    return jsonify(responses)   
                except Exception as e:
                    db.session.rollback()
                
                    return jsonify({'message': str(e), 'status': 500})
        @self.student_language_known_ns.route('/multiple_language/edit')
        class StudentMultipleLanguageKnownEdit(Resource):
            @self.student_language_known_ns.doc('student_multiple_language_known/edit', security='jwt')
            @self.api.expect(self.edit_student_multiple_language_known_model, validate=True)
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
                        student_id = item.get('student_id')
                        language_id = item.get('language_id')
                        proficiency = item.get('proficiency')

                        if not record_id:
                    
                            responses.append({'message': 'Please Provide Record Id', 'status': 201, 'item': item})
                            continue
                        if not student_id:
                   
                            responses.append({'message': 'Please Provide Student Id', 'status': 201, 'item': item})
                            continue
                        if not language_id:
                      
                            responses.append({'message': 'Please Provide Language Id', 'status': 201, 'item': item})
                            continue
                        if not proficiency:
                          
                            responses.append({'message': 'Please Provide Proficiency', 'status': 201, 'item': item})
                            continue

                        student_language_known = LanguageKnown.query.filter_by(language_known_id=record_id).first()
                        if not student_language_known:
                        
                            responses.append({'message': f'Student language Known with id {record_id} not found', 'status': 404, 'item': item})
                            continue

                        student_language_known.student_id = student_id
                        student_language_known.language_id = language_id
                        student_language_known.proficiency = proficiency
                        student_language_known.updated_by = current_user_id
                        db.session.commit()
                  

                    responses.append({'message': 'Student Languages Updated successfully', 'status': 200})

                    return jsonify(responses)
                except Exception as e:
                    db.session.rollback()
                  
                    return jsonify({'message': str(e), 'status': 500})
        @self.student_language_known_ns.route('/edit/<string:id>')
        class StudentLanguageKnownEdit(Resource):
            @self.student_language_known_ns.doc('student_language_known/edit', security='jwt')
            @api.expect(self.student_language_known_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    student_id = data.get('student_id')
                    language_id = data.get('language_id')
                    proficiency = data.get('proficiency')
                    current_user_id = get_jwt_identity()
                    if not student_id :
                      
                        return jsonify({'message': 'Please Provide Student Id', 'status': 201})
                    if not language_id :
                       
                        return jsonify({'message': 'Please Provide Language Id', 'status': 201})
                    if not proficiency :
               
                        return jsonify({'message': 'Please Provide Proficiency', 'status': 201})
                    else:
                      
                        student_language_known = LanguageKnown.query.filter_by(language_known_id=id).first()
                        if not student_language_known:
                        
                            return jsonify({'message': 'Student language Known not found', 'status': 404})
                        else:
                            student_language_known.student_id = student_id
                            student_language_known.language_id = language_id
                            student_language_known.proficiency = proficiency
                            student_language_known.updated_by = current_user_id
                            db.session.commit()
                            return jsonify({'message': 'Student language Known updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
             
                    return jsonify({'message': str(e), 'status': 500})
                    
            @self.student_language_known_ns.doc('student_language_known/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
               
                    student_language_knowns = LanguageKnown.query.filter_by(student_id=id,is_active=1).all()
                    if not student_language_knowns:
          
                        return jsonify({'message': 'Student language Known not found', 'status': 404})
                    else:
                        student_language_knowns_data =[]
                        for student_language_known in student_language_knowns:
                            student_language_known_data = {
                                'id': student_language_known.language_known_id,
                                'student_id': student_language_known.student_id,
                                'language_id': student_language_known.language_id,
                                'proficiency': student_language_known.proficiency,
                                'is_active': student_language_known.is_active
                            }
                            student_language_knowns_data.append(student_language_known_data)
                            print(student_language_known_data)
              
                        return jsonify({'message': 'Student language Known found Successfully', 'status': 200,'data':student_language_knowns_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
        @self.student_language_known_ns.route('delete/<string:id>')
        class LanguageKnownDelete(Resource):
            @self.student_language_known_ns.doc('student_language_known/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        student_language_known = LanguageKnown.query.get(id)
                        if not student_language_known:
                   
                            return jsonify({'message': 'Student language Known  not found', 'status': 404})
                        else:
                            student_language_known.is_active = 0
                            db.session.commit()
                           
                            return jsonify({'message': 'Student language Known deleted successfully', 'status': 200})
                    except Exception as e:

                            return jsonify({'message': str(e), 'status': 500})
                    
        @self.student_language_known_ns.route('/activate/<string:id>')
        class StudentLanguageKnownActivate(Resource):
            @self.student_language_known_ns.doc('student_language_known/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    student_language_known = LanguageKnown.query.get(id)
                    if not student_language_known:
                        return jsonify({'message': 'Student language Known not found', 'status': 404})

                    student_language_known.is_active = 1
                    db.session.commit()
                   
                    return jsonify({'message': 'Student language Known activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                 
                    return jsonify({'message': str(e), 'status': 500})
        
        @self.student_language_known_ns.route('/deactivate/<string:id>')
        class StudentLanguageKnownDeactivate(Resource):
            @self.student_language_known_ns.doc('student_language_known/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    student_language_known = LanguageKnown.query.get(id)
                    if not student_language_known:
                
                        return jsonify({'message': 'Student language Known not found', 'status': 404})

                    student_language_known.is_active = 0
                    db.session.commit()
               
                    return jsonify({'message': 'Student language Known deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
    
                    return jsonify({'message': str(e), 'status': 500})
        self.api.add_namespace(self.student_language_known_ns)