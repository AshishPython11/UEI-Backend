import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.adminuser import AdminBasicInformation
from app.models.student import StudentLogin,StudentFeedback,Feedback,Student
from sqlalchemy import desc
class FeedbackController:
    def __init__(self, api):
        self.api = api
        self.feedback_model = api.model('Feedback', {
            'question': fields.String(required=True, description='The feedback question'),
            'options': fields.List(fields.String, required=True, description='The options for the feedback question'),
           
        })

        self.student_feedback_model = api.model('StudentFeedback', {
            'student_id': fields.Integer(required=True, description='The ID of the student'),
            'feedbacks': fields.List(fields.Nested(api.model('FeedbackEntry', {
                'question': fields.String(required=True, description='The feedback question'),
                'answer': fields.String(required=True, description='The answer provided by the student')
            })))
        })
        self.feedback_bp = Blueprint('feedback', __name__)
        self.feedback_ns = Namespace('feedback', description='Feedback operations')
        self.register_routes()
    def register_routes(self):
        @self.feedback_ns.route('/list')
        class FeedbackList(Resource):
            @self.feedback_ns.doc('feedback/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    feedbacks = Feedback.query.filter_by(is_deleted=False).order_by(desc(Feedback.updated_at)).all()
                    feedbacks_data = []

                    for feedback in feedbacks:
                        created_by = 'Admin'
                        updated_by = 'Admin'
                        if feedback.created_by is not None:
                            createadmindata = AdminBasicInformation.query.filter_by(admin_login_id=feedback.created_by).first()
                            if createadmindata is not None:
                                created_by = createadmindata.first_name
                            else:
                                created_by = 'Admin'
                        if feedback.updated_by is not None:
                            updateadmindata = AdminBasicInformation.query.filter_by(admin_login_id=feedback.updated_by).first()
                            if updateadmindata is not None:
                                updated_by = updateadmindata.first_name
                            else:
                                updated_by = 'Admin'

                        options_str = feedback.options
                        options_list = []
                        if options_str:
                            try:
                                options_list = json.loads(options_str)
                            except Exception as e:
                                options_list = []

                        feedback_data = {
                            'id': feedback.id,
                            'question': feedback.question,
                            'options': options_list, 
                            'is_active': feedback.is_active,
                            'is_deleted': feedback.is_deleted,
                            'created_at': feedback.created_at,
                            'updated_at': feedback.updated_at,
                            'created_by': created_by,
                            'updated_by': updated_by,
                        }
                        feedbacks_data.append(feedback_data)

                    if not feedbacks_data:
                
                        return jsonify({'message': 'No feedback questions found', 'status': 404})
                    else:
                        return jsonify({'message': 'Feedback questions found successfully', 'status': 200, 'data': feedbacks_data})
                except Exception as e:
                    return jsonify({'message': str(e), 'status': 500})
        @self.feedback_ns.route('/add')
        class FeedbackAdd(Resource):
            @self.feedback_ns.doc('feedback/add', security='jwt')
            @self.api.expect(self.feedback_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    question = data.get('question')
                    options = data.get('options')
                    current_user_id = get_jwt_identity()
                    if not question or not options:
                        return jsonify({'message': 'Please provide question and options', 'status': 400})
                    else:
                        feedback = Feedback(question=question, options=options, is_active=1, created_by=current_user_id)
                        db.session.add(feedback)
                        db.session.commit()
                        return jsonify({'message': 'Feedback created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})
        @self.feedback_ns.route('/edit/<string:id>')
        class FeedbackEdit(Resource):
            @self.feedback_ns.doc('feedback/edit', security='jwt')
            @self.api.expect(self.feedback_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    question = data.get('question')
                    options = data.get('options')
                    current_user_id = get_jwt_identity()
                    if not question or not options:
                        return jsonify({'message': 'Please provide question and options', 'status': 400})
                    else:
                        feedback = Feedback.query.get(id)
                        if not feedback:
                            return jsonify({'message': 'Feedback not found', 'status': 404})
                        else:
                            feedback.question = question
                            feedback.options = options
                            feedback.updated_by = current_user_id
                            db.session.commit()
                            return jsonify({'message': 'Feedback updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})
        @self.feedback_ns.route('/delete/<string:id>')
        class FeedbackDelete(Resource):
            @self.feedback_ns.doc('feedback/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                try:
                    feedback = Feedback.query.get(id)
                    if not feedback:
                        return jsonify({'message': 'Feedback not found', 'status': 404})
                    else:
                        feedback.is_deleted = True
                        db.session.commit()
                        return jsonify({'message': 'Feedback deleted successfully', 'status': 200})
                except Exception as e:
                    return jsonify({'message': str(e), 'status': 500})
        @self.feedback_ns.route('/student_feedback')
        class StudentFeedbackAdd(Resource):
            @self.feedback_ns.doc('student_feedback/add', security='jwt')
            @self.api.expect(self.student_feedback_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    student_id = data.get('student_id')
                    feedbacks = data.get('feedbacks')

                    if not student_id or not feedbacks:
                        return jsonify({'message': 'Please provide student_id and feedbacks', 'status': 400})

                    for feedback_entry in feedbacks:
                        question = feedback_entry.get('question')
                        answer = feedback_entry.get('answer')

                        if not question:
                            return jsonify({'message': 'Each feedback entry must include a question', 'status': 400})

                        if answer is not None and len(answer.strip()) > 0:
                            student_feedback = StudentFeedback(
                                student_id=student_id,
                                question=question,
                                answer=answer
                            )
                            db.session.add(student_feedback)
                            db.session.commit()

                    return jsonify({'message': 'Student feedback submitted successfully', 'status': 200})


                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})
        @self.feedback_ns.route('/student_feedback/<string:student_id>')
        class StudentFeedbackGet(Resource):
            @self.feedback_ns.doc('student_feedback/get', security='jwt')
            @jwt_required()
            def get(self, student_id):
                try:
                    student = Student.query.filter_by(student_login_id=student_id).first()
                    if not student:
                        return jsonify({'message': 'Student not found', 'status': 404})

                    feedbacks = StudentFeedback.query.filter_by(student_id=student_id).all()
                    feedbacks_data = []

                    for feedback in feedbacks:
                        answer = feedback.answer

                        try:
                            answer = json.loads(answer) if isinstance(answer, str) and answer.startswith('[') else answer
                        except json.JSONDecodeError:
                            pass
                     

                        feedback_data = {
                            'id': feedback.id,
                            'student_id': feedback.student_id,
                            'question': feedback.question,
                            'answer': answer,
                            'is_active':feedback.is_active,
                            'student_name': f"{student.first_name} {student.last_name}",
                            'created_at': feedback.created_at
                        }
                        feedbacks_data.append(feedback_data)

                    if not feedbacks_data:
                 
                        return jsonify({'message': 'No feedback found', 'status': 404})
               
           
                    return jsonify({'message': 'Feedback retrieved successfully', 'status': 200, 'data': feedbacks_data})

                
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
        @self.feedback_ns.route('/all_student_feedback')
        class AllStudentFeedbackGet(Resource):
            @self.feedback_ns.doc('all_student_feedback/get', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    feedbacks = StudentFeedback.query.all()
                    grouped_feedbacks = {}
                    
                    for feedback in feedbacks:
                        student = Student.query.filter_by(student_login_id=feedback.student_id).first()
                        
                        if student:
                            student_name = f"{student.first_name} {student.last_name}"
                            student_is_active = student.is_active
                            student_created_at = student.created_at
                        else:
                            student_name = "Unknown Student"
                            student_is_active = None
                            student_created_at = None

                        answer = feedback.answer
                        try:
                            answer = json.loads(answer) if isinstance(answer, str) and answer.startswith('[') else answer
                        except json.JSONDecodeError:
                            pass

                        feedback_data = {
                            'id': feedback.id,
                            'question': feedback.question,
                            'answer': answer,
                        }

                        if student_name not in grouped_feedbacks:
                            grouped_feedbacks[student_name] = {
                                'created_at': student_created_at,
                                'is_active': student_is_active,
                                'responses': []
                            }

                        grouped_feedbacks[student_name]['responses'].append(feedback_data)

                    if not grouped_feedbacks:
            
                        return jsonify({'message': 'No feedback found', 'status': 404})

                    feedbacks_array = [
                        {
                            'student_name': student_name,
                            'created_at': details['created_at'],
                            'is_active': details['is_active'],
                            'responses': details['responses']
                        } 
                        for student_name, details in grouped_feedbacks.items()
                    ]
                    

                    return jsonify({'message': 'All Feedback retrieved successfully', 'status': 200, 'data': feedbacks_array})

                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
                
        @self.feedback_ns.route('/<string:id>')
        class FeedbackDetail(Resource):
            @self.feedback_ns.doc('feedback/get_by_id', security='jwt')
            @jwt_required()
            
            def get(self, id):
                """Get feedback details by ID"""
                feedback = Feedback.query.filter_by(id=id, is_deleted=False).first()
                if not feedback:
                    return jsonify({'message': 'Feedback not found', 'status': 404})
                else:
                    created_by = 'Admin'
                    updated_by = 'Admin'
                    if feedback.created_by is not None:
                        createadmindata = StudentLogin.query.filter_by(student_id=feedback.created_by).first()
                        if createadmindata is not None:
                            created_by = createadmindata.userid
                        else:
                            created_by = 'Admin'
                    if feedback.updated_by is not None:
                        updateadmindata = StudentLogin.query.filter_by(student_id=feedback.updated_by).first()
                        if updateadmindata is not None:
                            updated_by = updateadmindata.userid
                        else:
                            updated_by = 'Admin'

                    
                    options_str = feedback.options
                    options_list = []
                    if options_str:
                        try:
                            options_str = options_str.strip('{}')  
                            options_list = [opt.strip() for opt in options_str.split(',')]  
                        except Exception as e:
                            options_list = []  

                    feedback_data = {
                        'id': feedback.id,
                        'question': feedback.question,
                        'options': options_list,  
                        'is_active': feedback.is_active,
                        'is_deleted': feedback.is_deleted,
                        'created_at': feedback.created_at,
                        'updated_at': feedback.updated_at,
                        'created_by': created_by,
                        'updated_by': updated_by,
                    }
                    return jsonify({'message': 'Feedback Details found successfully', 'status': 200, 'data': feedback_data})
        @self.feedback_ns.route('/activate/<string:id>')
        class FeedbackActivate(Resource):
            @self.feedback_ns.doc('feedback/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    feedback = Feedback.query.get(id)
                    if not feedback:
 
                        return jsonify({'message': 'Feedback not found', 'status': 404})
                    else:
                        feedback.is_active = True
                        db.session.commit()
   
                        return jsonify({'message': 'Feedback activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
      
                    return jsonify({'message': str(e), 'status': 500})

        @self.feedback_ns.route('/deactivate/<string:id>')
        class FeedbackDeactivate(Resource):
            @self.feedback_ns.doc('feedback/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    feedback = Feedback.query.get(id)
                    if not feedback:
    
                        return jsonify({'message': 'Feedback not found', 'status': 404})
                    else:
                        feedback.is_active = False
                        db.session.commit()
    
                        return jsonify({'message': 'Feedback deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
        
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.feedback_ns.route('/student_activate/<string:id>')
        class StudentFeedbackActivate(Resource):
            @self.feedback_ns.doc('student_feedback/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    student_feedback = StudentFeedback.query.get(id)
                    if not student_feedback:
         
                        return jsonify({'message': 'Student Feedback not found', 'status': 404})
                    else:
                        student_feedback.is_active = 1
                        db.session.commit()

                        return jsonify({'message': 'Student Feedback activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
       
                    return jsonify({'message': str(e), 'status': 500})

        @self.feedback_ns.route('/student_deactivate/<string:id>')
        class StudentFeedbackDeactivate(Resource):
            @self.feedback_ns.doc('student_feedback/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    student_feedback = StudentFeedback.query.get(id)
                    if not student_feedback:
         
                        return jsonify({'message': 'Student Feedback not found', 'status': 404})
                    else:
                        student_feedback.is_active = 0
                        db.session.commit()
          
                        return jsonify({'message': 'Student Feedback deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
       
                    return jsonify({'message': str(e), 'status': 500})


        self.api.add_namespace(self.feedback_ns)


