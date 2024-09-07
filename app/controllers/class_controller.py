import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db,app,api,authorizations,logger
from flask_restx import  Api, Namespace, Resource, fields
from app.models.adminuser import AdminBasicInformation
from app.models.student import ClassMaster
from sqlalchemy import desc
class ClassController:
    def __init__(self, api):
        self.api = api
        self.class_model = self.api.model('ClassMaster', {
            'class_name': fields.String(required=True, description='Class Name'),
        })

        self.class_ns = Namespace('class', description='class Data', authorizations=authorizations)
        self.class_bp = Blueprint('class', __name__)

        self.register_routes()

    def register_routes(self):
        @self.class_ns.route('/list')
        class ClassList(Resource):
            @self.class_ns.doc('class/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    classes = ClassMaster.query.filter_by(is_deleted=False).order_by(desc(ClassMaster.updated_at)).all()
                    classes_data = []

                    for classs in classes:
                        created_by = 'Admin'
                        updated_by = 'Admin'
                    
                        if classs.created_by is not None:
                            createadmindata = AdminBasicInformation.query.filter_by(admin_login_id=classs.created_by).first()
                            if createadmindata:
                                created_by = createadmindata.first_name
                        if classs.updated_by is not None:
                            updateadmindata = AdminBasicInformation.query.filter_by(admin_login_id=classs.updated_by).first()
                            if updateadmindata:
                                updated_by = updateadmindata.first_name

                        class_data = {
                            'id': classs.class_id,
                            'class_name': classs.class_name,
                            'is_active': classs.is_active,
                            'is_deleted': classs.is_deleted,
                            'created_at': classs.created_at,
                            'updated_at': classs.updated_at,
                            'created_by': created_by,
                            'updated_by': updated_by,
                        }
                        classes_data.append(class_data)

                    if not classes_data:
                        logger.warning("Classes not found ")
                        return jsonify({'message': 'No class found', 'status': 404})
                    logger.info("Classes Found Successfully")
                    return jsonify({'message': 'Class Found Successfully', 'status': 200, 'data': classes_data})
                except Exception as e:
                    
                    logger.error(f"Error fetching class: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.class_ns.route('/add')
        class ClassAdd(Resource):
            @self.class_ns.doc('class/add', security='jwt')
            @self.api.expect(self.class_model)
            @jwt_required()
            def post(self):
                try:
                   
                        data = request.json
                        class_name = data.get('class_name')
                        current_user_id = get_jwt_identity()

                        if not class_name:
                            logger.warning("No class name provided")
                            return jsonify({'message': 'Please Provide Class Name', 'status': 400})

                        
                        existing_class = ClassMaster.query.filter_by(class_name=class_name).first()
                        if existing_class:
                            if existing_class.is_deleted:
                        
                                existing_class.is_deleted = False
                                existing_class.is_active = True
                                existing_class.updated_by = current_user_id
                                db.session.commit()
                                logger.info("Class created successfully")
                                return jsonify({'message': 'Class Created Successfully', 'status': 200})
                            else:
                                
                                logger.warning("Class already exists and is not deleted")
                                return jsonify({'message': 'Class Already Exists', 'status': 409})

                      
                        new_class = ClassMaster(class_name=class_name, is_active=True, created_by=current_user_id)
                        db.session.add(new_class)
                        db.session.commit()
                        logger.info("Class created successfully")
                        return jsonify({'message': 'Class Created Successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error adding class: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.class_ns.route('/edit/<int:id>')
        class ClassEdit(Resource):
            @self.class_ns.doc('class/edit', security='jwt')
            @self.class_ns.expect(self.class_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    class_name = data.get('class_name')
                    current_user_id = get_jwt_identity()

                    if not class_name:
                        logger.warning("No classes found")
                        return jsonify({'message': 'Please Provide Class Name', 'status': 400})

                    classes = ClassMaster.query.get(id)
                    if not classes:
                        logger.warning("No classes found")
                        return jsonify({'message': 'Class Not Found', 'status': 404})

                    existing_class = ClassMaster.query.filter_by(class_name=class_name).first()
                    if existing_class:
                        logger.warning(" classe already exists")
                        return jsonify({'message': 'Class Already Exists', 'status': 409})

                    classes.class_name = class_name
                    classes.updated_by = current_user_id
                    db.session.commit()
                    logger.info("class updated successfully")
                    return jsonify({'message': 'Class Updated Successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error editing class: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.class_ns.route('/get/<int:id>')
        class ClassGet(Resource):
            @self.class_ns.doc('class/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    classes = ClassMaster.query.get(id)
                    if not classes:
                        logger.warning("Class Name Not Provided")
                        return jsonify({'message': 'Class Not Found', 'status': 404})

                    class_data = {
                        'id': classes.class_id,
                        'class_name': classes.class_name,
                        'is_active': classes.is_active,
                        'is_deleted': classes.is_deleted,
                        'created_at': classes.created_at,
                        'updated_at': classes.updated_at,
                    }
                    logger.info("class found successfully")
                    return jsonify({'message': 'Class Found Successfully', 'status': 200, 'data': class_data})
                except Exception as e:
                    
                    logger.error(f"Error fetching class: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.class_ns.route('/delete/<int:id>')
        class ClassDelete(Resource):
            @self.class_ns.doc('class/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                try:
                    classes = ClassMaster.query.get(id)
                    if not classes:
                        logger.warning(f"Class not found: class_id {id}")
                        return jsonify({'message': 'Class Not Found', 'status': 404})

                    classes.is_deleted = True
                    db.session.commit()
                    logger.info(f"Class deleted successfully: class_id {id}")
                    return jsonify({'message': 'Class Deleted Successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error deleting class: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        @self.class_ns.route('/activate/<int:id>')
        class CourseActivate(Resource):
            @self.class_ns.doc('class/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    classes = ClassMaster.query.get(id)
                    if not classes:
                        logger.warning(f"Class with ID {id} not found")
                        return jsonify({'message': 'Class Not Found', 'status': 404})
                    else:
                        classes.is_active = 1
                        classes.updated_by = get_jwt_identity()
                        db.session.commit()
                        logger.info(f"Class Activated Successfully")
                        return jsonify({'message': 'Class Activated Successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error activating Class: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.class_ns.route('/deactivate/<int:id>')
        class CourseDeactivate(Resource):
            @self.class_ns.doc('class/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    classes = ClassMaster.query.get(id)
                    if not classes:
                        logger.warning(f"Class with ID {id} not found")
                        return jsonify({'message': 'Class not found', 'status': 404})
                    else:
                        classes.is_active = 0
                        classes.updated_by = get_jwt_identity()
                        db.session.commit()
                        logger.info(f"Class activated successfully")
                        return jsonify({'message': 'Class Deactivated Successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error deactivating Class: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        
        self.api.add_namespace(self.class_ns)

