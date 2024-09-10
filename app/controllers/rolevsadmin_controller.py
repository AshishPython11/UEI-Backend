import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.adminuser import AdminBasicInformation
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.role import RoleMasterData, RoleVsAdminMaster,ManageRole
from sqlalchemy import desc
class RolevsAdminController:
    def __init__(self,api):
        self.api = api
        self.rolevsadmin_model = api.model('RolevsAdmin Data ', {
            'admin_id': fields.String(required=True, description='Admin Id'),
            'role_master_id': fields.String(required=True, description='RolevsAdmin Master Id')
        })
        
        self.rolevsadmin_bp = Blueprint('rolevsadmin', __name__)
        self.rolevsadmin_ns = Namespace('rolevsadmin', description='RolevsAdmin Data  Details', authorizations=authorizations)
        
        # self.api = Api(self.rolevsadmin_bp)
        # self.api.add_namespace(self.rolevsadmin_ns)
        # self.api.init_app(self.rolevsadmin_bp)
        self.register_routes()

        
    def register_routes(self):
        @self.rolevsadmin_ns.route('/list')
        class RolevsAdminList(Resource):
            @self.rolevsadmin_ns.doc('rolevsadmin/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
               
                    rolevsadmines = RoleVsAdminMaster.query.filter_by(is_deleted=False).order_by(desc(RoleVsAdminMaster.updated_at)).all()
                    rolevsadmines_data = []
                    
                    for rolevsadmin in rolevsadmines:
                        created_by = 'Admin'
                        updated_by = 'Admin'
                        if rolevsadmin.created_by is not None:
                            createadmindata = AdminBasicInformation.query.filter_by(admin_login_id = rolevsadmin.created_by).first()
                            if createadmindata is not None:
                                created_by = createadmindata.first_name
                            else :
                                created_by = 'Admin'
                        if rolevsadmin.updated_by is not None:   
                            updateadmindata = AdminBasicInformation.query.filter_by(admin_login_id = rolevsadmin.updated_by).first()
                            if updateadmindata is not None:
                                updated_by = updateadmindata.first_name
                            else :
                                updated_by = 'Admin'
                        role = RoleMasterData.query.get(rolevsadmin.role_master_id)
                        admin = AdminBasicInformation.query.get(rolevsadmin.admin_id)
                        rolevsadmin_data = {
                        'id': rolevsadmin.role_admin_master_id,
                        'admin_id': rolevsadmin.admin_id,
                        'admin_name': admin.first_name,
                        'role_master_id': rolevsadmin.role_master_id,
                        'role_name': role.role_name,
                        'is_active': rolevsadmin.is_active,
                        'is_deleted': rolevsadmin.is_deleted, 
                        'created_at':rolevsadmin.created_at,
                        'updated_at':rolevsadmin.updated_at,
                        'created_by':created_by,
                        'updated_by':updated_by,
                        }
                        rolevsadmines_data.append(rolevsadmin_data)
                    
                    if not rolevsadmines_data:
       
                        return jsonify({'message': 'No RolevsUser found', 'status': 404})
                    else:
              
                        return jsonify({'message': 'RolevsUser found Successfully', 'status': 200, 'data': rolevsadmines_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
        @self.rolevsadmin_ns.route('/add')
        class RolevsAdminAdd(Resource):
            @self.rolevsadmin_ns.doc('rolevsadmin/add', security='jwt')
            @self.api.expect(self.rolevsadmin_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    admin_id = str(data.get('admin_id'))
                    role_master_id = str(data.get('role_master_id'))
                    current_user_id = get_jwt_identity()
                    if not admin_id :
             
                        return jsonify({'message': 'Please Provide Admin Id', 'status': 201})
                    if not role_master_id :
              
                        return jsonify({'message': 'Please Role Master Id', 'status': 201})
                    else:
                        try:
                            form = RoleVsAdminMaster(admin_id=admin_id,role_master_id=role_master_id,is_active=1,created_by=current_user_id)
                         
                            db.session.add(form)
                          
                            manage_roles = ManageRole.query.filter_by(role_master_id=role_master_id).all()
                            for manage_role in manage_roles:
                                if manage_role:
                                    manage_role.admin_id=admin_id,
                                    manage_role.is_active = 1
                                    manage_role.is_delete = False
                                else:
                                
                                    manage_role = ManageRole(
                                        admin_id=admin_id,
                                        role_master_id=role_master_id,
                                        is_active=1,
                                        is_delete=False
                                    )
                                db.session.commit()
                   
                            return jsonify({'message': 'RolevsUser Data  created successfully', 'status': 200})
                        except Exception as e:
              
                            print(f"Error occurred: {str(e)}")
                            return jsonify({'message': e.message, 'status': 500})
                except Exception as e:
                    db.session.rollback()

                    return jsonify({'message': str(e), 'status': 500})
                
        @self.rolevsadmin_ns.route('/edit/<int:id>')
        class RolevsAdminEdit(Resource):
            @self.rolevsadmin_ns.doc('rolevsadmin/edit', security='jwt')
            @api.expect(self.rolevsadmin_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    admin_id = str(data.get('admin_id'))
                    role_master_id = str(data.get('role_master_id'))
                    current_user_id = get_jwt_identity()
                    if not admin_id :
              
                        return jsonify({'message': 'Please Provide Admin Id', 'status': 201})
                    if not role_master_id :
            
                        return jsonify({'message': 'Please Role Master Id', 'status': 201})
                    else:
                        form = RoleVsAdminMaster.query.get(id)
                        if not form:
                       
                            return jsonify({'message': 'RolevsUser Data  not found', 'status': 404})
                        else:
                            form.admin_id = admin_id
                            form.role_master_id = role_master_id
                            form.updated_by = current_user_id
                            db.session.commit()
                            
                        
                            manage_role = ManageRole.query.filter_by(role_master_id=role_master_id).first()
                            if manage_role:
                                manage_role.admin_id = admin_id
                                manage_role.is_active = 1
                                manage_role.is_delete = False
            
                            return jsonify({'message': 'RolevsUser Data  updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
              
                    return jsonify({'message': str(e), 'status': 500})

                    
            @self.rolevsadmin_ns.doc('rolevsadmin/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    form = RoleVsAdminMaster.query.get(id)
                    if not form:
                 
                        return jsonify({'message': 'RolevsUser Data  not found', 'status': 404})
                    else:
                        form_data = {
                            'id': form.role_admin_master_id,
                            'admin_id': form.admin_id,
                            'role_master_id': form.role_master_id,
                            'is_active': form.is_active,
                            'is_deleted': form.is_deleted, 
                            'created_at':form.created_at,
                            'updated_at':form.updated_at,
                        }
                        print(form_data)
   
                        return jsonify({'message': 'RolevsUser Data found Successfully', 'status': 200,'data':form_data})
                except Exception as e:
 
                    return jsonify({'message': str(e), 'status': 500})
                
            
        @self.rolevsadmin_ns.route('delete/<int:id>')
        class RolevsAdminDelete(Resource):
            @self.rolevsadmin_ns.doc('rolevsadmin/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        formvsadmin_entity = RoleVsAdminMaster.query.get(id)
                        if not formvsadmin_entity:
                       
                            return jsonify({'message': 'RolevsUser not found', 'status': 404})
                        else:
                       
                            formvsadmin_entity.is_deleted=True
                            db.session.commit()
                   
                            return jsonify({'message': 'RolevsUser deleted successfully', 'status': 200})
                    except Exception as e:

                        return jsonify({'message': str(e), 'status': 500})
        @self.rolevsadmin_ns.route('/activate/<int:id>')
        class RolevsAdminActivate(Resource):
            @self.rolevsadmin_ns.doc('rolevsadmin/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    rolevsadmin = RoleVsAdminMaster.query.get(id)
                    if not rolevsadmin:
  
                        return jsonify({'message': 'RolevsUser Data not found', 'status': 404})

                    rolevsadmin.is_active = 1
                    db.session.commit()
           
                    return jsonify({'message': 'RolevsUser Data activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
    
                    return jsonify({'message': str(e), 'status': 500})

        @self.rolevsadmin_ns.route('/deactivate/<int:id>')
        class RolevsAdminDeactivate(Resource):
            @self.rolevsadmin_ns.doc('rolevsadmin/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    rolevsadmin = RoleVsAdminMaster.query.get(id)
                    if not rolevsadmin:
     
                        return jsonify({'message': 'RolevsUser Data not found', 'status': 404})

                    rolevsadmin.is_active = 0
                    db.session.commit()

                    return jsonify({'message': 'RolevsUser Data deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()

                    return jsonify({'message': str(e), 'status': 500})

        
        self.api.add_namespace(self.rolevsadmin_ns)