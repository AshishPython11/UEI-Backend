import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.adminuser import AdminBasicInformation, EntityType, Institution
from sqlalchemy import desc
class InstituteController:
    def __init__(self,api):
        self.api = api
        self.institution_model = api.model('Institution', {
            'institution_name': fields.String(required=True, description='Institution Name'),
            'entity_id': fields.String(required=False, description='Entity Id'),
            'address': fields.String(required=False, description='Institution Address'),
            'country': fields.String(required=False, description='Institution Country'),
            'state': fields.String(required=False, description='Institution State'),
            'city': fields.String(required=False, description='Institution City'),
            'district': fields.String(required=False, description='Institution District'),
            'pincode': fields.String(required=False, description='Institution Pincode'),
            'website_url': fields.String(required=False, description='Institution Webste Url'),
            'mobile_no': fields.String(required=False, description='Institution Mobile Number'),
            'email_id': fields.String(required=False, description='Institution Email id')
        })
        
        self.institution_bp = Blueprint('institution', __name__)
        self.institution_ns = Namespace('institution', description='Institution Details', authorizations=authorizations)
     
        self.register_routes()

        
    def register_routes(self):
        @self.institution_ns.route('/list')
        class InstitutionList(Resource):
            @self.institution_ns.doc('institution/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
             
                    institutiones = Institution.query.filter_by(is_deleted=False).order_by(desc(Institution.updated_at)).all()
                    institutiones_data = []
                    
                    for institution in institutiones:
                        created_by = 'Admin'
                        updated_by = 'Admin'
                        if institution.created_by is not None:
                            createadmindata = AdminBasicInformation.query.filter_by(admin_login_id = institution.created_by).first()
                            if createadmindata is not None:
                                created_by = createadmindata.first_name
                            else :
                                created_by = 'Admin'
                        if institution.updated_by is not None:   
                            updateadmindata = AdminBasicInformation.query.filter_by(admin_login_id = institution.updated_by).first()
                            if updateadmindata is not None:
                                updated_by = updateadmindata.first_name
                            else :
                                updated_by = 'Admin'
                            
                        entity = EntityType.query.get(institution.entity_id)
                        institution_data = {
                            'id': institution.institution_id,
                            'institution_name': institution.institution_name,
                            'entity_type': entity.entity_type if entity else None,
                            'entity_id': institution.entity_id if entity else None,
                            'address': institution.address,
                            'country': institution.country,
                            'state': institution.state,
                            'city': institution.city,
                            'district': institution.district,
                            'pincode': institution.pincode,
                            'website_url': institution.website_url,
                            'email_id': institution.email_id,
                            'mobile_no': institution.mobile_no,
                            'is_active': institution.is_active,
                            'created_at':institution.created_at,
                            'updated_at':institution.updated_at,
                            'created_by':created_by,
                            'updated_by':updated_by,
                        }
                        institutiones_data.append(institution_data)
                    
                    if not institutiones_data:
         
                        return jsonify({'message': 'No Institution found', 'status': 404})
                    else:
               
                        return jsonify({'message': 'Institutions found Successfully', 'status': 200, 'data': institutiones_data})
                except Exception as e:
                    
      
                    return jsonify({'message': str(e), 'status': 500})
                
            
        @self.institution_ns.route('/add')
        class InstitutionAdd(Resource):
            @self.institution_ns.doc('institution/add', security='jwt')
            @self.api.expect(self.institution_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    institution_name = data.get('institution_name')
                    entity_id = data.get('entity_id')
                    address = data.get('address')
                    country = data.get('country')
                    state = data.get('state')
                    city = data.get('city')
                    district = data.get('district')
                    pincode = data.get('pincode')
                    website_url = data.get('website_url')
                    email_id = data.get('email_id')
                    mobile_no = data.get('mobile_no')
                    current_user_id = get_jwt_identity()
                    if not institution_name :
            
                        return jsonify({'message': 'Please Provide Institution name', 'status': 201})
                  
                    else:
                        existing_institution = Institution.query.filter_by(institution_name=data['institution_name']).first()
                        if existing_institution:
                            
                   
                            return jsonify({'message': 'Institute already exists', 'status': 409})
                        institution = Institution(institution_name=institution_name,entity_id=entity_id,address=address,state=state,country=country,city=city,district=district,pincode=pincode,website_url=website_url,email_id=email_id,mobile_no=mobile_no,is_active=1,created_by=current_user_id)
                        db.session.add(institution)
                        db.session.commit()
                        return jsonify({'message': 'Institution created successfully', 'status': 200,'institution': {
                    'id': institution.institution_id,
                    'institution_name': institution.institution_name
                
                }})
                except Exception as e:
                    db.session.rollback()
      
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.institution_ns.route('/edit/<int:id>')
        class InstitutionEdit(Resource):
            @self.institution_ns.doc('institution/edit', security='jwt')
            @api.expect(self.institution_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    institution_name = data.get('institution_name')
                    entity_id = data.get('entity_id')
                    address = data.get('address')
                    country = data.get('country')
                    state = data.get('state')
                    city = data.get('city')
                    district = data.get('district')
                    pincode = data.get('pincode')
                    website_url = data.get('website_url')
                    email_id = data.get('email_id')
                    mobile_no = data.get('mobile_no')
                    current_user_id = get_jwt_identity()
                    if not institution_name :
       
                        return jsonify({'message': 'Please Provide Institution name', 'status': 201})
                    
                    if not address :
          
                        return jsonify({'message': 'Please Provide Address', 'status': 201})
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
                    
                    if not email_id or not mobile_no:
     
                        return jsonify({'message': 'Please Provide Email Id', 'status': 201})
                    if not mobile_no:
            
                        return jsonify({'message': 'Please Provide Mobile No', 'status': 201})
                    else:
                        institution = Institution.query.get(id)
                        if not institution:
                        
                            return jsonify({'message': 'Institution not found', 'status': 404})
                        else:
                            
                            institution.institution_name = institution_name
                            institution.entity_id = entity_id
                            institution.address = address
                            institution.country = country
                            institution.state = state
                            institution.city = city
                            institution.district = district
                            institution.pincode = pincode
                            institution.website_url = website_url
                            institution.email_id = email_id
                            institution.mobile_no = mobile_no
                            institution.updated_by = current_user_id
                            db.session.commit()
                    
                            return jsonify({'message': 'Institution updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
           
                    return jsonify({'message': str(e), 'status': 500})
                    
            @self.institution_ns.doc('institution/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    institution = Institution.query.get(id)
                    if not institution:
        
                        return jsonify({'message': 'Institution not found', 'status': 404})
                    else:
                        institution_data = {
                            'id': institution.institution_id,
                            'institution_name': institution.institution_name,
                            'entity_id': institution.entity_id,
                            'address': institution.address,
                            'country': institution.country,
                            'state': institution.state,
                            'city': institution.city,
                            'district': institution.district,
                            'pincode': institution.pincode,
                            'website_url': institution.website_url,
                            'email_id': institution.email_id,
                            'mobile_no': institution.mobile_no,
                            'is_active': institution.is_active,
                            'created_at':institution.created_at,
                            'updated_at':institution.updated_at,
                            
                        }
                        print(institution_data)
             
                        return jsonify({'message': 'Institution found Successfully', 'status': 200,'data':institution_data})
                except Exception as e:
      
                    return jsonify({'message': str(e), 'status': 500})
        @self.institution_ns.route('delete/<int:id>')
        class InstitutionDelete(Resource):
            @self.institution_ns.doc('institution/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        institution_entity = Institution.query.get(id)
                        if not institution_entity:
                          
                            return jsonify({'message': 'institution not found', 'status': 404})
                        else:
                            
                            institution_entity.is_deleted=True
                            db.session.commit()
                         
                            return jsonify({'message': 'Institution deleted successfully', 'status': 200})
                    except Exception as e:
  
                        return jsonify({'message': str(e), 'status': 500})
                    
        @self.institution_ns.route('/activate/<int:id>')
        class InstitutionActivate(Resource):
            @self.institution_ns.doc('institution/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    institution = Institution.query.get(id)
                    if not institution:
            
                        return jsonify({'message': 'Institution not found', 'status': 404})

                    institution.is_active = 1
                    db.session.commit()
           
                    return jsonify({'message': 'Institution activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
 
                    return jsonify({'message': str(e), 'status': 500})

        @self.institution_ns.route('/deactivate/<int:id>')
        class InstitutionDeactivate(Resource):
            @self.institution_ns.doc('institution/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:

                    institution = Institution.query.get(id)
                    if not institution:
                        return jsonify({'message': 'Institution not found', 'status': 404})

                    institution.is_active = 0
                    db.session.commit()
             
                    return jsonify({'message': 'Institution deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
 
                    return jsonify({'message': str(e), 'status': 500})


        
        self.api.add_namespace(self.institution_ns)

        