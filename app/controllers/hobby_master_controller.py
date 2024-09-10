import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app.models.adminuser import AdminBasicInformation
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.student import Hobby
from sqlalchemy import desc
class HobbyController:
    def __init__(self,api):
        self.api = api
        self.hobby_model = api.model('Hobby', {
            'hobby_name': fields.String(required=True, description='Hobby Name'),
        })
        
        self.hobby_bp = Blueprint('hobby', __name__)
        self.hobby_ns = Namespace('hobby', description='Hobby Details', authorizations=authorizations)
        
        self.register_routes()

        
    def register_routes(self):
        @self.hobby_ns.route('/list')
        class HobbyList(Resource):
            @self.hobby_ns.doc('hobby/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
             
                    hobbyes = Hobby.query.filter_by(is_deleted=False).order_by(desc(Hobby.updated_at)).all()
                    hobbyes_data = []
                    
                    for hobby in hobbyes:
                        created_by = 'Admin'
                        updated_by = 'Admin'
                        if hobby.created_by is not None:
                            createadmindata = AdminBasicInformation.query.filter_by(admin_login_id = hobby.created_by).first()
                            if createadmindata is not None:
                                created_by = createadmindata.first_name
                            else :
                                created_by = 'Admin'
                        if hobby.updated_by is not None:   
                            updateadmindata = AdminBasicInformation.query.filter_by(admin_login_id = hobby.updated_by).first()
                            if updateadmindata is not None:
                                updated_by = updateadmindata.first_name
                            else :
                                updated_by = 'Admin'
                        hobby_data = {
                            'id': hobby.hobby_id,
                            'hobby_name': hobby.hobby_name,
                            'is_active': hobby.is_active,
                            'is_deleted': hobby.is_deleted, 
                            'created_at':hobby.created_at,
                            'updated_at':hobby.updated_at,
                            'created_by':created_by,
                            'updated_by':updated_by,
                        }
                        hobbyes_data.append(hobby_data)
                    
                    if not hobbyes_data:
           
                        return jsonify({'message': 'No Hobby found', 'status': 404})
                    else:
  
                        return jsonify({'message': 'Hobbies found Successfully', 'status': 200, 'data': hobbyes_data})
                except Exception as e:
 
                    return jsonify({'message': str(e), 'status': 500})
        @self.hobby_ns.route('/add')
        class HobbyAdd(Resource):
            @self.hobby_ns.doc('hobby/add', security='jwt')
            @self.api.expect(self.hobby_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    hobby_name = data.get('hobby_name')
                    current_user_id = get_jwt_identity()
                    if not hobby_name:
                        return jsonify({'message': 'Please Provide Hobby name', 'status': 201})
                    else:
                        hobby = Hobby(hobby_name=hobby_name,is_active = 1,created_by = current_user_id)
                        db.session.add(hobby)
                        db.session.commit()
         
                        return jsonify({'message': 'Hobby created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()

                    return jsonify({'message': str(e), 'status': 500})
                
        @self.hobby_ns.route('/edit/<int:id>')
        class HobbyEdit(Resource):
            @self.hobby_ns.doc('hobby/edit', security='jwt')
            @api.expect(self.hobby_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    hobby_name = data.get('hobby_name')
                    current_user_id = get_jwt_identity()
                    if not hobby_name:
         
                        return jsonify({'message': 'Please provide hobby name', 'status': 400})
                    else:
                        hobby = Hobby.query.get(id)
                        if not hobby:
         
                            return jsonify({'message': 'Hobby not found', 'status': 404})
                        else:
                            hobby.hobby_name = hobby_name
                            hobby.updarted_by = current_user_id
                            db.session.commit()
    
                            return jsonify({'message': 'Hobby updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()

                    return jsonify({'message': str(e), 'status': 500})
                    
            @self.hobby_ns.doc('hobby/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    hobby = Hobby.query.get(id)
                    if not hobby:
            
                        return jsonify({'message': 'Hobby not found', 'status': 404})
                    else:
                        hobby_data = {
                            'id': hobby.hobby_id,
                            'hobby_name': hobby.hobby_name,
                            'is_active': hobby.is_active,
                            'is_deleted': hobby.is_deleted, 
                            'created_at':hobby.created_at,
                            'updated_at':hobby.updated_at,
                        }
                        print(hobby_data)
       
                        return jsonify({'message': 'Hobby found Successfully', 'status': 200,'data':hobby_data})
                except Exception as e:
                   
   
                    return jsonify({'message': str(e), 'status': 500})
                    
        @self.hobby_ns.route('delete/<int:id>')
        class HobbyDelete(Resource):
            @self.hobby_ns.doc('hobby/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        hobby_entity = Hobby.query.get(id)
                        if not hobby_entity:
               
                            return jsonify({'message': 'hobby not found', 'status': 404})
                        else:
                         
                            hobby_entity.is_deleted=True
                            db.session.commit()
                     
                            return jsonify({'message': 'Hobby deleted successfully', 'status': 200})
                    except Exception as e:
                        
       
                        return jsonify({'message': str(e), 'status': 500})
                        
        @self.hobby_ns.route('/activate/<int:id>')
        class HobbyActivate(Resource):
            @self.hobby_ns.doc('hobby/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    hobby = Hobby.query.get(id)
                    if not hobby:
             
                        return jsonify({'message': 'Hobby not found', 'status': 404})
                    else:
                        hobby.is_active = 1
                        db.session.commit()
           
                        return jsonify({'message': 'Hobby activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()

                    return jsonify({'message': str(e), 'status': 500})

        @self.hobby_ns.route('/deactivate/<int:id>')
        class HobbyDeactivate(Resource):
            @self.hobby_ns.doc('hobby/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    hobby = Hobby.query.get(id)
                    if not hobby:
          
                        return jsonify({'message': 'Hobby not found', 'status': 404})
                    else:
                        hobby.is_active = 0
                        db.session.commit()
                
                        return jsonify({'message': 'Hobby deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
             
                    return jsonify({'message': str(e), 'status': 500})


        
        self.api.add_namespace(self.hobby_ns)