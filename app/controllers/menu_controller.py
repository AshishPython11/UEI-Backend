import json
from urllib.parse import urlparse
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.adminuser import AdminBasicInformation
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.role import FormMasterData, MenuMasterData, RoleMasterData, RoleVsFormMasterData, SubMenuMasterData,ManageRole,RoleVsAdminMaster
from sqlalchemy import desc
from sqlalchemy import and_, func
class MenuController:
    def __init__(self,api):
        self.api = api
        self.menu_model = api.model('Menu', {
            'menu_name': fields.String(required=True, description='Menu Name'),
            'priority': fields.String(required=True, description='Priority'),
        })
        
        self.menu_bp = Blueprint('menu', __name__)
        self.menu_ns = Namespace('menu', description='Menu Details', authorizations=authorizations)
        
        self.register_routes()

        
    def register_routes(self):
        @self.menu_ns.route('/list')
        class MenuList(Resource):
            @self.menu_ns.doc('menu/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
               
                    menues = MenuMasterData.query.filter_by(is_deleted=False).order_by(desc(MenuMasterData.updated_at)).all()
                    menues_data = []
                    
                    for menu in menues:
                        forms = FormMasterData.query.filter_by(menu_master_id=menu.menu_master_id, is_deleted=False).all()

                    
                        submenus = SubMenuMasterData.query.filter_by(menu_master_id=menu.menu_master_id, is_deleted=False).all()

                    
                        forms_data = []
                        for form in forms:
                            form_data = {
                                'form_master_id': form.form_master_id,
                                'form_name': form.form_name,
                                'form_url': form.form_url,
                                'form_description': form.form_description,
                                'is_menu_visible': form.is_menu_visible,
                                'is_active': form.is_active,
                                'created_by': form.created_by,
                                'updated_by': form.updated_by,
                                'created_at': form.created_at,
                                'updated_at': form.updated_at
                                
                            }
                            forms_data.append(form_data)

                        
                        submenus_data = []
                        for submenu in submenus:
                            submenu_data = {
                                'submenu_master_id': submenu.submenu_master_id,
                                'submenu_name': submenu.menu_name,
                                'submenu_priority': submenu.priority,
                                'is_active': submenu.is_active,
                                'created_by': submenu.created_by,
                                'updated_by': submenu.updated_by,
                                'created_at': submenu.created_at,
                                'updated_at': submenu.updated_at
                                
                            }
                            submenus_data.append(submenu_data)
                        created_by = 'Admin'
                        updated_by = 'Admin'
                        if menu.created_by is not None:
                            createadmindata = AdminBasicInformation.query.filter_by(admin_login_id = menu.created_by).first()
                            if createadmindata is not None:
                                created_by = createadmindata.first_name
                            else :
                                created_by = 'Admin'
                        if menu.updated_by is not None:   
                            updateadmindata = AdminBasicInformation.query.filter_by(admin_login_id = menu.updated_by).first()
                            if updateadmindata is not None:
                                updated_by = updateadmindata.first_name
                            else :
                                updated_by = 'Admin'
                        menu_data = {
                            'id': menu.menu_master_id,
                            'menu_name': menu.menu_name,
                            'priority': menu.priority,
                            'is_active': menu.is_active,
                            'is_deleted': menu.is_deleted, 
                            'created_at':menu.created_at,
                            'updated_at':menu.updated_at,
                            'created_by':created_by,
                            'updated_by':updated_by,
                            'form_data': forms_data,      
                            'submenus_data': submenus_data
                        
                        }
                        menues_data.append(menu_data)
                    
                    if not menues_data:
       
                        return jsonify({'message': 'No Menu found', 'status': 404})
                    else:
      
                        return jsonify({'message': 'Menus found Successfully', 'status': 200, 'data': menues_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
                    
        @self.menu_ns.route('/list/<user_type>')
        class MenuListByRole(Resource):
            def remove_duplicate_menus(self,menus):
                unique_menus_map = {}
                
                for menu in menus:
                    if menu['menu_name'] not in unique_menus_map:
                        unique_menus_map[menu['menu_name']] = menu
                
                return list(unique_menus_map.values())
            def sorted_data(self,data):
               
                sorted_menus = sorted(data, key=lambda x: x['priority'])
              
                for menu in sorted_menus:
                    menu['submenus'] = sorted(menu['submenus'], key=lambda x: x['priority'])
                return sorted_menus
            @self.menu_ns.doc('menu/list_by_user_role', security='jwt')
            @jwt_required()
            def get(self,user_type):
                try:
                    role = RoleMasterData.query.filter(RoleMasterData.role_name.ilike(user_type)).first()
                    menues_data = []
                    sorted_menus = []
                    if role:
                        forms = RoleVsFormMasterData.query.filter_by(role_master_id=role.role_master_id,is_active=1).all()
                        print(forms)
                        for form in forms:
                            formdata = FormMasterData.query.filter_by(form_master_id=form.form_master_id,is_active=1).first()
                            if formdata:
                                menu = MenuMasterData.query.filter_by(menu_master_id = formdata.menu_master_id,is_active=1).first()
                                if formdata.form_url.startswith("http://") or formdata.form_url.startswith("https://"):
                              
                                    parsed_url = urlparse(formdata.form_url)
                                else:
                            
                                    parsed_url = urlparse("//" + formdata.form_url)
                                menu_url = parsed_url.path
                                if menu :
                                    created_by = 'Admin'
                                    updated_by = 'Admin'
                                    if menu.created_by is not None:
                                        createadmindata = AdminBasicInformation.query.filter_by(admin_login_id = menu.created_by).first()
                                        if createadmindata is not None:
                                            created_by = createadmindata.first_name
                                        else :
                                            created_by = 'Admin'
                                    if menu.updated_by is not None:   
                                        updateadmindata = AdminBasicInformation.query.filter_by(admin_login_id = menu.updated_by).first()
                                        if updateadmindata is not None:
                                            updated_by = updateadmindata.first_name
                                        else :
                                            updated_by = 'Admin'
                                    submenu_data = []
                                    submenus = SubMenuMasterData.query.filter_by(menu_master_id = menu.menu_master_id).order_by(SubMenuMasterData.priority.asc()).all()
                                    for submenu in submenus:
                                        if formdata.form_url.startswith("http://") or formdata.form_url.startswith("https://"):
                                            parsed_url = urlparse(formdata.form_url)
                                        else:
                                            parsed_url = urlparse("//" + formdata.form_url)

                                        path_without_domain = parsed_url.path
                                        submenuinfo={
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
                                            'url':path_without_domain,
                                            'is_menu_visible': formdata.is_menu_visible,
                                            'is_search': form.is_search,
                                            'is_save': form.is_save,
                                            'is_update': form.is_update,
                                        }
                                        submenu_data.append(submenuinfo)
                                    menuinfo ={
                                    'id': menu.menu_master_id,
                                    'menu_name': menu.menu_name,
                                    'priority': menu.priority,
                                    'is_active': menu.is_active,
                                    'is_deleted': menu.is_deleted, 
                                    'created_at':menu.created_at,
                                    'updated_at':menu.updated_at,
                                    'created_by':created_by,
                                    'updated_by':updated_by, 
                                    'submenus':submenu_data,
                                    'url':menu_url,
                                    'is_search': form.is_search,
                                    'is_save': form.is_save,
                                    'is_update': form.is_update,
                                    }
                                    menues_data.append(menuinfo)
                                    sorted_menus = self.sorted_data(menues_data)
                                    sorted_menus = self.remove_duplicate_menus(sorted_menus)
                    if not sorted_menus:
                
                        return jsonify({'message': 'No Menu found', 'status': 404})
                    else:
              
                        return jsonify({'message': 'Menus found Successfully', 'status': 200, 'data': sorted_menus})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
        @self.menu_ns.route('/add')
        class MenuAdd(Resource):
            @self.menu_ns.doc('menu/add', security='jwt')
            @self.api.expect(self.menu_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    menu_name = data.get('menu_name')
                    priority = data.get('priority')
                    current_user_id = get_jwt_identity()
                    if not menu_name :
                 
                        return jsonify({'message': 'Please Provide Menu name', 'status': 201})
                    if not priority :
                 
                        return jsonify({'message': 'Please Provide Priority', 'status': 201})
                    else:
                        menu = MenuMasterData(menu_name=menu_name,priority=priority,is_active=1,created_by=current_user_id)
                        db.session.add(menu)
                        db.session.commit()
        
                        return jsonify({'message': 'Menu created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
          
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.menu_ns.route('/edit/<string:id>')
        class MenuEdit(Resource):
            @self.menu_ns.doc('menu/edit', security='jwt')
            @api.expect(self.menu_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    menu_name = data.get('menu_name')
                    priority = data.get('priority')
                    current_user_id = get_jwt_identity()
                    if not menu_name :
               
                        return jsonify({'message': 'Please Provide Menu name', 'status': 201})
                    if not priority :
            
                        return jsonify({'message': 'Please Provide Priority', 'status': 201})
                    else:
                        menu = MenuMasterData.query.get(id)
                        if not menu:
                            return jsonify({'message': 'Menu not found', 'status': 404})
                        else:
                            menu.menu_name = menu_name
                            menu.priority = priority
                            menu.updated_by = current_user_id
                            db.session.commit()
                   
                            return jsonify({'message': 'Menu updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
     
                    return jsonify({'message': str(e), 'status': 500})
                        
            @self.menu_ns.doc('menu/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    menu = MenuMasterData.query.get(id)
                    if not menu:
               
                        return jsonify({'message': 'Menu not found', 'status': 404})
                    else:
                        menu_data = {
                            'id': menu.menu_master_id,
                            'menu_name': menu.menu_name,
                            'priority': menu.priority,
                            'is_active': menu.is_active,
                            'is_deleted': menu.is_deleted, 
                            'created_at':menu.created_at,
                            'updated_at':menu.updated_at,
                        }
                        print(menu_data)
           
                        return jsonify({'message': 'Menu found Successfully', 'status': 200,'data':menu_data})
                except Exception as e:
  
                    return jsonify({'message': str(e), 'status': 500})
        @self.menu_ns.route('delete/<string:id>')
        class MenuDelete(Resource):
            @self.menu_ns.doc('menu/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        menu_entity = MenuMasterData.query.get(id)
                        if not menu_entity:
          
                            return jsonify({'message': 'menu not found', 'status': 404})
                        else:
                          
                            menu_entity.is_deleted=True
                            db.session.commit()
                 
                            return jsonify({'message': 'Menu deleted successfully', 'status': 200})
                    except Exception as e:
                       

                        return jsonify({'message': str(e), 'status': 500})
                    
        @self.menu_ns.route('/activate/<string:id>')
        class MenuActivate(Resource):
            @self.menu_ns.doc('menu/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    menu = MenuMasterData.query.get(id)
                    if not menu:
         
                        return jsonify({'message': 'Menu not found', 'status': 404})

                    menu.is_active = 1
                    db.session.commit()
                
                    return jsonify({'message': 'Menu activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()

                    return jsonify({'message': str(e), 'status': 500})

        @self.menu_ns.route('/deactivate/<string:id>')
        class MenuDeactivate(Resource):
            @self.menu_ns.doc('menu/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    
                    menu = MenuMasterData.query.get(id)
                    if not menu:
                        return jsonify({'message': 'Menu not found', 'status': 404})

                    menu.is_active = 0
                    db.session.commit()
               
                    return jsonify({'message': 'Menu deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
              
                    return jsonify({'message': str(e), 'status': 500})
        @self.menu_ns.route('/menu/list_by_admin/<string:admin_id>')
        class MenuListByAdmin(Resource):
            @self.menu_ns.doc('menu/list_by_admin', security='jwt')
            @jwt_required()
            def remove_duplicate_submenus(self, submenus, key=None):
                        if key is None:
                            key = lambda x: x
                            
                        unique_submenus_map = {}
                        
                        for submenu in submenus:
                            k = key(submenu)
                            if k not in unique_submenus_map:
                                unique_submenus_map[k] = submenu
                        
                        return list(unique_submenus_map.values())
            def get(self, admin_id):
                    try:
                        manage_roles = ManageRole.query.filter_by(admin_id=admin_id).all()
                        
                        if not manage_roles:
                            return jsonify({'message': 'No roles found for the provided admin_id', 'status': 404})
                        
                        menus_data = {}
                        
                        for manage_role in manage_roles:
                            form = FormMasterData.query.filter_by(form_master_id=manage_role.form_master_id).first()
                            
                            if form:
                                menu = MenuMasterData.query.filter_by(menu_master_id=form.menu_master_id).first()
                                
                                if menu:
                                    menu_name = menu.menu_name
                                    
                                    if menu_name not in menus_data:
                                        menus_data[menu_name] = {
                                            'id': menu.menu_master_id,
                                            'menu_name': menu.menu_name,
                                            'priority': menu.priority,
                                            'is_active': menu.is_active,
                                            'is_deleted': menu.is_deleted,
                                            'created_at': menu.created_at,
                                            'updated_at': menu.updated_at,
                                            'submenus': [], 
                                            'form_data': {
                                                'is_search': manage_role.is_search,
                                                'is_save': manage_role.is_save,
                                                'is_update': manage_role.is_update,
                                                'form_url': form.form_url
                                            }
                                        }
                                    
                                if form.sub_menu_master_id is not None:
                                    submenu = SubMenuMasterData.query.filter_by(submenu_master_id=form.sub_menu_master_id).first()
                                    
                                    if submenu:
                                        submenu_info = {
                                            'id': submenu.submenu_master_id,
                                            'menu_name': submenu.menu_name,
                                            'priority': submenu.priority,
                                            'menu_master_id': menu.menu_master_id,
                                            'menu_master_name': menu.menu_name,
                                            'is_active': submenu.is_active,
                                            'is_deleted': submenu.is_deleted,
                                            'created_at': submenu.created_at,
                                            'updated_at': submenu.updated_at,
                                        }
                                        
                                        
                                    if submenu_info not in menus_data[menu_name]['submenus']:
                                            menus_data[menu_name]['submenus'].append(submenu_info)
                        
                        
                        menus_data_list = list(menus_data.values())
                        
                        
                        for menu in menus_data_list:
                            menu['submenus'] = self.remove_duplicate_submenus(menu['submenus'], key=lambda x: x['menu_name'])
                        
                        if not menus_data_list:
                       
                            return jsonify({'message': 'No menus found for the provided admin_id', 'status': 404})
                        else:
              
                            return jsonify({'message': 'Menus found successfully', 'status': 200, 'data': menus_data_list})
                    except Exception as e:
                   
    
                        return jsonify({'message': str(e), 'status': 500})

        self.api.add_namespace(self.menu_ns)