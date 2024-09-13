import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.adminuser import AdminBasicInformation
from app import db, api, authorizations,logger
from flask_restx import Api, Namespace, Resource, fields
from app.models.role import FormMasterData, RoleMasterData, RoleVsFormMasterData,ManageRole
from sqlalchemy import desc
class RolevsFormController:
    def __init__(self,api):
        self.api = api
        self.rolevsform_model = api.model('RolevsForm', {
            'role_master_id': fields.String(required=True, description='Role Id'),
            'form_master_id': fields.String(required=True, description='Form Data  Id'),
            'is_search': fields.Boolean(required=True, description='Search'),
            'is_save': fields.Boolean(required=True, description='Save'),
            'is_update': fields.Boolean(required=True, description='Update')
        })
        
        self.rolevsform_bp = Blueprint('rolevsform', __name__)
        self.rolevsform_ns = Namespace('rolevsform', description='RolevsForm Data  Details', authorizations=authorizations)
    
        self.register_routes()

        
    def register_routes(self):
        @self.rolevsform_ns.route('/list')
        class RoleVsFormList(Resource):
            @self.rolevsform_ns.doc('rolevsform/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
           
                    rolevsformes = RoleVsFormMasterData.query.filter_by(is_deleted=False).order_by(desc(RoleVsFormMasterData.updated_at)).all()
                    rolevsformes_data = []
                    
                    for rolevsform in rolevsformes:
                        created_by = 'Admin'
                        updated_by = 'Admin'
                        if rolevsform.created_by is not None:
                            createadmindata = AdminBasicInformation.query.filter_by(admin_login_id = rolevsform.created_by).first()
                            if createadmindata is not None:
                                created_by = createadmindata.first_name
                            else :
                                created_by = 'Admin'
                        if rolevsform.updated_by is not None:   
                            updateadmindata = AdminBasicInformation.query.filter_by(admin_login_id = rolevsform.updated_by).first()
                            if updateadmindata is not None:
                                updated_by = updateadmindata.first_name
                            else :
                                updated_by = 'Admin'
                        role = RoleMasterData.query.get(rolevsform.role_master_id)
                        form = FormMasterData.query.get(rolevsform.form_master_id)
                        rolevsform_data = {
                        'id': rolevsform.role_form_master_id,
                        'form_master_id': rolevsform.form_master_id,
                        'form_name': form.form_name,
                        'role_master_id': rolevsform.role_master_id,
                        'role_name': role.role_name,
                        'is_search': rolevsform.is_search,
                        'is_save': rolevsform.is_save,
                        'is_update': rolevsform.is_update,
                        'is_active': rolevsform.is_active,
                        'is_deleted': rolevsform.is_deleted, 
                        'created_at':rolevsform.created_at,
                        'updated_at':rolevsform.updated_at,
                        'created_by':created_by,
                        'updated_by':updated_by,
                        }
                        rolevsformes_data.append(rolevsform_data)
                    
                    if not rolevsformes_data:
                        logger.warning("No RoleVsForm found")
                        return jsonify({'message': 'No RoleVsForm found', 'status': 404})
                    else:
                        logger.info("Rolevsform found Successfully")
                        return jsonify({'message': 'RoleVsForms found Successfully', 'status': 200, 'data': rolevsformes_data})
                except Exception as e:
                 
                    logger.error(f"Error fetching rolevsform information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        @self.rolevsform_ns.route('/add')
        class RolevsFormAdd(Resource):
            @self.rolevsform_ns.doc('rolevsform/add', security='jwt')
            @self.api.expect(self.rolevsform_model, validate=True)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    role_master_id = data.get('role_master_id')
                    form_master_id = data.get('form_master_id')
                    is_search = data.get('is_search')
                    is_save = data.get('is_save')
                    is_update = data.get('is_update')
                    current_user_id = get_jwt_identity()

                    if not form_master_id:
                        logger.warning("No form_master_id found")
                        return jsonify({'message': 'Please Provide Form ID', 'status': 400})
                    if not role_master_id:
                        logger.warning("No role_master_id found")
                        return jsonify({'message': 'Please Provide Role ID', 'status': 400})


                 
                    new_association = RoleVsFormMasterData(
                        role_master_id=role_master_id,
                        form_master_id=form_master_id,
                        is_search=is_search,
                        is_save=is_save,
                        is_update=is_update, 
                        created_by=current_user_id
                    )
                    db.session.add(new_association)
                    db.session.commit()

                    logger.info("Role vs Form association created successfully")
                    return jsonify({'message': 'Role vs Form association created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error adding rolevsform information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
      
                
        @self.rolevsform_ns.route('/edit/<int:id>')
        class RolevsFormEdit(Resource):
            @self.rolevsform_ns.doc('rolevsform/edit', security='jwt')
            @api.expect(self.rolevsform_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    role_master_id = data.get('role_master_id')
                    form_master_id = data.get('form_master_id')
                    is_search = data.get('is_search')
                    is_save = data.get('is_save')
                    is_update = data.get('is_update')
                    current_user_id = get_jwt_identity()
                    if not form_master_id :
                        logger.warning("No form_master_id found")
                        return jsonify({'message': 'Please Provide From Id', 'status': 201})
                    if not role_master_id :
                        logger.warning("No role_master_id found")
                        return jsonify({'message': 'Please Provide Role Id', 'status': 201})
                 
                    else:
                        form = RoleVsFormMasterData.query.get(id)
                        if not form:
                            logger.warning("No RoleVsForm found")
                            return jsonify({'message': 'RolevsForm Data  not found', 'status': 404})
                        else:
                            form.form_master_id = form_master_id
                            form.role_master_id = role_master_id
                            form.is_search = is_search
                            form.is_save = is_save
                            form.is_update = is_update
                            form.updated_by=current_user_id
                            db.session.commit()
                            
                        
                            manage_role = ManageRole.query.filter_by(role_master_id=role_master_id, form_master_id=form_master_id).first()
                            if manage_role:
                                    manage_role.is_search = is_search
                                    manage_role.is_save = is_save
                                    manage_role.is_update = is_update
                            logger.info("Rolevsform updated Successfully")
                            return jsonify({'message': 'RolevsForm Data  updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error editing rolevsform information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                            
            @self.rolevsform_ns.doc('rolevsform/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    form = RoleVsFormMasterData.query.get(id)
                    if not form:
                        logger.warning("No RoleVsForm found")
                        return jsonify({'message': 'RolevsForm Data  not found', 'status': 404})
                    else:
                        form_data = {
                            'id': form.role_form_master_id,
                            'form_master_id': form.form_master_id,
                            'role_master_id': form.role_master_id,
                            'is_search': form.is_search,
                            'is_save': form.is_save,
                            'is_update': form.is_update,
                            'is_active': form.is_active,
                            'is_deleted': form.is_deleted, 
                            'created_at':form.created_at,
                            'updated_at':form.updated_at,
                            
                        }
                        print(form_data)
                        logger.info("Rolevsform found Successfully")
                        return jsonify({'message': 'RolevsForm Data found Successfully', 'status': 200,'data':form_data})
                except Exception as e:
                    
                    logger.error(f"Error fetching rolevsform information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        @self.rolevsform_ns.route('delete/<int:id>')
        class RolevsFormDelete(Resource):
            @self.rolevsform_ns.doc('rolevsform/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        form_entity = RoleVsFormMasterData.query.get(id)
                        if not form_entity:
                            logger.warning("No RoleVsForm found")
                            return jsonify({'message': 'form not found', 'status': 404})
                        else:
                          
                            form_entity.is_deleted = True
                            db.session.commit()
                            logger.info("Rolevsform deleted Successfully")
                            return jsonify({'message': 'Rolevsform deleted successfully', 'status': 200})
                    except Exception as e:
                        
                        logger.error(f"Error deleting rolevsform information: {str(e)}")
                        return jsonify({'message': str(e), 'status': 500})
        @self.rolevsform_ns.route('/activate/<int:id>')
        class RolevsformActivate(Resource):
            @self.rolevsform_ns.doc('student_academic_history/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    student_academic_history = RoleVsFormMasterData.query.get(id)
                    if not student_academic_history:
                        logger.warning("No RoleVsForm found")
                        return jsonify({'message': 'Rolevsform not found', 'status': 404})
                    else:
                        student_academic_history.is_active = 1
                        db.session.commit()
                        logger.info("Rolevsform activated Successfully")
                        return jsonify({'message': 'Rolevsform activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error activating rolevsform information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.rolevsform_ns.route('/deactivate/<int:id>')
        class RolevsformDeactivate(Resource):
            @self.rolevsform_ns.doc('student_academic_history/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    student_academic_history = RoleVsFormMasterData.query.get(id)
                    if not student_academic_history:
                        logger.warning("No RoleVsForm found")
                        return jsonify({'message': 'Rolevsform not found', 'status': 404})
                    else:
                        student_academic_history.is_active = 0
                        db.session.commit()
                        logger.info("Rolevsform deactivated Successfully")
                        return jsonify({'message': 'Rolevsform deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error deactivating rolevsform information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        
        self.api.add_namespace(self.rolevsform_ns)