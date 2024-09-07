from datetime import datetime
import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations,logger
from flask_restx import Api, Namespace, Resource, fields
from app.models.adminuser import AdminAddress, AdminBasicInformation, AdminContact, AdminDescription, AdminLanguageKnown, AdminLogin, AdminProfession

class AdminBasicInformationController:
    def __init__(self,api):
        self.api = api
        self.admin_basicinfo_model = api.model('AdminBasicInformation', {
            'department_id': fields.String(required=True, description='Department Id'),
            'first_name': fields.String(required=True, description='Admin First Name'),
            'last_name': fields.String(required=True, description='Admin Last Name'),
            'gender': fields.String(required=True, description='Admin Gender'),
            'dob': fields.Date(required=True, description='Admin Date of Birth'),
            'father_name': fields.String(required=True, description='Admin Father Name'),
            'mother_name': fields.String(required=True, description='Admin Mother Name'),
            'guardian_name': fields.String(required=True, description='Admin Gaurdian Name'),
            'is_kyc_verified': fields.Boolean(required=False, description='Admin KYC verified'),
            'pic_path': fields.String(required=True, description='Admin Pic path'),
            'admin_login_id': fields.String(required=True, description='Admin Login Id')
        })
        self.required_fields = ['department_id', 'first_name', 'last_name', 'gender', 'dob', 'father_name', 'mother_name', 'guardian_name', 'pic_path', 'admin_login_id']
        self.admin_basicinfo_bp = Blueprint('admin_basicinfo', __name__)
        self.admin_basicinfo_ns = Namespace('admin_basicinfo', description='Admin Basic Information Details', authorizations=authorizations)
       
        self.register_routes()

    def calculate_completion_percentage(self, data):
        filled_fields = sum(1 for field in self.required_fields if field in data and data[field])
        total_required_fields = len(self.required_fields)
        return (filled_fields / total_required_fields) * 100 if total_required_fields > 0 else 0    
    def register_routes(self):
        @self.admin_basicinfo_ns.route('/list')
        class AdminBasicInformationList(Resource):
            @self.admin_basicinfo_ns.doc('admin_basicinfo/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    admin_basicinfoes = AdminBasicInformation.query.filter_by(is_active=1).all()
                    admin_basicinfoes_data = []
                    
                    for admin_basicinfo in admin_basicinfoes:
                        admin_basicinfo_data = {
                            'id': admin_basicinfo.admin_id,
                            'department_id': admin_basicinfo.department_id,
                            'first_name': admin_basicinfo.first_name,
                            'last_name': admin_basicinfo.last_name,
                            'gender': admin_basicinfo.gender,
                            'dob': admin_basicinfo.dob,
                            'father_name': admin_basicinfo.father_name,
                            'mother_name': admin_basicinfo.mother_name,
                            'guardian_name': admin_basicinfo.guardian_name,
                            'is_kyc_verified': admin_basicinfo.is_kyc_verified,
                            'pic_path': admin_basicinfo.pic_path,
                            'admin_registration_no': admin_basicinfo.admin_registration_no,
                            'last_modified_datetime': admin_basicinfo.last_modified_datetime,
                            'is_active': admin_basicinfo.is_active,
                        }
                        admin_basicinfoes_data.append(admin_basicinfo_data)
                    
                    if not admin_basicinfoes_data:
                        logger.info('No Admin Basic Information found')
                        return jsonify({'message': 'No Admin Basic Information found', 'status': 404})
                    else:
                        logger.info('Admin Basic Informations found successfully')
                        return jsonify({'message': 'Admin Basic Informations found Successfully', 'status': 200, 'data': admin_basicinfoes_data})
                except Exception as e:
                
                    logger.error(f"Error fetching Admin basic information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.admin_basicinfo_ns.route('/alldata')
        class AdminBasicInformationList(Resource):
            @self.admin_basicinfo_ns.doc('admin_basicinfo/alldata', security='jwt')
            @jwt_required()
            def get(self):
                try:
                    admin_basicinfoes = AdminBasicInformation.query.all()
                    admin_basicinfoes_data = []
                    
                    for admin_basicinfo in admin_basicinfoes:
                        admin_basicinfo_data = {
                            'id': admin_basicinfo.admin_id,
                            'department_id': admin_basicinfo.department_id,
                            'first_name': admin_basicinfo.first_name,
                            'last_name': admin_basicinfo.last_name,
                            'gender': admin_basicinfo.gender,
                            'dob': admin_basicinfo.dob,
                            'father_name': admin_basicinfo.father_name,
                            'mother_name': admin_basicinfo.mother_name,
                            'guardian_name': admin_basicinfo.guardian_name,
                            'is_kyc_verified': admin_basicinfo.is_kyc_verified,
                            'pic_path': admin_basicinfo.pic_path,
                            'admin_registration_no': admin_basicinfo.admin_registration_no,
                            'last_modified_datetime': admin_basicinfo.last_modified_datetime,
                            'is_active': admin_basicinfo.is_active,
                        }
                        admin_basicinfoes_data.append(admin_basicinfo_data)
                    
                    if not admin_basicinfoes_data:
                        logger.info('No Admin Basic Information found')
                        return jsonify({'message': 'No Admin Basic Information found', 'status': 404})
                    else:
                        logger.info('Admin Basic Informations found successfully')
                        return jsonify({'message': 'Admin Basic Informations found Successfully', 'status': 200, 'data': admin_basicinfoes_data})
                except Exception as e:
                
                    logger.error(f"Error fetching Admin basic information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        @self.admin_basicinfo_ns.route('/add')
        class AdminBasicInformationAdd(Resource):
            @self.admin_basicinfo_ns.doc('admin_basicinfo/add', security='jwt')
            @self.api.expect(self.admin_basicinfo_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    last_data =  AdminBasicInformation.query.order_by(AdminBasicInformation.admin_id.desc()).first()
                    last_id = last_data.admin_id if last_data else 0
                    department_id = data.get('department_id')
                    first_name = data.get('first_name')
                    last_name = data.get('last_name')
                    gender = data.get('gender')
                    dob = data.get('dob')
                    father_name = data.get('father_name')
                    mother_name = data.get('mother_name')
                    guardian_name = data.get('guardian_name')
                    is_kyc_verified = data.get('is_kyc_verified')
                    pic_path = data.get('pic_path')
                    admin_login_id = data.get('admin_login_id')
                    today_date = datetime.now().strftime('%Y%m%d')
                    series_number = f"{today_date}{last_id + 1:06d}" 
                    admin_registration_no = series_number
                    current_user_id = get_jwt_identity()
                    
                    if not department_id :
                        logger.warning('Department Id is missing')
                        return jsonify({'message': 'Please Provide Department Id', 'status': 201})
                    if not first_name :
                        logger.warning('First Name is missing')
                        return jsonify({'message': 'Please Provide First Name', 'status': 201})
                    if not last_name :
                        logger.warning('Last Name is missing')
                        return jsonify({'message': 'Please Provide Last Name', 'status': 201})
                    if not gender :
                        logger.warning('gender is missing') 
                        return jsonify({'message': 'Please Provide Gender', 'status': 201})
                    if not dob :
                        logger.warning('Date of Birth is missing')
                        return jsonify({'message': 'Please Provide Date of Birth', 'status': 201})
                    if not father_name :
                        logger.warning('Father Name is missing')
                        return jsonify({'message': 'Please Provide Father Name', 'status': 201})
                    if not mother_name :
                        logger.warning('Mother Name is missing')
                        return jsonify({'message': 'Please Provide Mother Name', 'status': 201})
                 
                    if not admin_login_id:
                        logger.warning('Admin Login Id is missing')
                        return jsonify({'message': 'Please Provide Logged Admin Id', 'status': 201})
                    else:
                        admin_basicinfo = AdminBasicInformation(department_id=department_id,first_name=first_name,last_name=last_name,gender=gender,dob=dob,father_name=father_name,mother_name=mother_name,guardian_name=guardian_name,is_kyc_verified=is_kyc_verified,pic_path=pic_path,admin_registration_no=admin_registration_no,last_modified_datetime=datetime.now(),system_datetime=datetime.now(),is_active=1,created_by=current_user_id,admin_login_id=admin_login_id)
                        db.session.add(admin_basicinfo)
                        db.session.commit()
                        logger.info(f'Admin Basic Information added successfully')
                        return jsonify({'message': 'Admin Basic Information created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error in adding Admin basic information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.admin_basicinfo_ns.route('/edit/<int:id>')
        class AdminBasicInformationEdit(Resource):
            @self.admin_basicinfo_ns.doc('admin_basicinfo/edit', security='jwt')
            @api.expect(self.admin_basicinfo_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    department_id = data.get('department_id')
                    first_name = data.get('first_name')
                    last_name = data.get('last_name')
                    gender = data.get('gender')
                    dob = data.get('dob')
                    father_name = data.get('father_name')
                    mother_name = data.get('mother_name')
                    guardian_name = data.get('guardian_name')
                    is_kyc_verified = data.get('is_kyc_verified')
                    pic_path = data.get('pic_path')
                    admin_login_id = data.get('admin_login_id')
                    current_user_id = get_jwt_identity()
                    if not department_id :
                        logger.warning('Department Id is missing')
                        return jsonify({'message': 'Please Provide Department Id', 'status': 201})
                    if not first_name :
                        logger.warning('first_name is missing')
                        return jsonify({'message': 'Please Provide First Name', 'status': 201})
                    if not last_name :
                        logger.warning('last_name is missing')
                        return jsonify({'message': 'Please Provide Last Name', 'status': 201})
                    if not gender :
                        logger.warning('gender is missing')
                        return jsonify({'message': 'Please Provide Gender', 'status': 201})
                    if not dob :
                        logger.warning('dob is missing')
                        return jsonify({'message': 'Please Provide Date of Birth', 'status': 201})
                    if not father_name :
                        logger.warning('father_name is missing')
                        return jsonify({'message': 'Please Provide Father Name', 'status': 201})
                    if not mother_name :
                        logger.warning('mother_name is missing')
                        return jsonify({'message': 'Please Provide Mother Name', 'status': 201})
                   
                    if not admin_login_id:
                        logger.warning('admin_login_id is missing')
                        return jsonify({'message': 'Please Provide Logged Admin Id', 'status': 201})
                    else:
                        
                        admin_basicinfo = AdminBasicInformation.query.filter_by(admin_login_id=id).first()
                        if not admin_basicinfo:
                            logger.warning('Admin Basic Information not found')
                            return jsonify({'message': 'Admin Basic Information not found', 'status': 404})
                        else:
                            admin_basicinfo.department_id = department_id
                            admin_basicinfo.first_name = first_name
                            admin_basicinfo.last_name = last_name
                            admin_basicinfo.gender = gender
                            admin_basicinfo.dob = dob
                            admin_basicinfo.father_name = father_name
                            admin_basicinfo.mother_name = mother_name
                            admin_basicinfo.guardian_name = guardian_name
                            admin_basicinfo.is_kyc_verified = is_kyc_verified
                            admin_basicinfo.pic_path = pic_path
                            admin_basicinfo.updated_by = current_user_id
                            admin_basicinfo.admin_login_id = admin_login_id
                            db.session.commit()
                            logger.info(f'Admin Basic Information updated successfully with ID: {id}')
                            return jsonify({'message': 'Admin Basic Information updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error editing Admin basic information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                    
            @self.admin_basicinfo_ns.doc('admin_basicinfo/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
              
                    admin_basicinfo = AdminBasicInformation.query.filter_by(admin_login_id=id).first()
                    if not admin_basicinfo:
                        logger.warning(f'Admin Basic Information with ID: {id} not found')
                        return jsonify({'message': 'Admin Basic Information not found', 'status': 404})
                    else:
                        admin_basicinfo_data = {
                            'id': admin_basicinfo.admin_id,
                            'department_id': admin_basicinfo.department_id,
                            'first_name': admin_basicinfo.first_name,
                            'last_name': admin_basicinfo.last_name,
                            'gender': admin_basicinfo.gender,
                            'dob': admin_basicinfo.dob,
                            'father_name': admin_basicinfo.father_name,
                            'mother_name': admin_basicinfo.mother_name,
                            'guardian_name': admin_basicinfo.guardian_name,
                            'is_kyc_verified': admin_basicinfo.is_kyc_verified,
                            'pic_path': admin_basicinfo.pic_path,
                            'admin_registration_no': admin_basicinfo.admin_registration_no,
                            'last_modified_datetime': admin_basicinfo.last_modified_datetime,
                            'is_active': admin_basicinfo.is_active,
                            
                        }
                        print(admin_basicinfo_data)
                        logger.info(f'Adminbasic information retrieved successfully with ID: {id}')
                        return jsonify({'message': 'Admin Basic Information found Successfully', 'status': 200,'data':admin_basicinfo_data})
                except Exception as e:
                   
                    logger.error(f"Error fetching Admin basic information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.admin_basicinfo_ns.route('/getProfile/<int:id>')
        class AdminGetProfile(Resource):
                @self.admin_basicinfo_ns.doc('admin/getProfile', security='jwt')
                @jwt_required()
                def get(self, id):
                    try:
                        admin_login = AdminLogin.query.get(id)
                        admin = AdminBasicInformation.query.filter_by(admin_login_id=id).first()
                        if not admin:
                            logger.warning(f'Admin Basic Information with ID: {id} not found')
                            return jsonify({'message': 'Admin not found', 'status': 404})
                        else:
                            admin_address = AdminAddress.query.filter_by(admin_id=id).order_by(AdminAddress.admin_address_id.desc()).first()
                            admin_description = AdminDescription.query.filter_by(admin_id=id).order_by(AdminDescription.id.desc()).first()
                            admin_profession = AdminProfession.query.filter_by(admin_id=id).order_by(AdminProfession.id.desc()).first()
                            admin_language_known =AdminLanguageKnown.query.filter_by(admin_id=id).order_by(AdminLanguageKnown.id.desc()).first()
                            admin_contact =AdminContact.query.filter_by(admin_id=id).order_by(AdminContact.admin_contact_id.desc()).first()
                            admin_contact_data ={}
                            admin_profession_data ={}
                            admin_description_data ={}
                            admin_address_data ={}
                            admin_language_known_data= {}
                            admin_basic_information_data= {}
                            if admin:
                                admin_basic_information_data = {
                                    'id': admin.admin_id,
                                    'department_id': admin.department_id,
                                    'first_name': admin.first_name,
                                    'last_name': admin.last_name,
                                    'gender': admin.gender,
                                    'dob': admin.dob,
                                    'father_name': admin.father_name,
                                    'mother_name': admin.mother_name,
                                    'guardian_name': admin.guardian_name,
                                    'is_kyc_verified': admin.is_kyc_verified,
                                    'pic_path': admin.pic_path,
                                    'admin_registration_no': admin.admin_registration_no,
                                    'last_modified_datetime': admin.last_modified_datetime,
                                    'is_active': admin.is_active,
                                    
                                }
                            if admin_address:
                                admin_address_data = {
                                    'id': admin_address.admin_address_id,
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
                            if admin_description:
                                admin_description_data = {
                                    'id': admin_description.id,
                                    'admin_id': admin_description.admin_id,
                                    'description': admin_description.description,
                                    'is_active': admin_description.is_active,
                                }
                            if admin_profession:
                                admin_profession_data = {
                                    'id': admin_profession.id,
                                    'admin_id': admin_profession.admin_id,
                                    'institution_id': admin_profession.institution_id,
                                    'course_id':admin_profession.course_id,
                                    'subject_id': admin_profession.subject_id, 
                                    'is_active': admin_profession.is_active  
                                } 
                            if admin_language_known : 
                                admin_language_known_data = {
                                    'id': admin_language_known.id,
                                    'admin_id': admin_language_known.admin_id,
                                    'language_id': admin_language_known.language_id,
                                    'proficiency': admin_language_known.proficiency,
                                    'is_active': admin_language_known.is_active
                                }
                            if admin_contact :
                                admin_contact_data = {
                                    'id': admin_contact.admin_contact_id,
                                    'admin_id': admin_contact.admin_id,
                                    'mobile_isd_call': admin_contact.mobile_isd_call,
                                    'mobile_no_call': admin_contact.mobile_no_call,
                                    'mobile_isd_watsapp': admin_contact.mobile_isd_watsapp,
                                    'mobile_no_watsapp': admin_contact.mobile_no_watsapp,  
                                    'email_id': admin_contact.email_id,
                                    'is_active': admin_contact.is_active
                                }
                            admin_data = {
                                'id': admin.admin_id,
                                'department_id': admin.department_id,
                                'first_name': admin.first_name,
                                'last_name': admin.last_name,
                                'gender': admin.gender,
                                'dob': admin.dob,
                                'father_name': admin.father_name,
                                'mother_name': admin.mother_name,
                                'guardian_name': admin.guardian_name,
                                'is_kyc_verified': admin.is_kyc_verified,
                                'pic_path': admin.pic_path,
                                'admin_registration_no': admin.admin_registration_no,
                                'last_modified_datetime': admin.last_modified_datetime,
                                'is_active': admin.is_active,
                                'address':admin_address_data,
                                'admin_description':admin_description_data,
                                'profession':admin_profession_data,
                                'language_known':admin_language_known_data,
                                'contact':admin_contact_data,
                                'basic_info':admin_basic_information_data,
                                'userid':admin_login.userid
                            }
                            logger.info(f'Admin Profile retrieved successfully with ID: {id}')
                            return jsonify({'message': 'Admin found Successfully', 'status': 200,'data':admin_data}) 
                    except Exception as e:
                    
                        logger.error(f"Error in adding Admin basic information: {str(e)}")
                        return jsonify({'message': str(e), 'status': 500})
                        
        @self.admin_basicinfo_ns.route('/activate/<int:id>')
        class AdminBasicInformationActivate(Resource):
            @self.admin_basicinfo_ns.doc('admin_basicinfo/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    admin_basicinfo = AdminBasicInformation.query.get(id)
                    if not admin_basicinfo:
                        logger.warning(f'Admin Basic Information with ID: {id} not found')
                        return jsonify({'message': 'Admin Basic Information not found', 'status': 404})
                    else:
                        admin_basicinfo.is_active = 1
                        db.session.commit()
                        logger.info(f'Admin Basic Information activated successfully with ID: {id}')
                        return jsonify({'message': 'Admin Basic Information activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error activating Admin basic information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.admin_basicinfo_ns.route('/deactivate/<int:id>')
        class AdminBasicInformationDeactivate(Resource):
            @self.admin_basicinfo_ns.doc('admin_basicinfo/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    admin_basicinfo = AdminBasicInformation.query.get(id)
                    if not admin_basicinfo:
                        logger.warning(f'Admin Basic Information with ID: {id} not found')
                        return jsonify({'message': 'Admin Basic Information not found', 'status': 404})
                    else:
                        admin_basicinfo.is_active = 0
                        db.session.commit()
                        logger.info(f'Admin Basic Information deactivated successfully with ID: {id}')
                        return jsonify({'message': 'Admin Basic Information deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error deactivating Admin basic information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        self.api.add_namespace(self.admin_basicinfo_ns)