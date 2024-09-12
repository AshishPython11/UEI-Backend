import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db,app,api,authorizations
from flask_restx import  Api, Namespace, Resource, fields
from app.models.adminuser import AdminBasicInformation, CourseMaster
from sqlalchemy import desc

class CourseController:
    def __init__(self,api):
        self.api = api
        self.course_model = self.api.model('Course', {
            'course_name': fields.String(required=True, description='Course Name'),
        })

        self.course_ns = Namespace('course', description='Course Data', authorizations=authorizations)
        self.course_bp = Blueprint('course', __name__)
        
        self.register_routes()
      
        
    def register_routes(self):
        @self.course_ns.route('/list')
        class CourseList(Resource):
            @self.course_ns.doc('course/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
              
                    coursees = CourseMaster.query.filter_by(is_deleted=False).order_by(desc(CourseMaster.updated_at)).all()
                    coursees_data = []
                    
                    for course in coursees:
                        created_by = 'Admin'
                        updated_by = 'Admin'
                        if course.created_by is not None:
                            createadmindata = AdminBasicInformation.query.filter_by(admin_login_id = course.created_by).first()
                            if createadmindata is not None:
                                created_by = createadmindata.first_name
                            else :
                                created_by = 'Admin'
                        if course.updated_by is not None:   
                            updateadmindata = AdminBasicInformation.query.filter_by(admin_login_id = course.updated_by).first()
                            if updateadmindata is not None:
                                updated_by = updateadmindata.first_name
                            else :
                                updated_by = 'Admin'
                        course_data = {
                            'id': course.course_id,
                            'course_name': course.course_name,
                            'is_active': course.is_active,
                            'is_deleted': course.is_deleted, 
                            'created_at':course.created_at,
                            'updated_at':course.updated_at,
                            'created_by':created_by,
                            'updated_by':updated_by,
                        }
                        coursees_data.append(course_data)
                    
                    if not coursees_data:
                   
                        return jsonify({'message': 'No Course found', 'status': 404})
                    else:
                        
                        return jsonify({'message': 'Courses found Successfully', 'status': 200, 'data': coursees_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
        
        
        @self.course_ns.route('/add')
        class CourseAdd(Resource):
            @self.course_ns.doc('course/add', security='jwt')
            @self.api.expect(self.course_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    course_name = data.get('course_name')
                    current_user_id = get_jwt_identity()
                    print(data)
                    if not course_name :
                      
                        return jsonify({'message': 'Please Provide Course name','status':201})
                    else:
                        existing_course = CourseMaster.query.filter_by(course_name=course_name).first()

                        if existing_course:
                   
                            return jsonify({'message': 'Course already exists', 'status': 409})
                        course =  CourseMaster(course_name=course_name,is_active=1,is_deleted=False,created_by=current_user_id)
                        db.session.add(course)
                        db.session.commit()
                       
                        return jsonify({'message': 'Course created successfully','status':200})
                except Exception as e:
                    db.session.rollback()
                  
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.course_ns.route('/edit/<int:id>')
        class CourseEdit(Resource):
            @self.course_ns.doc('course/edit', security='jwt')
            @self.course_ns.expect(self.course_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    course_name = data.get('course_name')
                    current_user_id = get_jwt_identity()
                    if not course_name:
                      
                        return jsonify({'message': 'Please provide course name', 'status': 400})
                    else:
                        course = CourseMaster.query.get(id)
                    if not course:
                       
                        return jsonify({'message': 'Course not found', 'status': 404})
                    else:
                        existing_course = CourseMaster.query.filter_by(course_name=course_name).first()

                        if existing_course:
                   
                            return jsonify({'message': 'Course already exists', 'status': 409})
                        course.course_name = course_name
                        course.updated_by = current_user_id
                        db.session.commit()
                      
                        return jsonify({'message': 'Course updated successfully', 'status':200})
                except Exception as e:
                    db.session.rollback()
                
                    return jsonify({'message': str(e), 'status': 500})
                        
            @self.course_ns.doc('course/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    course = CourseMaster.query.get(id)
                    if not course:
                        
                        return jsonify({'message': 'Course not found', 'status': 404})
                    else:
                        course_data = {
                            'id': course.course_id,
                            'course_name': course.course_name,
                            'is_active': course.is_active,
                            'is_deleted': course.is_deleted, 
                            'created_at':course.created_at,
                            'updated_at':course.updated_at,
                        }
        
                        return jsonify({'message': 'Course found Successfully', 'status': 200,'data':course_data})
                except Exception as e:
    
                    return jsonify({'message': str(e), 'status': 500})
        @self.course_ns.route('delete/<int:id>')
        class CourseDelete(Resource):
            @self.course_ns.doc('course/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        course_entity = CourseMaster.query.get(id)
                        if not course_entity:
                        
                            return jsonify({'message': 'course not found', 'status': 404})
                        else:
                            # course_entity.is_active = 0
                            course_entity.is_deleted=True
                            db.session.commit()
                         
                            return jsonify({'message': 'course deleted successfully', 'status': 200})
                    except Exception as e:

                        return jsonify({'message': str(e), 'status': 500})
                    
        @self.course_ns.route('/activate/<int:id>')
        class CourseActivate(Resource):
            @self.course_ns.doc('course/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    course = CourseMaster.query.get(id)
                    if not course:

                        return jsonify({'message': 'Course not found', 'status': 404})
                    else:
                        course.is_active = 1
                        course.updated_by = get_jwt_identity()
                        db.session.commit()
                
                        return jsonify({'message': 'Course activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
           
                    return jsonify({'message': str(e), 'status': 500})

        @self.course_ns.route('/deactivate/<int:id>')
        class CourseDeactivate(Resource):
            @self.course_ns.doc('course/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    course = CourseMaster.query.get(id)
                    if not course:
          
                        return jsonify({'message': 'Course not found', 'status': 404})
                    else:
                        course.is_active = 0
                        course.updated_by = get_jwt_identity()
                        db.session.commit()
         
                        return jsonify({'message': 'Course deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
    
                    return jsonify({'message': str(e), 'status': 500})
                
        self.api.add_namespace(self.course_ns)