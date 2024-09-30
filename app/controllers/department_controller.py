import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.adminuser import AdminBasicInformation, DepartmentMaster
from sqlalchemy import desc
class DepartmentController:
    def __init__(self,api):
        self.api = api
        self.department_model = api.model('Department', {
            'department_name': fields.String(required=True, description='Department Name'),
        })
        
        self.department_bp = Blueprint('department', __name__)
        self.department_ns = Namespace('department', description='Department Details', authorizations=authorizations)
     
        self.register_routes()

        
    def register_routes(self):
        @self.department_ns.route('/add')
        class DepartmentAdd(Resource):
            @self.department_ns.doc('department/add', security='jwt')
            @self.api.expect(self.department_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    department_name = data.get('department_name')
                    current_user_id = get_jwt_identity()
              
                    if not department_name:
                   
                        return jsonify({'message': 'Please Provide Department name', 'status': 201})
                    else:
                        existing_deptartment = DepartmentMaster.query.filter_by(department_name=department_name).first()

                        if existing_deptartment:
                            
                            return jsonify({'message': 'Department already exists', 'status': 409})
                        department = DepartmentMaster(department_name=department_name,created_by=current_user_id)
                        db.session.add(department)
                        db.session.commit()
    
                        return jsonify({'message': 'Department created successfully', 'status': 200})
                except Exception as e:
                    
                 
                    return jsonify({'message': str(e), 'status': 500})
        @self.department_ns.route('/list')
        class DepartmentList(Resource):
            @self.department_ns.doc('department/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
             
                    departments = DepartmentMaster.query.filter_by(is_deleted=False).order_by(desc(DepartmentMaster.updated_at)).all()
                    departments_data = []
                    
                    for department in departments:
                        created_by = 'Admin'
                        updated_by = 'Admin'
                        if department.created_by is not None:
                            createadmindata = AdminBasicInformation.query.filter_by(admin_login_id = department.created_by).first()
                            if createadmindata is not None:
                                created_by = createadmindata.first_name
                            else :
                                created_by = 'Admin'
                        if department.updated_by is not None:   
                            updateadmindata = AdminBasicInformation.query.filter_by(admin_login_id = department.updated_by).first()
                            if updateadmindata is not None:
                                updated_by = updateadmindata.first_name
                            else :
                                updated_by = 'Admin'
                        department_data = {
                        'id': department.department_id,
                        'department_name': department.department_name,
                        'is_active':department.is_active,
                        'is_deleted': department.is_deleted, 
                        'created_by':department.created_by,
                        'created_at':department.created_at,
                        'updated_at':department.updated_at,
                            'created_by':created_by,
                            'updated_by':updated_by,
                        }
                        departments_data.append(department_data)
                    
                    if not departments_data:
                    
                        return jsonify({'message': 'No Department found', 'status': 404})
                    else:
                      
                        return jsonify({'message': 'Department found Successfully', 'status': 200, 'data': departments_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
                    
        
                
        @self.department_ns.route('/edit/<string:id>')
        class DepartmentEdit(Resource):
            @self.department_ns.doc('department/edit', security='jwt')
            @api.expect(self.department_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    department_name = data.get('department_name')
                    current_user_id = get_jwt_identity()
                    if not department_name:

                        return jsonify({'message': 'Please provide department name', 'status': 400})
                    else:
                        department = DepartmentMaster.query.get(id)
                        if not department:
       
                            return jsonify({'message': 'Department not found', 'status': 404})
                        else:
                            existing_deptartment = DepartmentMaster.query.filter_by(department_name=department_name).first()

                            if existing_deptartment:

                                return jsonify({'message': 'Department already exists', 'status': 409})
                            department.department_name = department_name
                            department.updated_by= current_user_id
                            db.session.commit()

                            return jsonify({'message': 'Department updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()

                    return jsonify({'message': str(e), 'status': 500})
                    
            @self.department_ns.doc('department/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    department = DepartmentMaster.query.get(id)
                    if not department:
      
                        return jsonify({'message': 'Department not found', 'status': 404})
                    else:
                        department_data = {
                            'id': department.department_id,
                            'department_name': department.department_name,
                            'is_active':department.is_active,
                            'is_deleted': department.is_deleted, 
                            'created_by':department.created_by,
                            'created_at':department.created_at,
                            'updated_at':department.updated_at
                        }
                        print(department_data)
                 
                        return jsonify({'message': 'Department found Successfully', 'status': 200,'data':department_data})
                except Exception as e:
                    return jsonify({'message': str(e), 'status': 500})
        
        @self.department_ns.route('delete/<string:id>')
        class DepartmentDelete(Resource):
            @self.department_ns.doc('department/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        department_entity = DepartmentMaster.query.get(id)
                        if not department_entity:
     
                            return jsonify({'message': 'Department not found', 'status': 404})
                        else:
                            # department_entity.is_active = 0
                            department_entity.is_deleted=True
                            db.session.commit()
       
                            return jsonify({'message': 'Department deleted successfully', 'status': 200})
                    except Exception as e:
                    

                        return jsonify({'message': str(e), 'status': 500})
                        
        @self.department_ns.route('/activate/<string:id>')
        class DepartmentActivate(Resource):
            @self.department_ns.doc('department/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    department = DepartmentMaster.query.get(id)
                    if not department:

                        return jsonify({'message': 'Department not found', 'status': 404})
                    else:
                        department.is_active = 1
                        department.updated_by = get_jwt_identity()
                        db.session.commit()

                        return jsonify({'message': 'Department activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()

                    return jsonify({'message': str(e), 'status': 500})

        @self.department_ns.route('/deactivate/<string:id>')
        class DepartmentDeactivate(Resource):
            @self.department_ns.doc('department/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    department = DepartmentMaster.query.get(id)
                    if not department:

                        return jsonify({'message': 'Department not found', 'status': 404})
                    else:
                        department.is_active = 0
                        department.updated_by = get_jwt_identity()
                        db.session.commit()

                        return jsonify({'message': 'Department deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
 
                    return jsonify({'message': str(e), 'status': 500})
        
        self.api.add_namespace(self.department_ns)