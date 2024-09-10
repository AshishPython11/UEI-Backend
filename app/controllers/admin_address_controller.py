from datetime import datetime
import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.adminuser import AdminAddress


import logging

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)
class AdminAddressController:
    def __init__(self,api):
        self.api = api
        self.admin_address_model = api.model('AdminAddress', {
            'admin_id': fields.String(required=True, description='Admin Id'),
            'address1': fields.String(required=True, description='Admin Address 1'),
            'address2': fields.String(required=False, description='Admin Address 2'),
            'country': fields.String(required=True, description='Country'),
            'state': fields.String(required=True, description='State'),
            'city': fields.String(required=True, description='City'),
            'district': fields.String(required=True, description='District'),
            'pincode': fields.String(required=True, description='Pincode'),
            'address_type': fields.String(required=True, description='Address Type',enum=["current_address", "permanent_address"])
        })
        self.required_fields = ['admin_id', 'address1', 'address2', 'country', 'state', 'city', 'district', 'pincode', 'address_type']
        self.admin_address_bp = Blueprint('admin_address', __name__)
        self.admin_address_ns = Namespace('admin_address', description='Admin Address Details', authorizations=authorizations)
        self.register_routes()
    def calculate_completion_percentage(self):
        total_required_fields = len(self.required_fields)
        return round((len(self.required_fields) / total_required_fields) * 100, 2) if total_required_fields > 0 else 0
    def register_routes(self):
        @self.admin_address_ns.route('/add')
        class AdminAddressAdd(Resource):
            @self.admin_address_ns.doc('admin_address/add', security='jwt')
            @self.api.expect(self.admin_address_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    admin_id = data.get('admin_id')
                    address1 = data.get('address1')
                    address2 = data.get('address2')
                    country = data.get('country')
                    state = data.get('state')
                    city = data.get('city')
                    district = data.get('district')
                    pincode = data.get('pincode')
                    address_type = data.get('address_type')
                    current_user_id = get_jwt_identity()
                
                        
                    if not admin_id :
                        return jsonify({'message': 'Please Provide Admin Id', 'status': 201})
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
                        admin_address = AdminAddress(admin_id=admin_id,address1=address1,address2=address2,country=country,state=state,city=city,district=district,pincode=pincode,address_type=address_type,is_active=1,created_by=current_user_id)
                        db.session.add(admin_address)
                        db.session.commit()
                        message = 'Admin Address created successfully'
                        return jsonify({'message': 'Admin Address Created Successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})

        @self.admin_address_ns.route('/list')
        class AdminAddressList(Resource):
            @self.admin_address_ns.doc('admin_address/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    admin_addresses = AdminAddress.query.filter_by(is_active=1).all()
                    admin_addresses_data = []
                    
                    for admin_address in admin_addresses:
                        admin_address_data = {
                            'id': admin_address.admin_address_id,
                            'admin_id': admin_address.admin_id,
                            'address1': admin_address.address1,
                            'address2': admin_address.address2,
                            'country': admin_address.country,
                            'state': admin_address.state,
                            'city': admin_address.city,
                            'district': admin_address.district,
                            'pincode': admin_address.pincode,
                            'address_type': admin_address.address_type,
                            'is_active':admin_address.is_active
                        }
                        admin_addresses_data.append(admin_address_data)
                    
                    if not admin_addresses_data:
                        return jsonify({'message': 'No Admin Addresses found', 'status': 404})
                    else:
                        return jsonify({'message': 'Admin Addresses found Successfully', 'status': 200, 'data': admin_addresses_data})
                except Exception as e:
                    return jsonify({'message': str(e), 'status': 500})
        @self.admin_address_ns.route('/alldata')
        class AdminAddressList(Resource):
            @self.admin_address_ns.doc('admin_address/alldata', security='jwt')
            @jwt_required()        
            def get(self):
                try:
                    admin_addresses = AdminAddress.query.all()
                    admin_addresses_data = []

                    for admin_address in admin_addresses:
                        admin_address_data = {
                            'id': admin_address.admin_address_id,
                            'admin_id': admin_address.admin_id,
                            'address1': admin_address.address1,
                            'address2': admin_address.address2,
                            'country': admin_address.country,
                            'state': admin_address.state,
                            'city': admin_address.city,
                            'district': admin_address.district,
                            'pincode': admin_address.pincode,
                            'address_type': admin_address.address_type,
                            'is_active': admin_address.is_active
                        }
                        admin_addresses_data.append(admin_address_data)

                    if not admin_addresses_data:
                        message = 'No Admin Addresses found'
                        return jsonify({'message': message, 'status': 404})
                    else:
                        message = 'Admin Addresses found successfully'
                        return jsonify({'message': message, 'status': 200, 'data': admin_addresses_data})
                except Exception as e:
                    return jsonify({'message': str(e), 'status': 500})
                   
        @self.admin_address_ns.route('/edit/<int:id>')
        class AdminAddressEdit(Resource):
            @self.admin_address_ns.doc('admin_address/edit', security='jwt')
            @api.expect(self.admin_address_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    admin_id = data.get('admin_id')
                    address1 = data.get('address1')
                    address2 = data.get('address2')
                    country = data.get('country')
                    state = data.get('state')
                    city = data.get('city')
                    district = data.get('district')
                    pincode = data.get('pincode')
                    address_type = data.get('address_type')
                    current_user_id = get_jwt_identity()
                    
                    if not admin_id :
                        return jsonify({'message': 'Please Provide Admin Id', 'status': 201})
                    if not address1 :
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
                       
                        admin_address = AdminAddress.query.filter_by(admin_id=id,address_type=address_type).first()
                        if not admin_address:
                
                            admin_address = AdminAddress(
                                admin_id=admin_id,
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
                            db.session.add(admin_address)
                            db.session.commit()
                            message = 'Admin Address created successfully'
                            return jsonify({'message': message, 'status': 201})

                        else:
                            admin_address.admin_id = admin_id
                            admin_address.address1 = address1
                            admin_address.address2 = address2
                            admin_address.country = country
                            admin_address.state = state
                            admin_address.city = city
                            admin_address.district = district
                            admin_address.pincode = pincode
                            admin_address.address_type = address_type
                            admin_address.updated_by = current_user_id
                            db.session.commit()
                            message = 'Admin Address updated successfully'
                            return jsonify({'message': message, 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})
                            
                    
            @self.admin_address_ns.doc('admin_address/get', security='jwt')
            @jwt_required()
            def get(self, id):
              
                try:
                    admin_addresses = AdminAddress.query.filter_by(admin_id=id).all()
                    if not admin_addresses:
                        message = 'Admin Address not found'
                        return jsonify({'message': message, 'status': 404})
                    else: 
                        admin_addresses_data=[]
                        for admin_address in admin_addresses:
                       
                            admin_address_data = {
                                'id': admin_address.admin_address_id,
                                'admin_id': admin_address.admin_id,
                                'address1': admin_address.address1,
                                'address2': admin_address.address2,
                                'country': admin_address.country,
                                'state': admin_address.state,
                                'city': admin_address.city,
                                'district': admin_address.district,
                                'pincode': admin_address.pincode,
                                'address_type': admin_address.address_type,
                                'is_active':admin_address.is_active
                            }
                            admin_addresses_data.append(admin_address_data)

                        print(admin_address_data)
                        message = 'Admin Address found successfully'
                        return jsonify({'message': message, 'status': 200, 'data': admin_addresses_data})
                        
                except Exception as e:
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.admin_address_ns.route('/activate/<int:id>')
        class AdminAddressActivate(Resource):
            @self.admin_address_ns.doc('admin_address/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    admin_address = AdminAddress.query.get(id)
                    if not admin_address:
                        message = 'Admin Address not found'
                        return jsonify({'message': message, 'status': 404})
                    else:
                        admin_address.is_active = 1
                        db.session.commit()
                        message = 'Admin Address activated successfully'
                        return jsonify({'message': message, 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})

        @self.admin_address_ns.route('/deactivate/<int:id>')
        class AdminAddressDeactivate(Resource):
            @self.admin_address_ns.doc('admin_address/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    admin_address = AdminAddress.query.get(id)
                    if not admin_address:
                        message = 'Admin Address not found'
                        return jsonify({'message': message, 'status': 404})
                    else:
                        admin_address.is_active = 0
                        db.session.commit()
                        message = 'Admin Address deactivated successfully'
                        return jsonify({'message': message, 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    return jsonify({'message': str(e), 'status': 500})
            
        
        self.api.add_namespace(self.admin_address_ns)