from datetime import datetime
import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations,logger
from flask_restx import Api, Namespace, Resource, fields
from app.models.adminuser import AdminDescription

class AdminProfileDescriptionController:
    def __init__(self,api):
        self.api = api
        self.admin_profile_description_model = api.model('AdminProfileDescription', {
            'admin_id': fields.String(required=True, description='Admin Id'),
            'description': fields.String(required=True, description='Admin Profile Description')
        })
        
        self.admin_profile_description_bp = Blueprint('admin_profile_description', __name__)
        self.admin_profile_description_ns = Namespace('admin_profile_description', description='Admin Profile Description Details', authorizations=authorizations)
        
       
        self.register_routes()

        
    def register_routes(self):
        @self.admin_profile_description_ns.route('/list')
        class AdminDescriptionList(Resource):
            @self.admin_profile_description_ns.doc('admin_profile_description/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    admin_profile_descriptiones = AdminDescription.query.filter_by(is_active=1).all()
                    admin_profile_descriptiones_data = []
                    
                    for admin_profile_description in admin_profile_descriptiones:
                        admin_profile_description_data = {
                            'id': admin_profile_description.id,
                            'admin_id': admin_profile_description.admin_id,
                            'description': admin_profile_description.description,   
                            'is_active': admin_profile_description.is_active    
                        }
                        admin_profile_descriptiones_data.append(admin_profile_description_data)
                    
                    if not admin_profile_descriptiones_data:
                        logger.info('No Admin Profile Description found')
                        return jsonify({'message': 'No Admin Profile Description found', 'status': 404})
                    else:
                        logger.info('Admin Profile Descriptions found Successfully')
                        return jsonify({'message': 'Admin Profile Descriptions found Successfully', 'status': 200, 'data': admin_profile_descriptiones_data})
                except Exception as e:
                   
                    logger.error(f"Error fetching Admin profile information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.admin_profile_description_ns.route('/alldata')
        class AdminDescriptionList(Resource):
            @self.admin_profile_description_ns.doc('admin_profile_description/alldata', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    admin_profile_descriptiones = AdminDescription.query.all()
                    admin_profile_descriptiones_data = []
                    
                    for admin_profile_description in admin_profile_descriptiones:
                        admin_profile_description_data = {
                            'id': admin_profile_description.id,
                            'admin_id': admin_profile_description.admin_id,
                            'description': admin_profile_description.description,   
                            'is_active': admin_profile_description.is_active    
                        }
                        admin_profile_descriptiones_data.append(admin_profile_description_data)
                    
                    if not admin_profile_descriptiones_data:
                        logger.info('No Admin Profile Description found')
                        return jsonify({'message': 'No Admin Profile Description found', 'status': 404})
                    else:
                        logger.info('Admin Profile Descriptions found Successfully')
                        return jsonify({'message': 'Admin Profile Descriptions found Successfully', 'status': 200, 'data': admin_profile_descriptiones_data})
                except Exception as e:
                    
                    logger.error(f"Error fetching Admin profession information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        @self.admin_profile_description_ns.route('/add')
        class AdminProfileDescriptionAdd(Resource):
            @self.admin_profile_description_ns.doc('admin_profile_description/add', security='jwt')
            @self.api.expect(self.admin_profile_description_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    admin_id = data.get('admin_id')
                    description = data.get('description')
                    current_user_id = get_jwt_identity()
                    if not admin_id :
                        logger.warning('Admin id not found')
                        return jsonify({'message': 'Please Provide Admin Id', 'status': 201})
                    if not description :
                        logger.warning('description not found')
                        return jsonify({'message': 'Please Provide Description', 'status': 201})
                    else:
                        admin_profile_description = AdminDescription(admin_id=admin_id,description=description,is_active=1,created_by=current_user_id)
                        db.session.add(admin_profile_description)
                        db.session.commit()
                        logger.info('Admin Profile Description created successfully')
                        return jsonify({'message': 'Admin Profile Description created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error adding Admin profession information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.admin_profile_description_ns.route('/edit/<int:id>')
        class AdminProfileDescriptionEdit(Resource):
            @self.admin_profile_description_ns.doc('admin_profile_description/edit', security='jwt')
            @api.expect(self.admin_profile_description_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    admin_id = data.get('admin_id')
                    description = data.get('description')
                    current_user_id = get_jwt_identity()
                    if not admin_id :
                        logger.warning('Admin id not found')
                        return jsonify({'message': 'Please Provide Admin Id', 'status': 201})
                    if not description :
                        logger.warning('description not found')
                        return jsonify({'message': 'Please Provide Description', 'status': 201})
                    else:
                       
                        admin_profile_description = AdminDescription.query.filter_by(admin_id=id).first()
                        if not admin_profile_description:
                            logger.warning('Admin Profile Description not found')
                            return jsonify({'message': 'Admin Profile Description not found', 'status': 404})
                        else:
                            admin_profile_description.admin_id = admin_id
                            admin_profile_description.description = description
                            admin_profile_description.updated_by = current_user_id
                            db.session.commit()
                            logger.info('Admin Profile Description updated successfully')
                            return jsonify({'message': 'Admin Profile Description updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error editing Admin profession information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                        
            @self.admin_profile_description_ns.doc('admin_profile_description/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
              
                    admin_profile_description = AdminDescription.query.filter_by(admin_id=id).first()
                    if not admin_profile_description:
                        logger.warning('No Admin Profile Description found')
                        return jsonify({'message': 'Admin Profile Description not found', 'status': 404})
                    else:
                        admin_profile_description_data = {
                            'id': admin_profile_description.id,
                            'admin_id': admin_profile_description.admin_id,
                            'description': admin_profile_description.description,
                            'is_active': admin_profile_description.is_active,

                        }
                        logger.info('Admin Profession deactivated Successfully')
                        print(admin_profile_description_data)
                        return jsonify({'message': 'Admin Profile Description found Successfully', 'status': 200,'data':admin_profile_description_data})
                except Exception as e:
                   
                    logger.error(f"Error fetching Admin profession information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.admin_profile_description_ns.route('/activate/<int:id>')
        class ActivateAdminProfileDescription(Resource):
            @self.admin_profile_description_ns.doc('admin_profile_description/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    admin_profile_description = AdminDescription.query.get(id)
                    if not admin_profile_description:
                        logger.warning('No Admin Profile Description found')
                        return jsonify({'message': 'Admin Profile Description not found', 'status': 404})
                    
                    admin_profile_description.is_active = 1
                    db.session.commit()
                    logger.info('Admin Profile Description activated successfully')
                    return jsonify({'message': 'Admin Profile Description activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error activating Admin profession information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.admin_profile_description_ns.route('/deactivate/<int:id>')
        class DeactivateAdminProfileDescription(Resource):
            @self.admin_profile_description_ns.doc('admin_profile_description/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    admin_profile_description = AdminDescription.query.get(id)
                    if not admin_profile_description:
                        logger.warning('No Admin Profile Description found')
                        return jsonify({'message': 'Admin Profile Description not found', 'status': 404})
                    
                    admin_profile_description.is_active = 0
                    db.session.commit()
                    logger.info('Admin Profile Description deactivated successfully')
                    return jsonify({'message': 'Admin Profile Description deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error deactivating Admin profession information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        
        self.api.add_namespace(self.admin_profile_description_ns)