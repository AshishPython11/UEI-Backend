from datetime import datetime
import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.student import StudentAddress

class StudentAddressController:
    def __init__(self,api):
        self.api = api
        self.student_address_model = api.model('StudentAddress', {
            'student_id': fields.String(required=True, description='Student Id'),
            'address1': fields.String(required=True, description='Student Address 1'),
            'address2': fields.String(required=False, description='Student Address 2'),
            'country': fields.String(required=True, description='Country'),
            'state': fields.String(required=True, description='State'),
            'city': fields.String(required=True, description='City'),
            'district': fields.String(required=True, description='District'),
            'pincode': fields.String(required=True, description='Pincode'),
            'address_type': fields.String(required=True, description='Address Type')
        })
        
        self.student_address_bp = Blueprint('student_address', __name__)
        self.student_address_ns = Namespace('student_address', description='Student Address Details', authorizations=authorizations)
  
        self.register_routes()

        
    def register_routes(self):
        @self.student_address_ns.route('/list')
        class StudentAddressList(Resource):
            @self.student_address_ns.doc('student_address/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    student_addresses = StudentAddress.query.filter_by(is_active=1).all()
                    student_addresses_data = []
                    
                    for student_address in student_addresses:
                        student_address_data = {
                            'id': student_address.address_id,
                            'student_id': student_address.student_id,
                            'address1': student_address.address1,
                            'address2': student_address.address2,
                            'country': student_address.country,
                            'state': student_address.state,
                            'city': student_address.city,
                            'district': student_address.district,
                            'pincode': student_address.pincode,
                            'address_type': student_address.address_type,
                            'is_active': student_address.is_active,
                            'created_at':student_address.created_at,
                            'updated_at':student_address.updated_at,
                        }
                        student_addresses_data.append(student_address_data)
                    
                    if not student_addresses_data:
      
                        return jsonify({'message': 'No StudentAddress found', 'status': 404})
                    else:
       
                        return jsonify({'message': 'StudentAddresses found Successfully', 'status': 200, 'data': student_addresses_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
                
        @self.student_address_ns.route('/alldata')
        class StudentAddressList(Resource):
            @self.student_address_ns.doc('student_address/alldata', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    student_addresses = StudentAddress.query.all()
                    student_addresses_data = []
                    
                    for student_address in student_addresses:
                        student_address_data = {
                            'id': student_address.address_id,
                            'student_id': student_address.student_id,
                            'address1': student_address.address1,
                            'address2': student_address.address2,
                            'country': student_address.country,
                            'state': student_address.state,
                            'city': student_address.city,
                            'district': student_address.district,
                            'pincode': student_address.pincode,
                            'address_type': student_address.address_type,
                            'is_active': student_address.is_active,
                            'created_at':student_address.created_at,
                            'updated_at':student_address.updated_at,
                        }
                        student_addresses_data.append(student_address_data)
                    
                    if not student_addresses_data:

                        return jsonify({'message': 'No StudentAddress found', 'status': 404})
                    else:
       
                        return jsonify({'message': 'StudentAddresses found Successfully', 'status': 200, 'data': student_addresses_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
        @self.student_address_ns.route('/add')
        class StudentAddressAdd(Resource):
            @self.student_address_ns.doc('student_address/add', security='jwt')
            @self.api.expect(self.student_address_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    student_id = data.get('student_id')
                    address1 = data.get('address1')
                    address2 = data.get('address2')
                    country = data.get('country')
                    state = data.get('state')
                    city = data.get('city')
                    district = data.get('district')
                    pincode = data.get('pincode')
                    address_type = data.get('address_type')
                    current_user_id = get_jwt_identity()
                    if not student_id :
 
                        return jsonify({'message': 'Please Provide Student Id', 'status': 201})
                    if not address1 :

                        return jsonify({'message': 'Please Provide Address 1', 'status': 201})
                   
                    if not country :
   
                        return jsonify({'message': 'Please Provide Country', 'status': 201})
                    if not state :
       
                        return jsonify({'message': 'Please Provide State', 'status': 201})
                    if not city :

                        return jsonify({'message': 'Please Provide City', 'status': 201})
                    if not district :

                        return jsonify({'message': 'Please Provide District', 'status': 201})
                    if not pincode :

                        return jsonify({'message': 'Please Provide Pincode', 'status': 201})
                    if not address_type :

                        return jsonify({'message': 'Please Provide Address Type', 'status': 201})
                    else:
                        student_address = StudentAddress(student_id=student_id,address1=address1,address2=address2,country=country,state=state,city=city,district=district,pincode=pincode,address_type=address_type,is_active = 1,created_by=current_user_id)
                        db.session.add(student_address)
                        db.session.commit()
     
                        return jsonify({'message': 'Student Address created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
 
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.student_address_ns.route('/edit/<int:id>')
        class StudentAddressEdit(Resource):
            @self.student_address_ns.doc('student_address/edit', security='jwt')
            @api.expect(self.student_address_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    student_id = data.get('student_id')
                    address1 = data.get('address1')
                    address2 = data.get('address2')
                    country = data.get('country')
                    state = data.get('state')
                    city = data.get('city')
                    district = data.get('district')
                    pincode = data.get('pincode')
                    address_type = data.get('address_type')
                    current_user_id = get_jwt_identity()
                    if not student_id :

                        return jsonify({'message': 'Please Provide Student Id', 'status': 201})
                    if not address1 :
                        if address_type == 'current':
                            return jsonify({'message': 'Please Provide Address 1', 'status': 201})
                    if not address2 :
        
                        return jsonify({'message': 'Please Provide Address 2', 'status': 201})
                    if not country :

                        return jsonify({'message': 'Please Provide Country', 'status': 201})
                    if not state :
           
                        return jsonify({'message': 'Please Provide State', 'status': 201})
                    if not city :
    
                        return jsonify({'message': 'Please Provide City', 'status': 201})
                    if not district :

                        return jsonify({'message': 'Please Provide District', 'status': 201})
                    if not pincode :

                        return jsonify({'message': 'Please Provide Pincode', 'status': 201})
                    if not address_type :
   
                        return jsonify({'message': 'Please Provide Address Type', 'status': 201})
                    else:
                  
                        student_address = StudentAddress.query.filter_by(student_id=id,address_type=address_type).first()
                        if not student_address:
                
                            student_address = StudentAddress(
                                student_id=student_id,
                                address1=address1,
                                address2=address2,
                                country=country,
                                state=state,
                                city=city,
                                district=district,
                                pincode=pincode,
                                address_type=address_type,
                                updated_by=current_user_id
                            )
                            db.session.add(student_address)
                            db.session.commit()
 
                            return jsonify({'message': 'Student Address created successfully', 'status': 201})
                        else:
                            student_address.student_id = student_id
                            student_address.address1 = address1
                            student_address.address2 = address2
                            student_address.country = country
                            student_address.state = state
                            student_address.city = city
                            student_address.district = district
                            student_address.pincode = pincode
                            student_address.address_type = address_type
                            student_address.updated_by = current_user_id
                            db.session.commit()
                     
                            return jsonify({'message': 'Student Address updated successfully', 'status': 200})
                except Exception as e:
                        db.session.rollback()
             
                        return jsonify({'message': str(e), 'status': 500})
                        
            @self.student_address_ns.doc('student_address/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
               
                    student_addresses = StudentAddress.query.filter_by(student_id=id).all()
                    if not student_addresses:
                
                        return jsonify({'message': 'Student Address not found', 'status': 404})
                    else:
                        student_addresses_data = []
                    
                        for student_address in student_addresses:
                            student_address_data = {
                                'id': student_address.address_id,
                                'student_id': student_address.student_id,
                                'address1': student_address.address1,
                                'address2': student_address.address2,
                                'country': student_address.country,
                                'state': student_address.state,
                                'city': student_address.city,
                                'district': student_address.district,
                                'pincode': student_address.pincode,
                                'address_type': student_address.address_type,
                                'is_active': student_address.is_active,
                                'created_at':student_address.created_at,
                                'updated_at':student_address.updated_at,
                            }
                            student_addresses_data.append(student_address_data)
                        print(student_address_data)
            
                        return jsonify({'message': 'Student Address found Successfully', 'status': 200,'data':student_addresses_data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
        @self.student_address_ns.route('delete/<int:id>')
        class StudentAddressDelete(Resource):
            @self.student_address_ns.doc('student_address/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        student_address = StudentAddress.query.get(id)
                        if not student_address:
                  
                            return jsonify({'message': 'Student Address  not found', 'status': 404})
                        else:
                            student_address.is_active = 0
                    
                            return jsonify({'message': 'Student Address deleted successfully', 'status': 200})
                    except Exception as e:

                        return jsonify({'message': str(e), 'status': 500})
                        
        @self.student_address_ns.route('/activate/<int:id>')
        class StudentAddressActivate(Resource):
            @self.student_address_ns.doc('student_address/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    student_address = StudentAddress.query.get(id)
                    if not student_address:
                    
                        return jsonify({'message': 'Student Address not found', 'status': 404})
                    else:
                        student_address.is_active = 1
                        db.session.commit()
               
                        return jsonify({'message': 'Student Address activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()

                    return jsonify({'message': str(e), 'status': 500})

        @self.student_address_ns.route('/deactivate/<int:id>')
        class StudentAddressDeactivate(Resource):
            @self.student_address_ns.doc('student_address/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    student_address = StudentAddress.query.get(id)
                    if not student_address:

                        return jsonify({'message': 'Student Address not found', 'status': 404})
                    else:
                        student_address.is_active = 0
                        db.session.commit()

                        return jsonify({'message': 'Student Address deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
    
                    return jsonify({'message': str(e), 'status': 500})
        
        self.api.add_namespace(self.student_address_ns)