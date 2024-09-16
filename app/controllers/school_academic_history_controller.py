from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations, logger
from flask_restx import Namespace, Resource, fields
from app.models.student import SchoolAcademicHistory,ClassMaster

class SchoolAcademicHistoryController:
    def __init__(self, api):
        self.api = api
        self.school_academic_history_model = self.api.model('SchoolAcademicHistory', {
            'student_id': fields.Integer(required=True, description='Student ID'),
            'institution_type': fields.String(required=True, description='Type of the institution'),
            'board': fields.String(required=False, description='Educational board'),
            'state_for_stateboard': fields.String(required=False, description='State for state board'),
            'class_id': fields.Integer(required=True, description='ID of the class'),
            'class_or_course': fields.String(required=False, description='Class or course name')
        })

        self.school_multiple_academic_history_model = self.api.model('SchoolAcademicHistories', {
            'histories': fields.List(fields.Nested(self.school_academic_history_model), required=True, description='List of School Academic Histories')
        })

        self.school_academic_history_edit_model = self.api.model('SchoolAcademicHistoryEdit', {
            'student_id': fields.Integer(required=True, description='Student ID'),
            'institution_type': fields.String(required=True, description='Type of the institution'),
            'board': fields.String(required=False, description='Educational board'),
            'state_for_stateboard': fields.String(required=False, description='State for state board'),
            'class_id': fields.Integer(required=True, description='ID of the class'),
            'class_or_course': fields.String(required=False, description='Class or course name')
        })

        self.school_multiple_academic_history_edit_model = self.api.model('SchoolAcademicHistoriesEdit', {
            'histories': fields.List(fields.Nested(self.school_academic_history_edit_model), required=True, description='List of School Academic Histories for Editing')
        })

        self.school_academic_history_bp = Blueprint('school_academic_history', __name__)
        self.school_academic_history_ns = Namespace('school_academic_history', description='School Academic History Details', authorizations=authorizations)
        
        self.register_routes()

    def register_routes(self):
 
        @self.school_academic_history_ns.route('/list')
        class SchoolAcademicHistoryList(Resource):
            @self.school_academic_history_ns.doc('school_academic_history/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    academic_histories = SchoolAcademicHistory.query.filter_by(is_active=True).all()
                    data = []
                    for history in academic_histories:
             
                        class_name = None
                        if history.class_id:
                            class_info = ClassMaster.query.get(history.class_id)
                            if class_info:
                                class_name = class_info.class_name

                    for history in academic_histories:
                        history_data = {
                            'student_id': history.student_id,
                            'institution_type': history.institution_type,
                            'board': history.board,
                            'state_for_stateboard': history.state_for_stateboard,
                            'class_id': history.class_id,
                            'class_name': class_name,
                            'class_or_course': history.class_or_course,
                            'created_at': history.created_at,
                            'updated_at': history.updated_at,
                            'is_active': history.is_active
                        }
                        data.append(history_data)

                    if not data:
                        logger.warning("No School Academic Histories found")
                        return jsonify({'message': 'No School Academic Histories found', 'status': 404})
                    else:
                        logger.info("School Academic Histories found successfully")
                        return jsonify({'message': 'School Academic Histories found successfully', 'status': 200, 'data': data})
                except Exception as e:
                    logger.error(f"Error fetching school academic histories: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

     
        @self.school_academic_history_ns.route('/add')
        class SchoolAcademicHistoryAdd(Resource):
            @self.school_academic_history_ns.doc('school_academic_history/add', security='jwt')
            @self.api.expect(self.school_academic_history_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    current_user_id = get_jwt_identity()

                    new_academic_history = SchoolAcademicHistory(
                        student_id=data['student_id'],
                        institution_type=data['institution_type'],
                        board=data.get('board'),
                        state_for_stateboard=data.get('state_for_stateboard'),
                        class_id=data['class_id'],
                        class_or_course=data.get('class_or_course'),
                        created_by=current_user_id,
                        updated_by=current_user_id
                    )
                    db.session.add(new_academic_history)
                    db.session.commit()

                    logger.info("School Academic History created successfully")
                    return jsonify({'message': 'School Academic History created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error adding school academic history: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        @self.school_academic_history_ns.route('/multiple_academic_history/add')
        class SchoolAcademicHistoryAddMultiple(Resource):
            @self.school_academic_history_ns.doc('school_academic_history_multiple/add', security='jwt')
            @self.api.expect(self.school_multiple_academic_history_model, validate=True)
            @jwt_required()
            def post(self):
                try:
                    data = request.json.get('histories')
                    if not isinstance(data, list):
                        logger.warning("Payload is not an array")
                        return jsonify({'message': 'Payload should be an array of objects', 'status': 400})

                    current_user_id = get_jwt_identity()
                    responses = []

                    for item in data:
                        if not all(key in item for key in ['student_id', 'institution_type', 'board', 'state_for_stateboard', 'class_id', 'class_or_course']):
                            logger.warning("Missing required fields in payload")
                            return jsonify({'message': 'Missing required fields', 'status': 400})

                        new_academic_history = SchoolAcademicHistory(
                            student_id=item.get('student_id'),
                            institution_type=item.get('institution_type'),
                            board=item.get('board'),
                            state_for_stateboard=item.get('state_for_stateboard'),
                            class_id=item.get('class_id'),
                            class_or_course=item.get('class_or_course'),
                            created_by=current_user_id,
                            updated_by=current_user_id
                        )
                        db.session.add(new_academic_history)
                    
                    db.session.commit()
                    responses.append({'message': 'School Academic Histories created successfully', 'status': 200})
                    logger.info("School Academic Histories created successfully")
                    return jsonify(responses)
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error adding multiple school academic histories: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        @self.school_academic_history_ns.route('/multiple_academic_history/edit')
        class SchoolAcademicHistoryEditMultiple(Resource):
            @self.school_academic_history_ns.doc('school_academic_history_multiple/edit', security='jwt')
            @self.api.expect(self.school_multiple_academic_history_edit_model, validate=True)
            @jwt_required()
            def put(self):
                try:
                    data = request.json.get('histories')
                    if not data:
                        logger.warning("No data provided")
                        return jsonify({'message': 'No data provided', 'status': 400})

                    current_user_id = get_jwt_identity()
                    responses = []

                    for item in data:
                        record_id = item.get('id')
                        record = SchoolAcademicHistory.query.get(record_id)
                        
                        if record:
                            record.student_id = item.get('student_id', record.student_id)
                            record.institution_type = item.get('institution_type', record.institution_type)
                            record.board = item.get('board', record.board)
                            record.state_for_stateboard = item.get('state_for_stateboard', record.state_for_stateboard)
                            record.class_id = item.get('class_id', record.class_id)
                            record.class_or_course = item.get('class_or_course', record.class_or_course)
                            record.updated_by = current_user_id
                            record.updated_at = datetime.now()

                            responses.append({'id': record.id, 'message': 'School Academic History updated successfully'})
                        else:
                            logger.warning(f"Record with ID {record_id} not found")
                            responses.append({'id': record_id, 'message': 'Record not found'})

                    db.session.commit()
                    logger.info("School Academic Histories updated successfully")
                    return jsonify({'message': 'School Academic Histories updated successfully', 'status': 200, 'data': responses})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error updating multiple school academic histories: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})



        @self.school_academic_history_ns.route('/edit/<int:id>')
        class SchoolAcademicHistoryEdit(Resource):
            @self.school_academic_history_ns.doc('edit_school_academic_history', security='jwt')
            @self.school_academic_history_ns.expect(self.school_academic_history_edit_model, validate=True)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    academic_history = SchoolAcademicHistory.query.filter_by(id=id, is_active=True).first()

                    if not academic_history:
                        return jsonify({'message': 'School Academic History not found', 'status': 404})

                    academic_history.student_id = data.get('student_id', academic_history.student_id)
                    academic_history.institution_type = data.get('institution_type', academic_history.institution_type)
                    academic_history.board = data.get('board', academic_history.board)
                    academic_history.state_for_stateboard = data.get('state_for_stateboard', academic_history.state_for_stateboard)
                    academic_history.class_id = data.get('class_id', academic_history.class_id)
                    academic_history.class_or_course = data.get('class_or_course', academic_history.class_or_course)
                    academic_history.updated_by = get_jwt_identity()
                    academic_history.updated_at = datetime.now()

                    db.session.commit()
                    return jsonify({'message': 'School Academic History updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})
        @self.school_academic_history_ns.route('/alldata')
        class SchoolAcademicHistoryList(Resource):
            @self.school_academic_history_ns.doc('school_academic_history/alldata', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    school_academic_histories = SchoolAcademicHistory.query.all()
                    school_academic_histories_data = []

                    for history in school_academic_histories:
                        # Fetch class_name if class_id exists
                        class_name = None
                        if history.class_id:
                            class_info = ClassMaster.query.get(history.class_id)
                            if class_info:
                                class_name = class_info.class_name

                        history_data = {
                            'id': history.id,
                            'student_id': history.student_id,
                            'institution_type': history.institution_type,  
                            'board': history.board,
                            'state_for_stateboard': history.state_for_stateboard,
                            'class_id': history.class_id,
                            'class_name': class_name,
                            'class_or_course': history.class_or_course,
                            'created_at': history.created_at,
                            'updated_at': history.updated_at,
                            'is_active': history.is_active
                        }
                        school_academic_histories_data.append(history_data)
                    
                    if not school_academic_histories_data:
                        logger.warning("No school academic histories found")
                        return jsonify({'message': 'No school academic histories found', 'status': 404})
                    else:
                        logger.info("School academic histories retrieved successfully")
                        return jsonify({'message': 'School Academic Histories retrieved successfully', 'status': 200, 'data': school_academic_histories_data})
                except Exception as e:
                    logger.error(f"Error fetching school academic history information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.school_academic_history_ns.route('/get/<int:id>')
        class SchoolAcademicHistoryGet(Resource):
            @self.school_academic_history_ns.doc('get_school_academic_history', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    # Query to fetch active school academic histories for the given student_id
                    school_academic_histories = SchoolAcademicHistory.query.filter_by(student_id=id, is_active=True).all()
                    
                    if not school_academic_histories:
                        return jsonify({'message': 'School Academic History not found', 'status': 404})
                    else:
                        school_academic_histories_data = []
                        
                        for school_academic_history in school_academic_histories:
                            class_name = None
                            if school_academic_history.class_id:
                                class_info = ClassMaster.query.get(school_academic_history.class_id)
                                if class_info:
                                    class_name = class_info.class_name
 
                            school_academic_history_data = {
                                "id": school_academic_history.id,
                                "student_id": school_academic_history.student_id,
                                "institution_type": school_academic_history.institution_type,
                                "board": school_academic_history.board,
                                "state_for_stateboard": school_academic_history.state_for_stateboard,
                                'class_id': school_academic_history.class_id,
                                'class_name':class_name,
                                "class_or_course": school_academic_history.class_or_course,
                                'created_at': school_academic_history.created_at,
                                'updated_at': school_academic_history.updated_at,
                                'is_active': school_academic_history.is_active
                            }
                            school_academic_histories_data.append(school_academic_history_data)
                        
                        logger.info("School Academic Histories found successfully")
                        return jsonify({'message': 'School Academic Histories found successfully', 'status': 200, 'data': school_academic_histories_data})
                except Exception as e:
                    logger.error(f"Error retrieving school academic histories: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.school_academic_history_ns.route('/delete/<int:id>')
        class SchoolAcademicHistoryDelete(Resource):
            @self.school_academic_history_ns.doc('delete_school_academic_history', security='jwt')
            @jwt_required()
            def delete(self, id):
                try:
                    academic_history = SchoolAcademicHistory.query.filter_by(id=id, is_active=True).first()

                    if not academic_history:
                        return jsonify({'message': 'School Academic History not found', 'status': 404})

                    academic_history.is_deleted = True
                    academic_history.updated_at = datetime.now()
                    academic_history.updated_by = get_jwt_identity()

                    db.session.commit()
                    return jsonify({'message': 'School Academic History deleted successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})
        @self.school_academic_history_ns.route('/activate/<int:id>')
        class SchoolAcademicHistoryActivate(Resource):
            @self.school_academic_history_ns.doc('activate_school_academic_history', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    school_academic_history = SchoolAcademicHistory.query.filter_by(id=id).first()
                    
                    if not school_academic_history:
                        return jsonify({'message': 'School Academic History not found', 'status': 404})

                    school_academic_history.is_active = True
                    school_academic_history.updated_at = datetime.now()
                    school_academic_history.updated_by = get_jwt_identity()

                    db.session.commit()
                    return jsonify({'message': 'School Academic History activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})
        @self.school_academic_history_ns.route('/deactivate/<int:id>')
        class SchoolAcademicHistoryDeactivate(Resource):
            @self.school_academic_history_ns.doc('deactivate_school_academic_history', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    school_academic_history = SchoolAcademicHistory.query.filter_by(id=id).first()
                    
                    if not school_academic_history:
                        return jsonify({'message': 'School Academic History not found', 'status': 404})

                    school_academic_history.is_active = False
                    school_academic_history.updated_at = datetime.now()
                    school_academic_history.updated_by = get_jwt_identity()

                    db.session.commit()
                    return jsonify({'message': 'School Academic History deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})
        self.api.add_namespace(self.school_academic_history_ns)