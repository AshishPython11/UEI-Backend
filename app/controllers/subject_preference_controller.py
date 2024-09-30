from datetime import datetime
import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.student import SubjectPreference

class SubjectPreferenceController:
    def __init__(self,api):
        self.api = api
        self.subject_preference_model = api.model('SubjectPreference', {
            'student_id': fields.String(required=True, description='Admin Id'),
            'course_id': fields.String(required=True, description='Course Id'),
            'subject_id': fields.String(required=True, description='Subject Id'),
            'preference': fields.String(required=True, description='Preference'),
            'score_in_percentage': fields.String(required=True, description='Score in percentage')
        })
       
        self.subject_multiple_preference_model = self.api.model('SubjectPreferences', {
            'preferences': fields.List(fields.Nested(self.subject_preference_model), required=True, description='List of Subject Preferences')
        })
        self.subject_preference_edit_model  = self.api.model('SubjectPreference', {
            'id': fields.Integer(required=True, description='ID of the record to be updated'),
            'student_id': fields.String(required=True, description='Student Id'),
            'course_id': fields.String(required=True, description='Course Id'),
            'subject_id': fields.String(required=True, description='Subject Id'),
            'preference': fields.String(required=True, description='Preference'),
            'score_in_percentage': fields.Float(required=True, description='Score in Percentage')
        })

    
        self.subject_multiple_preference_edit_model  = self.api.model('SubjectPreferences', {
            'preferences': fields.List(fields.Nested(self.subject_preference_edit_model ), required=True, description='List of Subject Preferences')
        })
                
        self.subject_preference_bp = Blueprint('subject_preference', __name__)
        self.subject_preference_ns = Namespace('subject_preference', description='Subject Preference Details', authorizations=authorizations)
        
    
        self.register_routes()

        
    def register_routes(self):
        @self.subject_preference_ns.route('/list')
        class SubjectPreferenceList(Resource):
            @self.subject_preference_ns.doc('subject_preference/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    subject_preferences = SubjectPreference.query.filter_by(is_active=1).all()
                    subject_preferences_data = []
                    
                    for subject_preference in subject_preferences:
                        subject_preference_data = {
                            'id': subject_preference.subject_preference_id,
                            'student_id': subject_preference.student_id,
                            'course_id':subject_preference.course_id,
                            'subject_id': subject_preference.subject_id,
                            'preference': subject_preference.preference,
                            'score_in_percentage': subject_preference.score_in_percentage,
                            'is_active': subject_preference.is_active,
                            'created_at':subject_preference.created_at,
                            'updated_at':subject_preference.updated_at,
                        }
                        subject_preferences_data.append(subject_preference_data)
                    
                    if not subject_preferences_data:
                   
                        return jsonify({'message': 'No Subject Preference found', 'status': 404})
                    else:
             
                        return jsonify({'message': 'Subjects Preferences found Successfully', 'status': 200, 'data': subject_preferences_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
                
        @self.subject_preference_ns.route('/alldata')
        class SubjectPreferenceList(Resource):
            @self.subject_preference_ns.doc('subject_preference/alldata', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    subject_preferences = SubjectPreference.query.all()
                    subject_preferences_data = []
                    
                    for subject_preference in subject_preferences:
                        subject_preference_data = {
                            'id': subject_preference.subject_preference_id,
                            'student_id': subject_preference.student_id,
                            'course_id':subject_preference.course_id,
                            'subject_id': subject_preference.subject_id,
                            'preference': subject_preference.preference,
                            'score_in_percentage': subject_preference.score_in_percentage,
                            'is_active': subject_preference.is_active,
                            'created_at':subject_preference.created_at,
                            'updated_at':subject_preference.updated_at,
                        }
                        subject_preferences_data.append(subject_preference_data)
                    
                    if not subject_preferences_data:
                       
                        return jsonify({'message': 'No Subject Preference found', 'status': 404})
                    else:
                     
                        return jsonify({'message': 'Subjects Preferences found Successfully', 'status': 200, 'data': subject_preferences_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})


        @self.subject_preference_ns.route('/add')
        class SubjectPreferenceAdd(Resource):
            @self.subject_preference_ns.doc('subject_preference/add', security='jwt')
            @self.api.expect(self.subject_preference_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    student_id = data.get('student_id')
                    course_id = data.get('course_id')
                    subject_id = data.get('subject_id')
                    preference = data.get('preference')
                    current_user_id = get_jwt_identity()
                    score_in_percentage = data.get('score_in_percentage')
                    if not student_id :
                 
                        return jsonify({'message': 'Please Provide Admin Id', 'status': 201})
                    if not course_id :
                
                        return jsonify({'message': 'Please Provide Course Id', 'status': 201})
                    if not subject_id :
          
                        return jsonify({'message': 'Please Provide Subject Id', 'status': 201})
                    if not preference :
         
                        return jsonify({'message': 'Please Provide Preference', 'status': 201})
                    if not score_in_percentage :
                   
                        return jsonify({'message': 'Please Provide Score in percentage', 'status': 201})
                    else:
                        subject_preference = SubjectPreference(student_id=student_id,course_id=course_id,subject_id=subject_id,preference=preference,score_in_percentage=score_in_percentage,is_active = 1,created_by=current_user_id)
                        db.session.add(subject_preference)
                        db.session.commit()
            
                        return jsonify({'message': 'Subject Preference created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
 
                    return jsonify({'message': str(e), 'status': 500})

        @self.subject_preference_ns.route('/multiple_subject/add')
        class SubjectMultiplePreferenceAdd(Resource):
            @self.subject_preference_ns.doc('multiple_subject_preference/add', security='jwt')
            @self.api.expect(self.subject_multiple_preference_model, validate=True)
            @jwt_required()
            def post(self):
                try:
                    data = request.json.get('preferences') 
                    if not isinstance(data, list):
                        return jsonify({'message': 'Payload should be an array of objects', 'status': 400})

                    current_user_id = get_jwt_identity()
                    responses = []

                    for item in data:
                        student_id = item.get('student_id')
                        course_id = item.get('course_id')
                        subject_id = item.get('subject_id')
                        preference = item.get('preference')
                        score_in_percentage = item.get('score_in_percentage')

                        if not student_id:
                        
                            responses.append({'message': 'Please Provide Student Id', 'status': 201, 'item': item})
                            continue
                        if not course_id:
                      
                            responses.append({'message': 'Please Provide Course Id', 'status': 201, 'item': item})
                            continue
                        if not subject_id:
                         
                            responses.append({'message': 'Please Provide Subject Id', 'status': 201, 'item': item})
                            continue
                        if not preference:
       
                            responses.append({'message': 'Please Provide Preference', 'status': 201, 'item': item})
                            continue
                        if score_in_percentage is None:
                   
                            responses.append({'message': 'Please Provide Score in Percentage', 'status': 201, 'item': item})
                            continue

                        subject_preference = SubjectPreference(
                            student_id=student_id,
                            course_id=course_id,
                            subject_id=subject_id,
                            preference=preference,
                            score_in_percentage=score_in_percentage,
                            is_active=1,
                            created_by=current_user_id
                        )
                        db.session.add(subject_preference)
                    
                    db.session.commit()
                    responses.append({'message': 'Subject Preferences Added successfully', 'status': 200})
                  
                    return jsonify(responses)
                except Exception as e:
                    db.session.rollback()
                  
                    return jsonify({'message': str(e), 'status': 500})
            
            @self.subject_preference_ns.route('/multiple_subject/edit')
            class SubjectMultiplePreferenceEdit(Resource):
                @self.subject_preference_ns.doc('multiple_subject_preference/edit', security='jwt')
                @self.api.expect(self.subject_multiple_preference_edit_model, validate=True)
                @jwt_required()
                def put(self):
                    try:
                        data = request.json.get('preferences') 
                        if not isinstance(data, list):
                            return jsonify({'message': 'Payload should be an array of objects', 'status': 400})

                        current_user_id = get_jwt_identity()
                        responses = []

                        for item in data:
                            record_id = item.get('id')
                            student_id = item.get('student_id')
                            course_id = item.get('course_id')
                            subject_id = item.get('subject_id')
                            preference = item.get('preference')
                            score_in_percentage = item.get('score_in_percentage')

                            if not record_id:
                           
                                responses.append({'message': 'Please Provide Record Id', 'status': 201, 'item': item})
                                continue
                            if not student_id:
                           
                                responses.append({'message': 'Please Provide Student Id', 'status': 201, 'item': item})
                                continue
                            if not course_id:
                          
                                responses.append({'message': 'Please Provide Course Id', 'status': 201, 'item': item})
                                continue
                            if not subject_id:
                        
                                responses.append({'message': 'Please Provide Subject Id', 'status': 201, 'item': item})
                                continue
                            if not preference:
                            
                                responses.append({'message': 'Please Provide Preference', 'status': 201, 'item': item})
                                continue
                            if score_in_percentage is None:
                            
                                responses.append({'message': 'Please Provide Score in Percentage', 'status': 201, 'item': item})
                                continue

                            subject_preference = SubjectPreference.query.filter_by(subject_preference_id=record_id).first()
                            if not subject_preference:
                                responses.append({'message': f'Subject Preference with id {record_id} not found', 'status': 404, 'item': item})
                                continue

                            subject_preference.student_id = student_id
                            subject_preference.course_id = course_id
                            subject_preference.subject_id = subject_id
                            subject_preference.preference = preference
                            subject_preference.score_in_percentage = score_in_percentage
                            subject_preference.updated_by = current_user_id
                            db.session.commit()
               
                        responses.append({'message': 'Subject Preferences Updated successfully', 'status': 200})

                        return jsonify(responses)
                    except Exception as e:
                        db.session.rollback()
              
                        return jsonify({'message': str(e), 'status': 500})


        @self.subject_preference_ns.route('/edit/<string:id>')
        class SubjectPreferenceEdit(Resource):
            @self.subject_preference_ns.doc('subject_preference/edit', security='jwt')
            @api.expect(self.subject_preference_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    student_id = data.get('student_id')
                    course_id = data.get('course_id')
                    subject_id = data.get('subject_id')
                    preference = data.get('preference')
                    current_user_id = get_jwt_identity()
                    score_in_percentage = data.get('score_in_percentage')
                    if not student_id :
            
                        return jsonify({'message': 'Please Provide Admin Id', 'status': 201})
                    if not course_id :
                    
                        return jsonify({'message': 'Please Provide Course Id', 'status': 201})
                    if not subject_id :
                
                        return jsonify({'message': 'Please Provide Subject Id', 'status': 201})
                    if not preference :
                
                        return jsonify({'message': 'Please Provide Preference', 'status': 201})
                    if not score_in_percentage :
         
                        return jsonify({'message': 'Please Provide Score in percentage', 'status': 201})
                    else:
                        subject_preference = SubjectPreference.query.get(id)
                        if not subject_preference:
                
                            return jsonify({'message': 'Subject Preference not found', 'status': 404})
                        else:
                            subject_preference.student_id = student_id
                            subject_preference.course_id = course_id
                            subject_preference.subject_id = subject_id
                            subject_preference.preference = preference
                            subject_preference.score_in_percentage = score_in_percentage
                            subject_preference.updated_by = current_user_id
                            db.session.commit()
           
                            return jsonify({'message': 'Subject Preference updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
          
                    return jsonify({'message': str(e), 'status': 500})
                        
            @self.subject_preference_ns.doc('subject_preference/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
              
                    subject_preferences = SubjectPreference.query.filter_by(student_id=id,is_active=1).all()
                    if not subject_preferences:       
                        return jsonify({'message': 'Subject Preference not found', 'status': 404})
                    else:
                        subject_preferences_data = []
                        for subject_preference in subject_preferences:
                            subject_preference_data = {
                                'id': subject_preference.subject_preference_id,
                                'student_id': subject_preference.student_id,
                                'course_id':subject_preference.course_id,
                                'subject_id': subject_preference.subject_id,
                                'preference': subject_preference.preference,
                                'score_in_percentage': subject_preference.score_in_percentage,
                                'is_active': subject_preference.is_active,
                                'created_at':subject_preference.created_at,
                                'updated_at':subject_preference.updated_at,
                            }
                            subject_preferences_data.append(subject_preference_data)
                        
                        print(subject_preference_data)
            
                        return jsonify({'message': 'Subject Preference found Successfully', 'status': 200,'data':subject_preferences_data})
                except Exception as e:
                    return jsonify({'message': str(e), 'status': 500})

     
        @self.subject_preference_ns.route('delete/<string:id>')
        class StudentSubjectPreferenceDelete(Resource):
            @self.subject_preference_ns.doc('subject_preference/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        subject_preference = SubjectPreference.query.get(id)
                        if not subject_preference:
                    
                            return jsonify({'message': 'Student Preference  not found', 'status': 404})
                        else:
                            subject_preference.is_active = 0
                            db.session.commit()
                     
                            return jsonify({'message': 'Student Preference deleted successfully', 'status': 200})  
                    except Exception as e:
 
                        return jsonify({'message': str(e), 'status': 500})
                        
        @self.subject_preference_ns.route('/activate/<string:id>')
        class SubjectPreferenceActivate(Resource):
            @self.subject_preference_ns.doc('subject_preference/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    subject_preference = SubjectPreference.query.get(id)
                    if not subject_preference:
 
                        return jsonify({'message': 'Subject Preference not found', 'status': 404})
                    subject_preference.is_active = 1
                    db.session.commit()
                    return jsonify({'message': 'Subject Preference activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})
            
        @self.subject_preference_ns.route('/deactivate/<string:id>')
        class SubjectPreferenceDeactivate(Resource):
            @self.subject_preference_ns.doc('subject_preference/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    subject_preference = SubjectPreference.query.get(id)
                    if not subject_preference:
                        return jsonify({'message': 'Subject Preference not found', 'status': 404})
                    subject_preference.is_active = 0
                    db.session.commit()
            
                    return jsonify({'message': 'Subject Preference deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})
                    

        
        self.api.add_namespace(self.subject_preference_ns)