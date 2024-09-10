from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.student import NewStudentAcademicHistory
from app.models.adminuser import Institution

class NewStudentAcademicHistoryController:
    def __init__(self, api):
        self.api = api
        self.student_academic_history_model = api.model('AcademicHistory', {
            'student_id': fields.String(required=True, description='Student ID'),
            'institution_type': fields.String(required=True, description='Type of the institution'),
            'board': fields.String(required=False, description='Educational board'),
            'state_for_stateboard': fields.String(required=False, description='State for state board'),
            'institute_id': fields.String(required=True, description='ID of the institution'),
            'course_id': fields.String(required=True, description='ID of the course'),
            'learning_style': fields.String(required=False, description='Learning style'),
            'class_id': fields.String(required=True, description='ID of the class'),
            'year': fields.String(required=False, description='Academic year or semester')
        })

        self.student_multiple_academic_history_model = self.api.model('AcademicHistories', {
            'histories': fields.List(fields.Nested(self.student_academic_history_model), required=True, description='List of Academic Histories')
        })

        student_academic_history_edit_model = self.api.model('AcademicHistoryEdit', {
            'student_id': fields.String(required=True, description='Student ID'),
            'institution_type': fields.String(required=True, description='Type of the institution'),
            'board': fields.String(required=False, description='Educational board'),
            'state_for_stateboard': fields.String(required=False, description='State for state board'),
            'institute_id': fields.String(required=True, description='ID of the institution'),
            'course_id': fields.String(required=True, description='ID of the course'),
            'learning_style': fields.String(required=False, description='Learning style'),
            'class_id': fields.String(required=True, description='ID of the class'),
            'year': fields.String(required=False, description='Academic year or semester')
        })

        self.student_multiple_academic_history_edit_model = self.api.model('AcademicHistoriesEdit', {
            'histories': fields.List(fields.Nested(student_academic_history_edit_model), required=True, description='List of Academic Histories for Editing')
        })

        self.new_student_academic_history_bp = Blueprint('new_student_academic_history', __name__)
        self.new_student_academic_history_ns = Namespace('new_student_academic_history', description='New Student Academic History Details', authorizations=authorizations)
        
        self.register_routes()

    def register_routes(self):
        @self.new_student_academic_history_ns.route('/list')
        class StudentAcademicHistoryList(Resource):
            @self.new_student_academic_history_ns.doc('student_academic_history/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    academic_histories = NewStudentAcademicHistory.query.filter_by(is_active=True).all()
                    data = []

                    for history in academic_histories:
                       
                        institution_name = None
                        if history.institute_id:
                            institution = Institution.query.get(history.institute_id)
                            if institution:
                                institution_name = institution.institution_name
                        
                        history_data = {
                            'student_id': history.student_id,
                            'institution_type': history.institution_type,
                            'board': history.board,
                            'state_for_stateboard': history.state_for_stateboard,
                            'institute_id': history.institute_id,
                            'institute_name': institution_name,  
                            'course_id': history.course_id,
                            'learning_style': history.learning_style,
                            'class_id': history.class_id,
                            'year': history.year_or_semester,
                            'created_at': history.created_at,
                            'updated_at': history.updated_at,
                            'is_active': history.is_active
                        }
                        data.append(history_data)

                    if not data:
                    
                        return jsonify({'message': 'No Academic Histories found', 'status': 404})
                    else:
                   
                        return jsonify({'message': 'Academic Histories found successfully', 'status': 200, 'data': data})
                except Exception as e:
                
                    return jsonify({'message': str(e), 'status': 500})
        @self.new_student_academic_history_ns.route('/alldata')
        class StudentAcademicHistoryList(Resource):
            @self.new_student_academic_history_ns.doc('student_academic_history/alldata', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    student_academic_histories = NewStudentAcademicHistory.query.all()
                    student_academic_histories_data = []
                    institution_name = None
                    if student_academic_histories.institute_id:
                        institution = Institution.query.get(student_academic_histories.institute_id)
                        if institution:
                            institution_name = institution.institution_name
                    
                    for history in student_academic_histories:
                        history_data = {
                            'student_id': history.student_id,
                            'institution_type': history.institution_type,  
                            'board': history.board,
                            'state_for_stateboard': history.state_for_stateboard,
                            'institute_id': history.institute_id,  
                            'institute_name': institution_name,
                            'course_id': history.course_id,  
                            'learning_style': history.learning_style,
                            'class_id': history.class_id,  
                            'year': history.year_or_semester,  
                            'created_at': history.created_at,
                            'updated_at': history.updated_at,
                            'is_active': history.is_active
                        }
                        student_academic_histories_data.append(history_data)
                    
                    if not student_academic_histories_data:
             
                        return jsonify({'message': 'No student academic histories found', 'status': 404})
                    else:
               
                        return jsonify({'message': 'Student Academic Histories retrieved successfully', 'status': 200, 'data': student_academic_histories_data})
                except Exception as e:
          
                    return jsonify({'message': str(e), 'status': 500})

       
        @self.new_student_academic_history_ns.route('/add')
        class AcademicHistoryAdd(Resource):
            @self.new_student_academic_history_ns.doc('student_academic_history/add', security='jwt')
            @self.api.expect(self.student_academic_history_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    current_user_id = get_jwt_identity()

                    institute_id = int(data['institute_id']) if data.get('institute_id') else None
                    course_id = int(data['course_id']) if data.get('course_id') else None
                    class_id = int(data['class_id']) if data.get('class_id') else None

                    new_academic_history = NewStudentAcademicHistory(
                        student_id=int(data['student_id']), 
                        institution_type=data['institution_type'],
                        board=data.get('board'),
                        state_for_stateboard=data.get('state_for_stateboard'),
                        institute_id=institute_id,
                        course_id=course_id,
                        learning_style=data['learning_style'],
                        class_id=class_id,
                        year_or_semester=data['year'],
                        created_by=current_user_id,  
                        updated_by=current_user_id
                    )
                    db.session.add(new_academic_history)
                    db.session.commit()

                    return jsonify({'message': 'Academic History created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})

        @self.new_student_academic_history_ns.route('/multiple_academic_history/add')
        class AcademicHistoryAddMultiple(Resource):
            @self.new_student_academic_history_ns.doc('student_multiple_academic_history/add', security='jwt')
            @self.api.expect(self.student_multiple_academic_history_model, validate=True)
            @jwt_required()
            def post(self):
                try:
                    data = request.json.get('histories')
                    if not isinstance(data, list):
                
                        return jsonify({'message': 'Payload should be an array of objects', 'status': 400})

                    current_user_id = get_jwt_identity()
                    responses = []

                    for item in data:
                      
                        if not all(key in item for key in ['student_id', 'institution_type', 'board', 'state_for_stateboard', 'class_id', 'year', 'institute_id', 'course_id', 'learning_style']):
                           
                            return jsonify({'message': 'Missing required fields', 'status': 400})

                        new_academic_history = NewStudentAcademicHistory(
                            student_id=item.get('student_id'),
                            institution_type=item.get('institution_type'),
                            board=item.get('board'),
                            state_for_stateboard=item.get('state_for_stateboard'),
                            class_id=item.get('class_id'),
                            year_or_semester=item.get('year'),
                            university_name=item.get('university_name', None),  
                            learning_style=item.get('learning_style'),
                            institute_id=item.get('institute_id'),
                            course_id=item.get('course_id'),
                            created_by=current_user_id,
                            updated_by=current_user_id
                        )
                        db.session.add(new_academic_history)
                    
                    db.session.commit()
                    responses.append({'message': 'Academic Histories created successfully', 'status': 200})
            
                    return jsonify(responses)
                except Exception as e:
                    db.session.rollback()
           
                    return jsonify({'message': str(e), 'status': 500})

        @self.new_student_academic_history_ns.route('/multiple_academic_history/edit')
        class MultipleAcademicHistoryEdit(Resource):
            @self.new_student_academic_history_ns.doc('student_multiple_academic_history/edit', security='jwt')
            @self.api.expect(self.student_multiple_academic_history_edit_model, validate=True)
            @jwt_required()
            def put(self):
                
                    try:
                        data = request.json.get('histories')
                        if not data:
                
                            return jsonify({'message': 'No data provided', 'status': 400})

                        current_user_id = get_jwt_identity()
                        responses = []

                        for item in data:
                            record_id = item.get('id')
                            record = NewStudentAcademicHistory.query.get(record_id)
                            
                            if record:
                                
                                record.student_id = item.get('student_id', record.student_id)
                                record.institution_type = item.get('institution_type', record.institution_type)
                                record.board = item.get('board', record.board)
                                record.state_for_stateboard = item.get('state_for_stateboard', record.state_for_stateboard)
                                record.institute_id = item.get('institute_id', record.institute_id)
                                record.course_id = item.get('course_id', record.course_id)
                                record.learning_style = item.get('learning_style', record.learning_style)
                                record.class_id = item.get('class_id', record.class_id)
                                record.year_or_semester = item.get('year', record.year_or_semester)
                                record.updated_by = current_user_id
                                record.updated_at = datetime.now()

                                responses.append({'id': record.id, 'message': 'Academic History updated successfully'})
                            else:
                                
                                responses.append({'id': record_id, 'message': 'Record not found'})

                        db.session.commit()
                       
                        return jsonify({'message': 'Academic Histories updated successfully', 'status': 200, 'data': responses})
                    except Exception as e:
                        db.session.rollback()
                  
                        return jsonify({'message': str(e), 'status': 500})

        @self.new_student_academic_history_ns.route('/edit/<int:id>')
        class AcademicHistoryEdit(Resource):
            @self.new_student_academic_history_ns.doc('edit_academic_history', security='jwt')
            @self.new_student_academic_history_ns.expect(self.student_academic_history_model, validate=True)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    academic_history = NewStudentAcademicHistory.query.filter_by(id=id, is_active=True).first()
                    
                    if not academic_history:
                        return jsonify({'message': 'Academic History not found', 'status': 404})

                    academic_history.student_id = data.get('student_id', academic_history.student_id)
                    academic_history.institution_type = data.get('institution_type', academic_history.institution_type)  
                    academic_history.board = data.get('board', academic_history.board)
                    academic_history.state_for_stateboard = data.get('state_for_stateboard', academic_history.state_for_stateboard)
                    academic_history.institute_id = data.get('institution_id', academic_history.institute_id)  
                    academic_history.course_id = data.get('course_id', academic_history.course_id)  
                    academic_history.learning_style = data.get('learning_style', academic_history.learning_style)
                    academic_history.class_id = data.get('class_id', academic_history.class_id)  
                    academic_history.year_or_semester = data.get('year', academic_history.year_or_semester) 
                    academic_history.updated_by = get_jwt_identity()
                    academic_history.updated_at = datetime.now()

                    db.session.commit()
                    return jsonify({'message': 'Academic History updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})

        @self.new_student_academic_history_ns.route('/get/<int:id>')
        class AcademicHistoryGet(Resource):
            @self.new_student_academic_history_ns.doc('get_academic_history', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    student_academic_historyes = NewStudentAcademicHistory.query.filter_by(student_id=id, is_active=True).all()
                    
                    if not student_academic_historyes:
                        return jsonify({'message': 'Academic History not found', 'status': 404})
                    else:
                        student_academic_historyes_data = []
                            
                        for student_academic_history in student_academic_historyes:
                            institution_name = None
                            if student_academic_history.institute_id:
                                institution = Institution.query.get(student_academic_history.institute_id)
                                if institution:
                                    institution_name = institution.institution_name
                            student_academic_history_data = {
                                "id":student_academic_history.id,
                                "student_id": student_academic_history.student_id,
                                "institution_type": student_academic_history.institution_type,
                                "board": student_academic_history.board,
                                "state_for_stateboard": student_academic_history.state_for_stateboard,
                                'institute_name': institution_name,
                                'institute_id': student_academic_history.institute_id,
                                "course_id": student_academic_history.course_id,
                                "learning_style": student_academic_history.learning_style,
                                "class_id": student_academic_history.class_id,
                                "year": student_academic_history.year_or_semester,
                                'created_at': student_academic_history.created_at,
                                'updated_at': student_academic_history.updated_at,
                                'is_active': student_academic_history.is_active
                            }
                            student_academic_historyes_data.append(student_academic_history_data)
                        print(student_academic_history_data)
                       
                        return jsonify({'message': 'Student Academic History found Successfully', 'status': 200,'data':student_academic_historyes_data})
                except Exception as e:
                    return jsonify({'message': str(e), 'status': 500})

        @self.new_student_academic_history_ns.route('/delete/<int:id>')
        class AcademicHistoryDelete(Resource):
            @self.new_student_academic_history_ns.doc('delete_academic_history', security='jwt')
            @jwt_required()
            def delete(self, id):
                try:
                    academic_history = NewStudentAcademicHistory.query.filter_by(id=id, is_active=True).first()
                    
                    if not academic_history:
                        return jsonify({'message': 'Academic History not found', 'status': 404})

                    academic_history.is_active = False
                    academic_history.updated_at = datetime.now()
                    academic_history.updated_by = get_jwt_identity()

                    db.session.commit()
                    return jsonify({'message': 'Academic History deleted successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})

        @self.new_student_academic_history_ns.route('/activate/<int:id>')
        class AcademicHistoryActivate(Resource):
            @self.new_student_academic_history_ns.doc('activate_academic_history', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    academic_history = NewStudentAcademicHistory.query.filter_by(id=id).first()
                    
                    if not academic_history:
                        return jsonify({'message': 'Academic History not found', 'status': 404})

                    academic_history.is_active = True
                    academic_history.updated_at = datetime.now()
                    academic_history.updated_by = get_jwt_identity()

                    db.session.commit()
                    return jsonify({'message': 'Academic History activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})

        @self.new_student_academic_history_ns.route('/deactivate/<int:id>')
        class AcademicHistoryDeactivate(Resource):
            @self.new_student_academic_history_ns.doc('deactivate_academic_history', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    academic_history = NewStudentAcademicHistory.query.filter_by(id=id).first()
                    
                    if not academic_history:
                        return jsonify({'message': 'Academic History not found', 'status': 404})

                    academic_history.is_active = False
                    academic_history.updated_at = datetime.now()
                    academic_history.updated_by = get_jwt_identity()

                    db.session.commit()
                    return jsonify({'message': 'Academic History deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})
        self.api.add_namespace(self.new_student_academic_history_ns)


        