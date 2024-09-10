import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from jinja2 import Undefined
from app.models.adminuser import AdminBasicInformation
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.role import FormMasterData, MenuMasterData, SubMenuMasterData,ManageRole
from sqlalchemy import desc,text
class FormController:
    def __init__(self,api):
        self.api = api
        self.form_model = api.model('Form', {
            'form_name': fields.String(required=True, description='Form Name'),
            'menu_master_id': fields.String(required=True, description='Menu Id'),
            'sub_menu_master_id': fields.String(required=False, description='Sub Menu Id'),
            'form_url': fields.String(required=True, description='Form Url'),
            'form_description': fields.String(required=False, description='Form Description'),
            'is_menu_visible': fields.Boolean(required=True, description='Menu Visible')
        })
        
        self.form_bp = Blueprint('form', __name__)
        self.form_ns = Namespace('form', description='Form Details', authorizations=authorizations)
      
        self.register_routes()

        
    def register_routes(self):
        @self.form_ns.route('/list')
        class FormList(Resource):
            @self.form_ns.doc('form/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    formes = FormMasterData.query.filter_by(is_deleted=False).order_by(desc(FormMasterData.updated_at)).all()
                    formes_data = []
                    
                    for form in formes:
                        created_by = 'Admin'
                        updated_by = 'Admin'
                        
                        if form.created_by:
                            created_admin = AdminBasicInformation.query.filter_by(admin_login_id=form.created_by).first()
                            created_by = created_admin.first_name if created_admin else 'Admin'
                        
                        if form.updated_by:
                            updated_admin = AdminBasicInformation.query.filter_by(admin_login_id=form.updated_by).first()
                            updated_by = updated_admin.first_name if updated_admin else 'Admin'
                        
                        menu = MenuMasterData.query.get(form.menu_master_id)
                        menu_master_name = menu.menu_name if menu else ''
                        
                        submenu = None
                        sub_menu_master_name = ''
                        if form.sub_menu_master_id:
                            submenu = SubMenuMasterData.query.get(form.sub_menu_master_id)
                            sub_menu_master_name = submenu.menu_name if submenu else ''
                        
                        form_data = {
                            'id': form.form_master_id,
                            'form_name': form.form_name,
                            'sub_menu_master_id': form.sub_menu_master_id,
                            'sub_menu_master_name': sub_menu_master_name,
                            'menu_master_id': form.menu_master_id,
                            'menu_master_name': menu_master_name,
                            'form_url': form.form_url,
                            'form_description': form.form_description,
                            'is_menu_visible': form.is_menu_visible,
                            'is_active': form.is_active,
                            'is_deleted': form.is_deleted, 
                            'created_at': form.created_at,
                            'updated_at': form.updated_at,
                            'created_by': created_by,
                            'updated_by': updated_by,
                        }
                        formes_data.append(form_data)
                    
                    if not formes_data:
    
                        return jsonify({'message': 'No Form found', 'status': 404})
                    else:

                        return jsonify({'message': 'Forms found Successfully', 'status': 200, 'data': formes_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})

        @self.form_ns.route('/add')
        class FormAdd(Resource):
            @self.form_ns.doc('form/add', security='jwt')
            @self.api.expect(self.form_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    form_name = data.get('form_name')
                    menu_master_id = data.get('menu_master_id')
                    sub_menu_master_id = data.get('sub_menu_master_id')
                    form_url = data.get('form_url')
                    form_description = data.get('form_description')
                    is_menu_visible = data.get('is_menu_visible')
                    current_user_id = get_jwt_identity()
                    if not form_name :
       
                        return jsonify({'message': 'Please Provide Form name', 'status': 201})
                   
                    if not menu_master_id :
 
                        return jsonify({'message': 'Please Provide Menu Id', 'status': 201})
                    if not form_url :

                        return jsonify({'message': 'Please Provide Form Url', 'status': 201})
                   
                    else:
                        form = FormMasterData(form_name=form_name,sub_menu_master_id=sub_menu_master_id,menu_master_id=menu_master_id,form_url=form_url,form_description=form_description,is_menu_visible=is_menu_visible,is_active=1,created_by=current_user_id)
                        db.session.add(form)
                        db.session.commit()

                        
                except Exception as e:
                    db.session.rollback()
  
                    return jsonify({'message': str(e), 'status': 500})
                    
        @self.form_ns.route('/edit/<int:id>')
        class FormEdit(Resource):
            @self.form_ns.doc('form/edit', security='jwt')
            @api.expect(self.form_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    form_name = data.get('form_name')
                    menu_master_id = data.get('menu_master_id')
                    sub_menu_master_id = data.get('sub_menu_master_id')
                    form_url = data.get('form_url')
                    form_description = data.get('form_description')
                    is_menu_visible = data.get('is_menu_visible')
                    current_user_id = get_jwt_identity()
                    if not form_name :

                        return jsonify({'message': 'Please Provide Form name', 'status': 201})
                 
                    if not menu_master_id :
          
                        return jsonify({'message': 'Please Provide Menu Id', 'status': 201})
                    if not form_url :
 
                        return jsonify({'message': 'Please Provide Form Url', 'status': 201})
                    
                    else:
                        form = FormMasterData.query.get(id)
                        if not form:

                            return jsonify({'message': 'Form not found', 'status': 404})
                        else:
                            form.form_name = form_name
                            form.sub_menu_master_id = sub_menu_master_id
                            form.menu_master_id = menu_master_id
                            form.form_url = form_url
                            form.form_description = form_description
                            form.is_menu_visible = is_menu_visible
                            form.updated_by=current_user_id
                            db.session.commit()
           
                            return jsonify({'message': 'Form updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
             
                    return jsonify({'message': str(e), 'status': 500})
                    
            @self.form_ns.doc('form/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    form = FormMasterData.query.get(id)
                    if not form:
                        pass
     
                    else:
                        form_data = {
                            'id': form.form_master_id,
                            'form_name': form.form_name,
                            'sub_menu_master_id': form.sub_menu_master_id,
                            'menu_master_id': form.menu_master_id,
                            'form_url': form.form_url,
                            'form_description': form.form_description,
                            'is_menu_visible': form.is_menu_visible,
                            'is_active': form.is_active,
                            'is_deleted': form.is_deleted, 
                            'created_at':form.created_at,
                            'updated_at':form.updated_at,
                            
                        }
                        print(form_data)
                
                        return jsonify({'message': 'Form found Successfully', 'status': 200,'data':form_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
        @self.form_ns.route('delete/<int:id>')
        class FormDelete(Resource):
            @self.form_ns.doc('form/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        form_entity = FormMasterData.query.get(id)
                        if not form_entity:
       
                            return jsonify({'message': 'form not found', 'status': 404})
                        else:
                            str_id=str(id)
                            
                            manage_roles = ManageRole.query.filter_by(form_master_id=str_id).all()
                            
                            for manage_role in manage_roles:
                                manage_role.is_delete = True
                                
                                db.session.commit()
                            form_entity.is_active = 0
                            form_entity.is_deleted=True
                            db.session.commit()
         
                            return jsonify({'message': 'Form deleted successfully', 'status': 200})
                    except Exception as e:

                        return jsonify({'message': str(e), 'status': 500})
                    
        @self.form_ns.route('/activate/<int:id>')
        class FormActivate(Resource):
            @self.form_ns.doc('form/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    form = FormMasterData.query.get(id)
                    if not form:

                        return jsonify({'message': 'Form not found', 'status': 404})
                    else:
                        form.is_active = 1
                    
                        db.session.commit()
    
                        return jsonify({'message': 'Form activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
    
                    return jsonify({'message': str(e), 'status': 500})

        @self.form_ns.route('/deactivate/<int:id>')
        class FormDeactivate(Resource):
            @self.form_ns.doc('form/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    form = FormMasterData.query.get(id)
                    if not form:

                        return jsonify({'message': 'Form not found', 'status': 404})
                    else:
                        form.is_active = 0
                        db.session.commit()

                        return jsonify({'message': 'Form deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()

                    return jsonify({'message': str(e), 'status': 500})

        
        self.api.add_namespace(self.form_ns)