from datetime import datetime
import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.student import StudentHobby

class StudentHobbyController:
    def __init__(self,api):
        self.api = api
        self.student_hobby_model = api.model('StudentHobby', {
            'student_id': fields.String(required=True, description='Student Id'),
            'hobby_id': fields.Integer(required=True, description='Hobby Id')
        })
        self.student_multiple_hobby_model = self.api.model('StudentHobbies', {
            'hobbies': fields.List(fields.Nested(self.student_hobby_model), required=True, description='List of Student Hobbies')
        })
        self.student_hobby_edit_model = self.api.model('StudentHobbyEdit', {
            'id': fields.Integer(required=True, description='ID of the record to be updated'),
            'student_id': fields.String(required=True, description='Student Id'),
            'hobby_id': fields.Integer(required=True, description='Hobby Id')
        })

        self.student_multiple_hobby_edit_model = self.api.model('StudentHobbiesEdit', {
            'hobbies': fields.List(fields.Nested(self.student_hobby_edit_model), required=True, description='List of Student Hobbies for Editing')
        })
        
        self.student_hobby_bp = Blueprint('student_hobby', __name__)
        self.student_hobby_ns = Namespace('student_hobby', description='Student Hobby Details', authorizations=authorizations)

        self.register_routes()

        
    def register_routes(self):
        @self.student_hobby_ns.route('/list')
        class StudentHobbyList(Resource):
            @self.student_hobby_ns.doc('student_hobby/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    student_hobbies = StudentHobby.query.filter_by(is_active=1).all()
                    student_hobbies_data = []
                    
                    for student_hobby in student_hobbies:
                        student_hobby_data = {
                            'id': student_hobby.id,
                            'student_id': student_hobby.student_id,
                            'hobby_id': student_hobby.hobby_id,
                            'is_active': student_hobby.is_active
                        }
                        student_hobbies_data.append(student_hobby_data)
                    
                    if not student_hobbies_data:
                   
                        return jsonify({'message': 'No Student Hobby found', 'status': 404})
                    else:
                    
                        return jsonify({'message': 'Student Hobbies found Successfully', 'status': 200, 'data': student_hobbies_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
        @self.student_hobby_ns.route('/alldata')
        class StudentHobbyList(Resource):
            @self.student_hobby_ns.doc('student_hobby/alldata', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    student_hobbies = StudentHobby.query.all()
                    student_hobbies_data = []
                    
                    for student_hobby in student_hobbies:
                        student_hobby_data = {
                            'id': student_hobby.id,
                            'student_id': student_hobby.student_id,
                            'hobby_id': student_hobby.hobby_id,
                            'is_active': student_hobby.is_active
                        }
                        student_hobbies_data.append(student_hobby_data)
                    
                    if not student_hobbies_data:
               
                        return jsonify({'message': 'No Student Hobby found', 'status': 404})
                    else:

                        return jsonify({'message': 'Student Hobbies found Successfully', 'status': 200, 'data': student_hobbies_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
        @self.student_hobby_ns.route('/add')
        class StudentHobbyAdd(Resource):
            @self.student_hobby_ns.doc('student_hobby/add', security='jwt')
            @self.api.expect(self.student_hobby_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    
                    student_id = data.get('student_id')
                    hobby_id = data.get('hobby_id')
                    current_user_id = get_jwt_identity()
                    
                    if not student_id :
       
                        return jsonify({'message': 'Please Provide Student Id', 'status': 201})
                    if not hobby_id :

                        return jsonify({'message': 'Please Provide Hobby Id', 'status': 201})
                    else:
                        student_hobby = StudentHobby(student_id=student_id,hobby_id=hobby_id,is_active=1,created_by=current_user_id)
                        db.session.add(student_hobby)
                        db.session.commit()
  
                        return jsonify({'message': 'Student Hobby created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()

                    return jsonify({'message': str(e), 'status': 500})
                

        @self.student_hobby_ns.route('/multiadd')
        class StudentMultipleHobbyAdd(Resource):
            @self.student_hobby_ns.doc('student_multiple_hobby/add', security='jwt')
            @self.api.expect(self.student_multiple_hobby_model, validate=True)
            @jwt_required()
            def post(self):
                try:
                    data = request.json.get('hobbies')  
                    if not isinstance(data, list):
                        return jsonify({'message': 'Payload should be an array of objects', 'status': 400})

                    current_user_id = get_jwt_identity()
                    responses = []

                    for item in data:
                        student_id = item.get('student_id')
                        hobby_id = item.get('hobby_id')

                        if not student_id:
                      
                            responses.append({'message': 'Please Provide Student Id', 'status': 201, 'item': item})
                            continue
                        if not hobby_id:
                   
                            responses.append({'message': 'Please Provide Hobby Id', 'status': 201, 'item': item})
                            continue

                        student_hobby = StudentHobby(
                            student_id=student_id,
                            hobby_id=hobby_id,
                            is_active=1,
                            created_by=current_user_id
                        )
                        db.session.add(student_hobby)
                    
                    db.session.commit()
        
                    responses.append({'message': 'Student Hobbies found successfully', 'status': 200})

                    return jsonify(responses)
                except Exception as e:
                    db.session.rollback()
                
                    return jsonify({'message': str(e), 'status': 500})
                

        @self.student_hobby_ns.route('/multiple_hobby_edit')
        class StudentMultipleHobbyEdit(Resource):
            @self.student_hobby_ns.doc('student_multiple_hobby/edit', security='jwt')
            @self.api.expect(self.student_multiple_hobby_edit_model, validate=True)
            @jwt_required()
            def put(self):
                try:
                    data = request.json.get('hobbies') 
                    if not isinstance(data, list):
                        return jsonify({'message': 'Payload should be an array of objects', 'status': 400})

                    current_user_id = get_jwt_identity()
                    responses = []

                    for item in data:
                        record_id = item.get('id')
                        student_id = item.get('student_id')
                        hobby_id = item.get('hobby_id')

                        if not record_id:
    
                            responses.append({'message': 'Please Provide Record Id', 'status': 201, 'item': item})
                            continue
                        if not student_id:
              
                            responses.append({'message': 'Please Provide Student Id', 'status': 201, 'item': item})
                            continue
                        if not hobby_id:

                            responses.append({'message': 'Please Provide Hobby Id', 'status': 201, 'item': item})
                            continue

                        student_hobby = StudentHobby.query.filter_by(id=record_id).first()
                        if not student_hobby:
       
                            responses.append({'message': f'Student Hobby with id {record_id} not found', 'status': 404, 'item': item})
                            continue

                        student_hobby.student_id = student_id
                        student_hobby.hobby_id = hobby_id
                        student_hobby.updated_by = current_user_id
                        db.session.commit()
                   
                    responses.append({'message': 'All valid records processed successfully', 'status': 200})

                    return jsonify(responses)
                except Exception as e:
                    db.session.rollback()
                    
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.student_hobby_ns.route('/edit/<string:id>')
        class StudentHobbyEdit(Resource):
            @self.student_hobby_ns.doc('student_hobby/edit', security='jwt')
            @api.expect(self.student_hobby_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    student_id = data.get('student_id')
                    hobby_id = data.get('hobby_id')
                    current_user_id = get_jwt_identity()
                    if not student_id :
                  
                        return jsonify({'message': 'Please Provide Student Id', 'status': 201})
                    if not hobby_id :
                    
                        return jsonify({'message': 'Please Provide Hobby Id', 'status': 201})
                    
                    else:
                        
                        student_hobby = StudentHobby.query.filter_by(student_id=student_id, is_active=1).first()
                        if not student_hobby:
                        
                            return jsonify({'message': 'Student Hobby not found', 'status': 404})
                        else:
                            student_hobby.student_id = student_id
                            student_hobby.hobby_id = hobby_id
                            student_hobby.updated_by = current_user_id
                            db.session.commit()
              
                            return jsonify({'message': 'Student Hobby updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
              
                    return jsonify({'message': str(e), 'status': 500})
                    
            @self.student_hobby_ns.doc('student_hobby/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
               
                    student_hobbies = StudentHobby.query.filter_by(student_id=id,is_active=1).all() 
                    student_hobbies_data = []
                    
                    for student_hobby in student_hobbies:
                        student_hobby_data = {
                            'id': student_hobby.id,
                            'student_id': student_hobby.student_id,
                            'hobby_id': student_hobby.hobby_id,
                            'is_active': student_hobby.is_active
                        }
                        student_hobbies_data.append(student_hobby_data)
                    
                    if not student_hobbies_data:
        
                        return jsonify({'message': 'No Student Hobby found', 'status': 404})
                    else:
      
                        return jsonify({'message': 'Student Hobbies found Successfully', 'status': 200, 'data': student_hobbies_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
        @self.student_hobby_ns.route('/delete/<string:id>')
        class StudentHobbyDelete(Resource):
            @self.student_hobby_ns.doc('student_hobby/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                try:
                    student_hobby = StudentHobby.query.get(id)
                    if not student_hobby:
   
                        return jsonify({'message': 'Student Hobby not found', 'status': 404})

                    student_hobby.is_active = 0
                    db.session.commit()

                    return jsonify({'message': 'Student Hobby deleted successfully', 'status': 200})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
                
        @self.student_hobby_ns.route('/activate/<string:id>')
        class StudentHobbyActivate(Resource):
            @self.student_hobby_ns.doc('student_hobby/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    student_hobby = StudentHobby.query.get(id)
                    if not student_hobby:
        
                        return jsonify({'message': 'Student Hobby not found', 'status': 404})

                    student_hobby.is_active = 1
                    db.session.commit()
      
                    return jsonify({'message': 'Student Hobby activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
     
                    return jsonify({'message': str(e), 'status': 500})
        
        @self.student_hobby_ns.route('/deactivate/<string:id>')
        class StudentHobbyDeactivate(Resource):
            @self.student_hobby_ns.doc('student_hobby/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    student_hobby = StudentHobby.query.get(id)
                    if not student_hobby:

                        return jsonify({'message': 'Student Hobby not found', 'status': 404})

                    student_hobby.is_active = 0
                    db.session.commit()

                    return jsonify({'message': 'Student Hobby deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()

                    return jsonify({'message': str(e), 'status': 500})

        
        self.api.add_namespace(self.student_hobby_ns)