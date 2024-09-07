from datetime import datetime
import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations,logger
from flask_restx import Api, Namespace, Resource, fields
from app.models.student import AcademicHistory

class StudentAcademicHistoryController:
    def __init__(self,api):
        self.api = api
        self.student_academic_history_model = api.model('AcademicHistory', {
            'student_id': fields.String(required=True, description='Student Id'),
            'institution_id': fields.String(required=True, description='Institute Id'),
            'course_id': fields.String(required=True, description='Course Id'),
            'class_id': fields.String(required=True, description='Class Id'),
            'starting_date': fields.String(required=True, description='Starting Date'),
            'ending_date': fields.String(required=True, description='Ending Date'),
            'learning_style': fields.String(required=True, description='Learning Style')
        })
        self.student_multiple_academic_history_model = self.api.model('AcademicHistories', {
            'histories': fields.List(fields.Nested(self.student_academic_history_model), required=True, description='List of Academic Histories')
        })
        student_academic_history_edit_model = self.api.model('AcademicHistoryEdit', {
            'id': fields.Integer(required=True, description='ID of the record to be updated'),
            'student_id': fields.String(required=True, description='Student Id'),
            'institution_id': fields.String(required=True, description='Institution Id'),
            'course_id': fields.String(required=True, description='Course Id'),
            'class_id': fields.String(required=True, description='Class Id'),
            'ending_date': fields.Date(required=True, description='Ending Date'),
            'starting_date': fields.Date(required=True, description='Starting Date'),
            'learning_style': fields.String(required=True, description='Learning Style')
        })

        # Define a model for an array of academic history objects for editing
        self.student_multiple_academic_history_edit_model = self.api.model('AcademicHistoriesEdit', {
            'histories': fields.List(fields.Nested(student_academic_history_edit_model), required=True, description='List of Academic Histories for Editing')
        })
        
        self.student_academic_history_bp = Blueprint('student_academic_history', __name__)
        self.student_academic_history_ns = Namespace('student_academic_history', description='Student Academic History Details', authorizations=authorizations)
        
        self.register_routes()

        
    def register_routes(self):
        @self.student_academic_history_ns.route('/list')
        class StudentAcademicHistoryList(Resource):
            @self.student_academic_history_ns.doc('student_academic_history/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    student_academic_historyes = AcademicHistory.query.filter_by(is_active=1).all()
                    student_academic_historyes_data = []
                    
                    for student_academic_history in student_academic_historyes:
                        student_academic_history_data = {
                            'id': student_academic_history.academic_history_id,
                            'student_id': student_academic_history.student_id,
                            'institution_id': student_academic_history.institution_id,
                            'course_id': student_academic_history.course_id,
                            'ending_date': student_academic_history.ending_date,
                            'class_id': student_academic_history.class_id,
                            'starting_date': student_academic_history.starting_date,
                            'learning_style': student_academic_history.learning_style,
                            'is_active': student_academic_history.is_active,
                            'created_at':student_academic_history.created_at,
                            'updated_at':student_academic_history.updated_at,
                        }
                        student_academic_historyes_data.append(student_academic_history_data)
                    
                    if not student_academic_historyes_data:
                        logger.warning("No StudentAcademicHistory found")
                        return jsonify({'message': 'No StudentAcademicHistory found', 'status': 404})
                    else:
                        logger.info("StudentAcademicHistorys found Successfully")
                        return jsonify({'message': 'StudentAcademicHistorys found Successfully', 'status': 200, 'data': student_academic_historyes_data})
                except Exception as e:
                 
                    logger.error(f"Error fetching rolstudent academic history  information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.student_academic_history_ns.route('/alldata')
        class StudentAcademicHistoryList(Resource):
            @self.student_academic_history_ns.doc('student_academic_history/alldata', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    student_academic_historyes = AcademicHistory.query.all()
                    student_academic_historyes_data = []
                    
                    for student_academic_history in student_academic_historyes:
                        student_academic_history_data = {
                            'id': student_academic_history.academic_history_id,
                            'student_id': student_academic_history.student_id,
                            'institution_id': student_academic_history.institution_id,
                            'course_id': student_academic_history.course_id,
                            'ending_date': student_academic_history.ending_date,
                            'class_id': student_academic_history.class_id,
                            'starting_date': student_academic_history.starting_date,
                            'learning_style': student_academic_history.learning_style,
                            'is_active': student_academic_history.is_active,
                            'created_at':student_academic_history.created_at,
                            'updated_at':student_academic_history.updated_at,
                        }
                        student_academic_historyes_data.append(student_academic_history_data)
                    
                    if not student_academic_historyes_data:
                        logger.warning("No StudentAcademicHistory found")
                        return jsonify({'message': 'No StudentAcademicHistory found', 'status': 404})
                    else:
                        logger.info("StudentAcademicHistorys found Successfully")
                        return jsonify({'message': 'StudentAcademicHistorys found Successfully', 'status': 200, 'data': student_academic_historyes_data})
                except Exception as e:
                 
                    logger.error(f"Error fetching rolstudent academic history  information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        @self.student_academic_history_ns.route('/add')
        class AcademicHistoryAdd(Resource):
            @self.student_academic_history_ns.doc('student_academic_history/add', security='jwt')
            @self.api.expect(self.student_academic_history_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    student_id = data.get('student_id')
                    institution_id = data.get('institution_id')
                    course_id = data.get('course_id')
                    class_id = data.get('class_id')
                    ending_date = data.get('ending_date')
                    starting_date = data.get('starting_date')
                    learning_style = data.get('learning_style')
                    current_user_id = get_jwt_identity()
                    if not student_id :
                        logger.warning("No student_id found")
                        return jsonify({'message': 'Please Provide Student Id', 'status': 201})
                    if not institution_id :
                        logger.warning("No institution_id found")
                        return jsonify({'message': 'Please Provide Institute Id', 'status': 201})
                    if not course_id :
                        logger.warning("No course_id found")
                        return jsonify({'message': 'Please Provide Course Id', 'status': 201})
                    if not class_id :
                        logger.warning("No class_id found")
                        return jsonify({'message': 'Please Provide class Id', 'status': 201})
                    if not ending_date :
                        logger.warning("No ending_date found")
                        return jsonify({'message': 'Please Provide Ending Date', 'status': 201})
                    if not starting_date :
                        logger.warning("No starting_date found")
                        return jsonify({'message': 'Please Provide Starting Date', 'status': 201})
                    if not learning_style :
                        logger.warning("No learning_style found")
                        return jsonify({'message': 'Please Provide Learning Style', 'status': 201})
                    else:
                        student_academic_history = AcademicHistory(student_id=student_id,institution_id=institution_id,course_id=course_id,class_id=class_id,ending_date=ending_date,starting_date=starting_date,learning_style=learning_style,is_active=1,created_by=current_user_id)
                        db.session.add(student_academic_history)
                        db.session.commit()
                        logger.info("Student Academic Historys created Successfully")
                        return jsonify({'message': 'Student Academic History created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error adding rolstudent academic history  information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})


            @self.student_academic_history_ns.route('/multiple_academic_history/add')
            class AcademicHistoryAdd(Resource):
                @self.student_academic_history_ns.doc('student_multiple_academic_history/add', security='jwt')
                @self.api.expect(self.student_multiple_academic_history_model, validate=True)
                @jwt_required()
                def post(self):
                    try:
                        data = request.json.get('histories')  # Expecting an array of objects under 'histories' key
                        if not isinstance(data, list):
                            logger.warning("No StudentAcademicHistory found")
                            return jsonify({'message': 'Payload should be an array of objects', 'status': 400})

                        current_user_id = get_jwt_identity()
                        responses = []

                        for item in data:
                            student_id = item.get('student_id')
                            institution_id = item.get('institution_id')
                            course_id = item.get('course_id')
                            class_id = item.get('class_id')
                            ending_date = item.get('ending_date')
                            starting_date = item.get('starting_date')
                            learning_style = item.get('learning_style')

                            if not student_id:
                                logger.warning("No student_id found")
                                responses.append({'message': 'Please Provide Student Id', 'status': 201, 'item': item})
                                continue
                            if not institution_id:
                                logger.warning("No institution_id found")
                                responses.append({'message': 'Please Provide Institution Id', 'status': 201, 'item': item})
                                continue
                            if not course_id:
                                logger.warning("No course_id found")
                                responses.append({'message': 'Please Provide Course Id', 'status': 201, 'item': item})
                                continue
                            if not class_id:
                                logger.warning("No class_id found")
                                responses.append({'message': 'Please Provide class Id', 'status': 201, 'item': item})
                                continue
                            if not ending_date:
                                logger.warning("No ending_date found")
                                responses.append({'message': 'Please Provide Ending Date', 'status': 201, 'item': item})
                                continue
                            if not starting_date:
                                logger.warning("No starting_date found")
                                responses.append({'message': 'Please Provide Starting Date', 'status': 201, 'item': item})
                                continue
                            if not learning_style:
                                logger.warning("No learning_style found")
                                responses.append({'message': 'Please Provide Learning Style', 'status': 201, 'item': item})
                                continue

                            student_academic_history = AcademicHistory(
                                student_id=student_id,
                                institution_id=institution_id,
                                course_id=course_id,
                                ending_date=ending_date,
                                starting_date=starting_date,
                                class_id=class_id,
                                learning_style=learning_style,
                                is_active=1,
                                created_by=current_user_id
                            )
                            db.session.add(student_academic_history)
                        
                        db.session.commit()
                        responses.append({'message': 'Academic History Created successfully', 'status': 200})
                        logger.info("Student Academic Historys created Successfully")
                        return jsonify(responses)
                    except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error adding rolstudent academic history  information: {str(e)}")
                        return jsonify({'message': str(e), 'status': 500})

        @self.student_academic_history_ns.route('/multiple_academic_history/edit')
        class AcademicHistoryMultipleEdit(Resource):
            @self.student_academic_history_ns.doc('student_multiple_academic_history/edit', security='jwt')
            @self.api.expect(self.student_multiple_academic_history_edit_model, validate=True)
            @jwt_required()
            def put(self):
                try:
                    data = request.json.get('histories')  # Expecting an array of objects under 'histories' key
                    if not isinstance(data, list):
                        return jsonify({'message': 'Payload should be an array of objects', 'status': 400})

                    current_user_id = get_jwt_identity()
                    responses = []

                    for item in data:
                        record_id = item.get('id')
                        student_id = item.get('student_id')
                        institution_id = item.get('institution_id')
                        course_id = item.get('course_id')
                        class_id = item.get('class_id')
                        ending_date = item.get('ending_date')
                        starting_date = item.get('starting_date')
                        learning_style = item.get('learning_style')

                        if not record_id:
                            logger.warning("No record_id found")
                            responses.append({'message': 'Please Provide Record Id', 'status': 201, 'item': item})
                            continue
                        if not student_id:
                            logger.warning("No student_id found")
                            responses.append({'message': 'Please Provide Student Id', 'status': 201, 'item': item})
                            continue
                        if not institution_id:
                            logger.warning("No institution_id found")
                            responses.append({'message': 'Please Provide Institution Id', 'status': 201, 'item': item})
                            continue
                        if not course_id:
                            logger.warning("No course_id found")
                            responses.append({'message': 'Please Provide Course Id', 'status': 201, 'item': item})
                            continue
                        if not class_id:
                            logger.warning("No class_id found")
                            responses.append({'message': 'Please Provide class Id', 'status': 201, 'item': item})
                            continue
                        if not ending_date:
                            logger.warning("No v found")
                            responses.append({'message': 'Please Provide Ending Date', 'status': 201, 'item': item})
                            continue
                        if not starting_date:
                            logger.warning("No starting_date found")
                            responses.append({'message': 'Please Provide Starting Date', 'status': 201, 'item': item})
                            continue
                        if not learning_style:
                            logger.warning("No learning_style found")
                            responses.append({'message': 'Please Provide Learning Style', 'status': 201, 'item': item})
                            continue

                        student_academic_history = AcademicHistory.query.filter_by(academic_history_id=record_id).first()
                        if not student_academic_history:
                            logger.warning("No StudentAcademicHistory found")
                            responses.append({'message': f'Academic History with id {record_id} not found', 'status': 404, 'item': item})
                            continue

                        student_academic_history.student_id = student_id
                        student_academic_history.institution_id = institution_id
                        student_academic_history.course_id = course_id
                        student_academic_history.class_id = class_id
                        student_academic_history.ending_date = ending_date
                        student_academic_history.starting_date = starting_date
                        student_academic_history.learning_style = learning_style
                        student_academic_history.updated_by = current_user_id
                        db.session.commit()
                    logger.info("Student Academic Historys updated Successfully")
                    responses.append({'message': 'Academic Histuory Updated successfully', 'status': 200})

                    return jsonify(responses)
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error editing rolstudent academic history  information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        
        @self.student_academic_history_ns.route('/edit/<int:id>')
        class AcademicHistoryEdit(Resource):
            @self.student_academic_history_ns.doc('student_academic_history/edit', security='jwt')
            @api.expect(self.student_academic_history_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    student_id = data.get('student_id')
                    institution_id = data.get('institution_id')
                    course_id = data.get('course_id')
                    class_id = data.get('class_id')
                    print(class_id)
                    ending_date = data.get('ending_date')
                    starting_date = data.get('starting_date')
                    learning_style = data.get('learning_style')
                    current_user_id = get_jwt_identity()
                    if not student_id :
                        logger.warning("No student_id found")
                        return jsonify({'message': 'Please Provide Student Id', 'status': 201})
                    if not institution_id :
                        logger.warning("No institution_id found")
                        return jsonify({'message': 'Please Provide Institute Id', 'status': 201})
                    if not course_id :
                        logger.warning("No course_id found")
                        return jsonify({'message': 'Please Provide Course Id', 'status': 201})
                    if not class_id :
                        logger.warning("No class_id found")
                        return jsonify({'message': 'Please Provide Class Id', 'status': 201})
                    if not ending_date :
                        logger.warning("No ending_date found")
                        return jsonify({'message': 'Please Provide Ending Year', 'status': 201})
                    if not starting_date :
                        logger.warning("No starting_date found")
                        return jsonify({'message': 'Please Provide Starting Date', 'status': 201})
                    if not learning_style :
                        logger.warning("No learning_style found")
                        return jsonify({'message': 'Please Provide Learning Style', 'status': 201})
                    else:
                        student_academic_history = AcademicHistory.query.get(id)
                        if not student_academic_history:
                            logger.warning("No StudentAcademicHistory found")
                            return jsonify({'message': 'Student Academic History not found', 'status': 404})
                        else:
                            student_academic_history.student_id = student_id
                            student_academic_history.institution_id = institution_id
                            student_academic_history.course_id = course_id
                            student_academic_history.class_id = class_id
                            student_academic_history.ending_date = ending_date
                            student_academic_history.starting_date = starting_date
                            student_academic_history.learning_style = learning_style
                            student_academic_history.updated_by = current_user_id
                            db.session.commit()
                            logger.info("Student Academic Historys updated Successfully")
                            return jsonify({'message': 'Student Academic History updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error editing rolstudent academic history  information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                        
            @self.student_academic_history_ns.doc('student_academic_history/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
              
                    student_academic_historyes = AcademicHistory.query.filter_by(student_id=id,is_active=1).all()
                    if not student_academic_historyes:
                        logger.warning("No StudentAcademicHistory found")
                        return jsonify({'message': 'Student Academic History not found', 'status': 404})
                    else:
                        student_academic_historyes_data = []
                        
                        for student_academic_history in student_academic_historyes:
                            student_academic_history_data = {
                                'id': student_academic_history.academic_history_id,
                                'student_id': student_academic_history.student_id,
                                'institution_id': student_academic_history.institution_id,
                                'course_id': student_academic_history.course_id,
                                'class_id': student_academic_history.class_id,
                                'ending_date': student_academic_history.ending_date,
                                'starting_date': student_academic_history.starting_date,
                                'learning_style': student_academic_history.learning_style,
                                'is_active': student_academic_history.is_active,
                                'created_at':student_academic_history.created_at,
                                'updated_at':student_academic_history.updated_at,
                            }
                            student_academic_historyes_data.append(student_academic_history_data)
                        print(student_academic_history_data)
                        logger.info("Student Academic Historys found Successfully")
                        return jsonify({'message': 'Student Academic History found Successfully', 'status': 200,'data':student_academic_historyes_data})
                except Exception as e:
                    
                    logger.error(f"Error fetching rolstudent academic history  information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.student_academic_history_ns.route('delete/<int:id>')
        class StudentAcademicHistoryDelete(Resource):
            @self.student_academic_history_ns.doc('student_academic_history/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        student_academic_history = AcademicHistory.query.get(id)
                        if not student_academic_history:
                            logger.warning("No StudentAcademicHistory found")
                            return jsonify({'message': 'Student Academic History  not found', 'status': 404})
                        else:
                            student_academic_history.is_active = 0
                            db.session.commit()
                            logger.info("Student Academic Historys deleted Successfully")
                            return jsonify({'message': 'Student Academic History deleted successfully', 'status': 200})
                    except Exception as e:
                       
                        logger.error(f"Error deleting rolstudent academic history  information: {str(e)}")
                        return jsonify({'message': str(e), 'status': 500})
                    
        @self.student_academic_history_ns.route('/activate/<int:id>')
        class StudentAcademicHistoryActivate(Resource):
            @self.student_academic_history_ns.doc('student_academic_history/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    student_academic_history = AcademicHistory.query.get(id)
                    if not student_academic_history:
                        logger.warning("No StudentAcademicHistory found")
                        return jsonify({'message': 'Student Academic History not found', 'status': 404})
                    else:
                        student_academic_history.is_active = 1
                        db.session.commit()
                        logger.info("Student Academic Historys activated Successfully")
                        return jsonify({'message': 'Student Academic History activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error activating rolstudent academic history  information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.student_academic_history_ns.route('/deactivate/<int:id>')
        class StudentAcademicHistoryDeactivate(Resource):
            @self.student_academic_history_ns.doc('student_academic_history/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    student_academic_history = AcademicHistory.query.get(id)
                    if not student_academic_history:
                        logger.warning("No StudentAcademicHistory found")
                        return jsonify({'message': 'Student Academic History not found', 'status': 404})
                    else:
                        student_academic_history.is_active = 0
                        db.session.commit()
                        logger.info("Student Academic Historys deactivated Successfully")
                        return jsonify({'message': 'Student Academic History deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error deactivating rolstudent academic history  information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                
       
                
        self.api.add_namespace(self.student_academic_history_ns)