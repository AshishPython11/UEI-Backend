from datetime import datetime
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations, logger
from flask_restx import Namespace, Resource, fields
from app.models.student import CollegeAcademicHistory, CourseMaster, Institution

class CollegeAcademicHistoryController:
    def __init__(self, api):
        self.api = api
        self.college_academic_history_model = self.api.model('CollegeAcademicHistory', {
            'student_id': fields.Integer(required=True, description='Student ID'),
            'institution_type': fields.String(required=True, description='Type of the institution'),
            'institute_id': fields.Integer(required=True, description='ID of the institution'),
            'course_id': fields.Integer(required=True, description='ID of the course'),
            'learning_style': fields.String(required=False, description='Learning style'),
            'year_or_semester': fields.String(required=False, description='Year or semester'),
            'university_name': fields.String(required=False, description='University name')
        })

        self.college_multiple_academic_history_model = self.api.model('CollegeAcademicHistories', {
            'histories': fields.List(fields.Nested(self.college_academic_history_model), required=True, description='List of College Academic Histories')
        })

        self.college_academic_history_edit_model = self.api.model('CollegeAcademicHistoryEdit', {
            'student_id': fields.Integer(required=True, description='Student ID'),
            'institution_type': fields.String(required=True, description='Type of the institution'),
            'institute_id': fields.Integer(required=True, description='ID of the institution'),
            'course_id': fields.Integer(required=True, description='ID of the course'),
            'learning_style': fields.String(required=False, description='Learning style'),
            'year_or_semester': fields.String(required=False, description='Year or semester'),
            'university_name': fields.String(required=False, description='University name')
        })

        self.college_multiple_academic_history_edit_model = self.api.model('CollegeAcademicHistoriesEdit', {
            'histories': fields.List(fields.Nested(self.college_academic_history_edit_model), required=True, description='List of College Academic Histories for Editing')
        })

        self.college_academic_history_bp = Blueprint('college_academic_history', __name__)
        self.college_academic_history_ns = Namespace('college_academic_history', description='College Academic History Details', authorizations=authorizations)
        
        self.register_routes()

    def register_routes(self):
 
        @self.college_academic_history_ns.route('/list')
        class CollegeAcademicHistoryList(Resource):
            @self.college_academic_history_ns.doc('college_academic_history/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    academic_histories = CollegeAcademicHistory.query.filter_by(is_active=True).all()
                    data = []
                    for history in academic_histories:
                        institution_name = None
                        course_name = None

                        if history.institute_id:
                            institution = Institution.query.get(history.institute_id)
                            if institution:
                                institution_name = institution.institution_name

             
                        if history.course_id:
                            course = CourseMaster.query.get(history.course_id)
                            if course:
                                course_name = course.course_name

                        history_data = {
                            'id': history.id,
                            'student_id': history.student_id,
                            'institution_type': history.institution_type,
                            'institute_id': history.institute_id,
                            'institute_name': institution_name,
                            'course_id': history.course_id,
                            'course_name': course_name,
                            'learning_style': history.learning_style,
                            'year_or_semester': history.year_or_semester,
                            'university_name': history.university_name,
                            'created_at': history.created_at,
                            'updated_at': history.updated_at,
                            'is_active': history.is_active
                        }
                        data.append(history_data)

                    if not data:
                        logger.warning("No College Academic Histories found")
                        return jsonify({'message': 'No College Academic Histories found', 'status': 404})
                    else:
                        logger.info("College Academic Histories found successfully")
                        return jsonify({'message': 'College Academic Histories found successfully', 'status': 200, 'data': data})
                except Exception as e:
                    logger.error(f"Error fetching college academic histories: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.college_academic_history_ns.route('/add')
        class CollegeAcademicHistoryAdd(Resource):
            @self.college_academic_history_ns.doc('college_academic_history/add', security='jwt')
            @self.api.expect(self.college_academic_history_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    current_user_id = get_jwt_identity()

                    new_academic_history = CollegeAcademicHistory(
                        student_id=data['student_id'],
                        institution_type=data['institution_type'],
                        institute_id=data['institute_id'],
                        course_id=data['course_id'],
                        learning_style=data.get('learning_style'),
                        year_or_semester=data.get('year_or_semester'),
                        university_name=data.get('university_name'),
                        created_by=current_user_id,
                        updated_by=current_user_id
                    )
                    db.session.add(new_academic_history)
                    db.session.commit()

                    logger.info("College Academic History created successfully")
                    return jsonify({'message': 'College Academic History created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error adding college academic history: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.college_academic_history_ns.route('/multiple_academic_history/add')
        class CollegeAcademicHistoryAddMultiple(Resource):
            @self.college_academic_history_ns.doc('college_academic_history_multiple/add', security='jwt')
            @self.api.expect(self.college_multiple_academic_history_model, validate=True)
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
                        if not all(key in item for key in ['student_id', 'institution_type', 'institute_id', 'course_id']):
                            logger.warning("Missing required fields in payload")
                            return jsonify({'message': 'Missing required fields', 'status': 400})

                        new_academic_history = CollegeAcademicHistory(
                            student_id=item.get('student_id'),
                            institution_type=item.get('institution_type'),
                            institute_id=item.get('institute_id'),
                            course_id=item.get('course_id'),
                            learning_style=item.get('learning_style'),
                            year_or_semester=item.get('year_or_semester'),
                            university_name=item.get('university_name'),
                            created_by=current_user_id,
                            updated_by=current_user_id
                        )
                        db.session.add(new_academic_history)
                    
                    db.session.commit()
                    responses.append({'message': 'College Academic Histories created successfully', 'status': 200})
                    logger.info("College Academic Histories created successfully")
                    return jsonify(responses)
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error adding multiple college academic histories: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.college_academic_history_ns.route('/multiple_academic_history/edit')
        class CollegeAcademicHistoryEditMultiple(Resource):
            @self.college_academic_history_ns.doc('college_academic_history_multiple/edit', security='jwt')
            @self.api.expect(self.college_multiple_academic_history_edit_model, validate=True)
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
                        record = CollegeAcademicHistory.query.get(record_id)
                        
                        if record:
                            record.student_id = item.get('student_id', record.student_id)
                            record.institution_type = item.get('institution_type', record.institution_type)
                            record.institute_id = item.get('institute_id', record.institute_id)
                            record.course_id = item.get('course_id', record.course_id)
                            record.learning_style = item.get('learning_style', record.learning_style)
                            record.year_or_semester = item.get('year_or_semester', record.year_or_semester)
                            record.university_name = item.get('university_name', record.university_name)
                            record.updated_by = current_user_id
                            record.updated_at = datetime.now()

                            responses.append({'id': record.id, 'message': 'College Academic History updated successfully'})
                        else:
                            logger.warning(f"Record with ID {record_id} not found")
                            responses.append({'id': record_id, 'message': 'Record not found'})

                    db.session.commit()
                    logger.info("College Academic Histories updated successfully")
                    return jsonify({'message': 'College Academic Histories updated successfully', 'status': 200, 'data': responses})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error updating multiple college academic histories: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        @self.college_academic_history_ns.route('/get/<int:id>')
        class CollegeAcademicHistoryGet(Resource):
            @self.college_academic_history_ns.doc('college_academic_history/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    academic_history = CollegeAcademicHistory.query.get(id)
                    if not academic_history:
                        return jsonify({'message': 'College Academic History not found', 'status': 404})

                    institution_name = None
                    course_name = None

                    if academic_history.institute_id:
                        institution = Institution.query.get(academic_history.institute_id)
                        if institution:
                            institution_name = institution.institution_name

                    if academic_history.course_id:
                        course = CourseMaster.query.get(academic_history.course_id)
                        if course:
                            course_name = course.course_name

                    history_data = {
                        'id': academic_history.id,
                        'student_id': academic_history.student_id,
                        'institution_type': academic_history.institution_type,
                        'institute_id': academic_history.institute_id,
                        'institute_name': institution_name,
                        'course_id': academic_history.course_id,
                        'course_name': course_name,
                        'learning_style': academic_history.learning_style,
                        'year_or_semester': academic_history.year_or_semester,
                        'university_name': academic_history.university_name,
                        'created_at': academic_history.created_at,
                        'updated_at': academic_history.updated_at,
                        'is_active': academic_history.is_active
                    }

                    logger.info("College Academic History found successfully")
                    return jsonify({'message': 'College Academic History found successfully', 'status': 200, 'data': history_data})
                except Exception as e:
                    logger.error(f"Error retrieving college academic history: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.college_academic_history_ns.route('/edit/<int:id>')
        class CollegeAcademicHistoryEdit(Resource):
            @self.college_academic_history_ns.doc('edit_college_academic_history', security='jwt')
            @self.api.expect(self.college_academic_history_edit_model, validate=True)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    academic_history = CollegeAcademicHistory.query.filter_by(id=id, is_active=True).first()

                    if not academic_history:
                        return jsonify({'message': 'College Academic History not found', 'status': 404})

                    academic_history.student_id = data.get('student_id', academic_history.student_id)
                    academic_history.institution_type = data.get('institution_type', academic_history.institution_type)
                    academic_history.institute_id = data.get('institute_id', academic_history.institute_id)
                    academic_history.course_id = data.get('course_id', academic_history.course_id)
                    academic_history.learning_style = data.get('learning_style', academic_history.learning_style)
                    academic_history.year_or_semester = data.get('year_or_semester', academic_history.year_or_semester)
                    academic_history.university_name = data.get('university_name', academic_history.university_name)
                    academic_history.updated_by = get_jwt_identity()
                    academic_history.updated_at = datetime.now()

                    db.session.commit()
                    return jsonify({'message': 'College Academic History updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})

        @self.college_academic_history_ns.route('/delete/<int:id>')
        class CollegeAcademicHistoryDelete(Resource):
            @self.college_academic_history_ns.doc('delete_college_academic_history', security='jwt')
            @jwt_required()
            def delete(self, id):
                try:
                    academic_history = CollegeAcademicHistory.query.filter_by(id=id, is_active=True).first()

                    if not academic_history:
                        return jsonify({'message': 'College Academic History not found', 'status': 404})

                    academic_history.is_deleted = True
                    academic_history.updated_at = datetime.now()
                    academic_history.updated_by = get_jwt_identity()

                    db.session.commit()
                    return jsonify({'message': 'College Academic History deleted successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})
        @self.college_academic_history_ns.route('/alldata')
        class CollegeAcademicHistoryList(Resource):
            @self.college_academic_history_ns.doc('college_academic_history/alldata', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    academic_histories = CollegeAcademicHistory.query.filter_by().all()
                    data = []
                    for history in academic_histories:
                        institution_name = None
                        course_name = None

                        # Fetch institution name if institute_id exists
                        if history.institute_id:
                            institution = Institution.query.get(history.institute_id)
                            if institution:
                                institution_name = institution.institution_name

                        # Fetch course name if course_id exists
                        if history.course_id:
                            course = CourseMaster.query.get(history.course_id)
                            if course:
                                course_name = course.course_name

                        history_data = {
                            'id': history.id,
                            'student_id': history.student_id,
                            'institution_type': history.institution_type,
                            'institute_id': history.institute_id,
                            'institute_name': institution_name,
                            'course_id': history.course_id,
                            'course_name': course_name,
                            'learning_style': history.learning_style,
                            'year_or_semester': history.year_or_semester,
                            'university_name': history.university_name,
                            'created_at': history.created_at,
                            'updated_at': history.updated_at,
                            'is_active': history.is_active
                        }
                        data.append(history_data)

                    if not data:
                        logger.warning("No College Academic Histories found")
                        return jsonify({'message': 'No College Academic Histories found', 'status': 404})
                    else:
                        logger.info("College Academic Histories found successfully")
                        return jsonify({'message': 'College Academic Histories found successfully', 'status': 200, 'data': data})
                except Exception as e:
                    logger.error(f"Error fetching college academic histories: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.college_academic_history_ns.route('/activate/<int:id>')
        class CollegeAcademicHistoryActivate(Resource):
            @self.college_academic_history_ns.doc('activate_college_academic_history', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    academic_history = CollegeAcademicHistory.query.filter_by(id=id).first()

                    if not academic_history:
                        return jsonify({'message': 'College Academic History not found', 'status': 404})

                    academic_history.is_active = True
                    academic_history.updated_at = datetime.now()
                    academic_history.updated_by = get_jwt_identity()

                    db.session.commit()
                    return jsonify({'message': 'College Academic History activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})

        @self.college_academic_history_ns.route('/deactivate/<int:id>')
        class CollegeAcademicHistoryDeactivate(Resource):
            @self.college_academic_history_ns.doc('deactivate_college_academic_history', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    academic_history = CollegeAcademicHistory.query.filter_by(id=id).first()

                    if not academic_history:
                        return jsonify({'message': 'College Academic History not found', 'status': 404})

                    academic_history.is_active = False
                    academic_history.updated_at = datetime.now()
                    academic_history.updated_by = get_jwt_identity()

                    db.session.commit()
                    return jsonify({'message': 'College Academic History deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})
        self.api.add_namespace(self.college_academic_history_ns)