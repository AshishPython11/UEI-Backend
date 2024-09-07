import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.adminuser import AdminBasicInformation
from app import db, api, authorizations,logger
from flask_restx import Api, Namespace, Resource, fields
from app.models.role import RoleMasterData,ManageRole
from sqlalchemy import desc
from sqlalchemy import text
class RoleController:
    def __init__(self,api):
        self.api = api
        self.role_model = api.model('Role', {
            'role_name': fields.String(required=True, description='Role Name')
        })
        
        self.role_bp = Blueprint('role', __name__)
        self.role_ns = Namespace('role', description='Role Details', authorizations=authorizations)
   
        self.register_routes()

        
    def register_routes(self):
        @self.role_ns.route('/list')
        class RoleList(Resource):
            @self.role_ns.doc('role/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
              
                    rolees = RoleMasterData.query.filter_by(is_deleted=False).order_by(desc(RoleMasterData.updated_at)).all()
                    rolees_data = []
                    
                    for role in rolees:
                        created_by = 'Admin'
                        updated_by = 'Admin'
                        if role.created_by is not None:
                            createadmindata = AdminBasicInformation.query.filter_by(admin_login_id = role.created_by).first()
                            if createadmindata is not None:
                                created_by = createadmindata.first_name
                            else :
                                created_by = 'Admin'
                        if role.updated_by is not None:   
                            updateadmindata = AdminBasicInformation.query.filter_by(admin_login_id = role.updated_by).first()
                            if updateadmindata is not None:
                                updated_by = updateadmindata.first_name
                            else :
                                updated_by = 'Admin'
                        role_data = {
                            'id': role.role_master_id,
                            'role_name': role.role_name,
                            'is_active': role.is_active,
                            'created_at':role.created_at,
                            'is_deleted': role.is_deleted, 
                            'updated_at':role.updated_at,
                            'created_by':created_by,
                            'updated_by':updated_by,
                        }
                        rolees_data.append(role_data)
                    
                    if not rolees_data:
                        logger.warning("No Role found")
                        return jsonify({'message': 'No Role found', 'status': 404})
                    else:
                        logger.info("Roles found Successfully")
                        return jsonify({'message': 'Roles found Successfully', 'status': 200, 'data': rolees_data})
                except Exception as e:
                    
                    logger.error(f"Error fetching role information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        @self.role_ns.route('/add')
        class RoleAdd(Resource):
            @self.role_ns.doc('role/add', security='jwt')
            @self.api.expect(self.role_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    role_name = data.get('role_name')
                    current_user_id = get_jwt_identity()
                    if not role_name :
                        logger.warning("No Role name found")
                        return jsonify({'message': 'Please Provide Role name', 'status': 201})
                    
                    existing_role = RoleMasterData.query.filter_by(role_name=role_name).first()
                    if existing_role:
                        logger.warning("Role with the same name already exists")
                        return jsonify({'message': 'Role with the same name already exists', 'status': 400})
                    else:
                        role = RoleMasterData(role_name=role_name,is_active=1,created_by=current_user_id)
                        db.session.add(role)
                        db.session.commit()
                        logger.info("Roles created Successfully")
                        return jsonify({'message': 'Role created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error adding role information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.role_ns.route('/edit/<int:id>')
        class RoleEdit(Resource):
            @self.role_ns.doc('role/edit', security='jwt')
            @api.expect(self.role_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    role_name = data.get('role_name')
                    current_user_id = get_jwt_identity()
                    if not role_name :
                        logger.warning("No Role name found") 
                        return jsonify({'message': 'Please Provide Role name', 'status': 201})
                    existing_role = RoleMasterData.query.filter_by(role_name=role_name).first()
                    if existing_role and existing_role.role_master_id != id:
                        return jsonify({'message': 'Role with the same name already exists', 'status': 400})
                    else:
                        role = RoleMasterData.query.get(id)
                        if not role:
                            logger.warning("No Role found") 

                            return jsonify({'message': 'Role not found', 'status': 404})
                        else:
                            role.role_name = role_name
                            role.updated_by = current_user_id

                            db.session.commit()
                            logger.info("Roles updated Successfully")
                            return jsonify({'message': 'Role updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error editing role information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                    
            @self.role_ns.doc('role/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    role = RoleMasterData.query.get(id)
                    if not role:
                        logger.warning("No Role found") 

                        return jsonify({'message': 'Role not found', 'status': 404})
                    else:
                        role_data = {
                            'id': role.role_master_id,
                            'role_name': role.role_name,
                            'is_active': role.is_active,
                            'is_deleted': role.is_deleted, 
                            'created_at':role.created_at,
                            'updated_at':role.updated_at,
                        }
                        print(role_data)
                        logger.info("Roles found Successfully")
                        return jsonify({'message': 'Role found Successfully', 'status': 200,'data':role_data})
                except Exception as e:
                  
                    logger.error(f"Error fetching role information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        @self.role_ns.route('delete/<int:id>')
        class RoleDelete(Resource):
            @self.role_ns.doc('role/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        role_entity = RoleMasterData.query.get(id)
                        if not role_entity:
                            logger.warning("No Role found") 

                            return jsonify({'message': 'role not found', 'status': 404})
                        else:
                            #
                            manage_roles = ManageRole.query.filter_by(role_master_id=str(id)).all()
                            
         
                            
                            for manage_role in manage_roles:
                                
                                manage_role.is_delete=True
                                
                                db.session.commit()
                           
                            role_entity.is_deleted=True
                            db.session.commit()
                            logger.info("Roles deleted Successfully")
                            return jsonify({'message': 'Role deleted successfully', 'status': 200})
                    except Exception as e:
                        logger.error(f"Error DELETING role information: {str(e)}")
                        return jsonify({'message': str(e), 'status': 500})
                        
        @self.role_ns.route('/activate/<int:id>')
        class RoleActivate(Resource):
            @self.role_ns.doc('role/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    role = RoleMasterData.query.get(id)
                    if not role:
                        logger.warning("No Role found") 

                        return jsonify({'message': 'Role not found', 'status': 404})

                    role.is_active = 1
                    db.session.commit()
                    logger.info("Roles activated Successfully")
                    return jsonify({'message': 'Role activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error activating role information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.role_ns.route('/deactivate/<int:id>')
        class RoleDeactivate(Resource):
            @self.role_ns.doc('role/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    role = RoleMasterData.query.get(id)
                    if not role:
                        logger.warning("No Role found") 

                        return jsonify({'message': 'Role not found', 'status': 404})

                    role.is_active = 0
                    db.session.commit()
                    logger.info("Roles deactivated Successfully")
                    return jsonify({'message': 'Role deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error deactivating role information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})


        
        self.api.add_namespace(self.role_ns)