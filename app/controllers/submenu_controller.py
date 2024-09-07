import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.adminuser import AdminBasicInformation
from app import db, api, authorizations,logger
from flask_restx import Api, Namespace, Resource, fields
from app.models.role import MenuMasterData, SubMenuMasterData
from sqlalchemy import desc
from sqlalchemy import literal
class SubMenuController:
    def __init__(self,api):
        self.api = api
        self.submenu_model = api.model('SubMenu', {
            'menu_name': fields.String(required=True, description='SubMenu Name'),
            'menu_master_id': fields.String(required=True, description='Menu Id'),
            'priority': fields.String(required=True, description='Priority'),
        })
        
        self.submenu_bp = Blueprint('submenu', __name__)
        self.submenu_ns = Namespace('submenu', description='SubMenu Details', authorizations=authorizations)
     
        self.register_routes()

        
    def register_routes(self):
        @self.submenu_ns.route('/list')
        class SubjectPreferenceList(Resource):
            @self.submenu_ns.doc('submenu/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
    
                    submenus = SubMenuMasterData.query.filter_by(is_deleted=False).order_by(desc(SubMenuMasterData.updated_at)).all()
                    submenus_data = []
                    
                    for submenu in submenus:
                        created_by = 'Admin'
                        updated_by = 'Admin'
                        if submenu.created_by is not None:
                            createadmindata = AdminBasicInformation.query.filter_by(admin_login_id = submenu.created_by).first()
                            if createadmindata is not None:
                                created_by = createadmindata.first_name
                            else :
                                created_by = 'Admin'
                        if submenu.updated_by is not None:   
                            updateadmindata = AdminBasicInformation.query.filter_by(admin_login_id = submenu.updated_by).first()
                            if updateadmindata is not None:
                                updated_by = updateadmindata.first_name
                            else :
                                updated_by = 'Admin'
                        menu = MenuMasterData.query.get(submenu.menu_master_id)
                        submenu_data = {
                            'id': submenu.submenu_master_id,
                            'menu_name': submenu.menu_name,
                            'priority': submenu.priority,
                            'menu_master_id':submenu.menu_master_id,
                            'menu_master_name':menu.menu_name,
                            'is_active':submenu.is_active,
                            'is_deleted': submenu.is_deleted, 
                            'created_at':submenu.created_at,
                            'updated_at':submenu.updated_at,
                            'created_by':created_by,
                            'updated_by':updated_by,
                        }
                        submenus_data.append(submenu_data)
                    
                    if not submenus_data:
                        logger.warning("No Submenu found")
                        return jsonify({'message': 'No Submenu found', 'status': 404})
                    else:
                        logger.info("Submenus found Successfully")
                        return jsonify({'message': 'Submenus found Successfully', 'status': 200, 'data': submenus_data})
                except Exception as e:
                    
                    logger.error(f"Error fetching submenu information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.submenu_ns.route('/add')
        class SubMenuAdd(Resource):
            @self.submenu_ns.doc('submenu/add', security='jwt')
            @self.api.expect(self.submenu_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    menu_name = data.get('menu_name')
                    menu_master_id = data.get('menu_master_id')
                    priority = data.get('priority')
                    current_user_id = get_jwt_identity()
                    if not menu_name :
                        logger.warning("No menu_name found")
                        return jsonify({'message': 'Please Provide SubMenu name', 'status': 201})
                    if not menu_master_id :
                        logger.warning("No menu_master_id found")
                        return jsonify({'message': 'Please Provide Menu Id', 'status': 201})
                    if not priority :
                        logger.warning("No priority found")
                        return jsonify({'message': 'Please Provide Priority', 'status': 201})
                    else:
                        submenu = SubMenuMasterData(menu_name=menu_name,priority=priority,menu_master_id=menu_master_id,is_active=1,created_by=current_user_id)
                        db.session.add(submenu)
                        db.session.commit()
                        logger.info("Submenus created Successfully")
                        return jsonify({'message': 'SubMenu created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error adding submenu information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.submenu_ns.route('/edit/<int:id>')
        class SubMenuEdit(Resource):
            @self.submenu_ns.doc('submenu/edit', security='jwt')
            @api.expect(self.submenu_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    menu_name = data.get('menu_name')
                    menu_master_id = data.get('menu_master_id')
                    priority = data.get('priority')
                    current_user_id = get_jwt_identity()
                    if not menu_name :
                        logger.warning("No menu_name found")
                        return jsonify({'message': 'Please Provide SubMenu name', 'status': 201})
                    if not priority :
                        logger.warning("No priority found")
                        return jsonify({'message': 'Please Provide Priority', 'status': 201})
                    else:
                        submenu = SubMenuMasterData.query.get(id)
                        if not submenu:
                            logger.warning("No Submenu found")
                            return jsonify({'message': 'SubMenu not found', 'status': 404})
                        else:
                            submenu.menu_name = menu_name
                            submenu.priority = priority
                            submenu.menu_master_id = menu_master_id
                            submenu.created_by = current_user_id
                            
                            db.session.commit()
                            logger.info("Submenus updated Successfully")
                            return jsonify({'message': 'SubMenu updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error editing submenu information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                    
            @self.submenu_ns.doc('submenu/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    submenu = SubMenuMasterData.query.get(id)
                    if not submenu:
                        logger.warning("No Submenu found")
                        return jsonify({'message': 'SubMenu not found', 'status': 404})
                    else:
                        submenu_data = {
                            'id': submenu.submenu_master_id,
                            'menu_name': submenu.menu_name,
                            'priority': submenu.priority,
                            'menu_master_id':submenu.menu_master_id,
                            'is_active':submenu.is_active,
                            'is_deleted': submenu.is_deleted, 
                            'created_at':submenu.created_at,
                            'updated_at':submenu.updated_at,
                        }
                        print(submenu_data)
                        logger.info("Submenus found Successfully")
                        return jsonify({'message': 'SubMenu found Successfully', 'status': 200,'data':submenu_data})
                except Exception as e:
                    
                    logger.error(f"Error fetching submenu information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        @self.submenu_ns.route('delete/<int:id>')
        class SubMenuDelete(Resource):
            @self.submenu_ns.doc('submenu/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        submenu_entity = SubMenuMasterData.query.get(id)
                        if not submenu_entity:
                            logger.warning("No Submenu found")
                            return jsonify({'message': 'SubMenu not found', 'status': 404})
                        else:
                      
                            submenu_entity.is_deleted = True
                            db.session.commit()
                            logger.info("Submenus deleted Successfully")
                            return jsonify({'message': 'SubMenu deleted successfully', 'status': 200})
                    except Exception as e:
                    
                        logger.error(f"Error deleting submenu information: {str(e)}")
                        return jsonify({'message': str(e), 'status': 500})
                    
        @self.submenu_ns.route('/activate/<int:id>')
        class SubMenuActivate(Resource):
            @self.submenu_ns.doc('submenu/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    submenu = SubMenuMasterData.query.get(id)
                    if not submenu:
                        logger.warning("No Submenu found")
                        return jsonify({'message': 'SubMenu not found', 'status': 404})
                    else:
                        submenu.is_active = 1
                        db.session.commit()
                        logger.info("Submenus activated Successfully")
                        return jsonify({'message': 'SubMenu activated successfully', 'status': 200})
                except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error activating submenu information: {str(e)}")
                        return jsonify({'message': str(e), 'status': 500})

        @self.submenu_ns.route('/deactivate/<int:id>')
        class SubMenuDeactivate(Resource):
            @self.submenu_ns.doc('submenu/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    submenu = SubMenuMasterData.query.get(id)
                    if not submenu:
                        logger.warning("No Submenu found")
                        return jsonify({'message': 'SubMenu not found', 'status': 404})
                    else:
                        submenu.is_active =0

                        db.session.commit()
                        logger.info("Submenus deactivated Successfully")
                        return jsonify({'message': 'SubMenu deactivated successfully', 'status': 200})
                except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error deactivating  submenu information: {str(e)}")
                        return jsonify({'message': str(e), 'status': 500})

        
        self.api.add_namespace(self.submenu_ns)