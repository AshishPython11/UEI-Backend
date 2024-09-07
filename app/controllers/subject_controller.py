from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db,app,api,authorizations,logger
from flask_restx import  Api, Namespace, Resource, fields
from app.models.adminuser import AdminBasicInformation, SubjectMaster
from sqlalchemy import desc
class SubjectController:
    def __init__(self,api):
        self.api = api
        self.subject_model = self.api.model('Subject', {
            'subject_name': fields.String(required=True, description='Subject Name'),
        })

        self.subject_ns = Namespace('subject', description='Subject Data', authorizations=authorizations)
        self.subject_bp = Blueprint('subject', __name__)
        
        self.register_routes()
 

        
    def register_routes(self):
        @self.subject_ns.route('/list')
        class SubjectList(Resource):
            @self.subject_ns.doc('subject/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
               
                    subjects = SubjectMaster.query.filter_by(is_deleted=False).order_by(desc(SubjectMaster.updated_at)).all()
                    subjects_data = []
                    
                    for subject in subjects:
                        created_by = 'Admin'
                        updated_by = 'Admin'
                        if subject.created_by is not None:
                            createadmindata = AdminBasicInformation.query.filter_by(admin_login_id = subject.created_by).first()
                            if createadmindata is not None:
                                created_by = createadmindata.first_name
                            else :
                                created_by = 'Admin'
                        if subject.updated_by is not None:   
                            updateadmindata = AdminBasicInformation.query.filter_by(admin_login_id = subject.updated_by).first()
                            if updateadmindata is not None:
                                updated_by = updateadmindata.first_name
                            else :
                                updated_by = 'Admin'
                        subject_data = {
                            'id': subject.subject_id,
                            'subject_name': subject.subject_name,
                            'is_active': subject.is_active,
                            'is_deleted': subject.is_deleted, 
                            'created_at':subject.created_at,
                            'updated_at':subject.updated_at,
                            'created_by':created_by,
                            'updated_by':updated_by,
                        }
                        subjects_data.append(subject_data)
                    
                    if not subjects_data:
                        logger.warning("Subject not found")
                        return jsonify({'message': 'No Subject found', 'status': 404})
                    else:
                        logger.info("Subjects found Successfully")
                        return jsonify({'message': 'Subjects found Successfully', 'status': 200, 'data': subjects_data})
                except Exception as e:
                  
                    logger.error(f"Error fetching subject information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.subject_ns.route('/add')
        class SubjectAdd(Resource):
            @self.subject_ns.doc('subject/add', security='jwt')
            @self.api.expect(self.subject_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    subject_name = data.get('subject_name')
                    current_user_id = get_jwt_identity()
                    print(data)
                    if not subject_name :
                        logger.warning("Subject name not found")
                        return jsonify({'message': 'Please Provide Subject name','status':201})
                    else:
                        existing_subject = SubjectMaster.query.filter_by(subject_name=subject_name).first()

                        if existing_subject:
                            logger.warning("Subject already exists")
                            return jsonify({'message': 'Subject already exists', 'status': 409})
                        subject =  SubjectMaster(subject_name=subject_name,is_active = 1,created_by=current_user_id)
                        db.session.add(subject)
                        db.session.commit()
                        logger.info("Subjects created Successfully")
                        return jsonify({'message': 'Subject created successfully','status':200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error adding subject information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                    
        @self.subject_ns.route('/edit/<int:id>')
        class SubjectEdit(Resource):
            @self.subject_ns.doc('subject/edit', security='jwt')
            @self.subject_ns.expect(self.subject_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    subject_name = data.get('subject_name')
                    current_user_id = get_jwt_identity()
                    if not subject_name:
                        logger.warning("Subject name not found")
                        return jsonify({'message': 'Please provide subject name', 'status': 400})
                    else:
                        subject = SubjectMaster.query.get(id)
                    if not subject:
                        logger.warning("Subject not found")
                        return jsonify({'message': 'Subject not found', 'status': 404})
                    else:
                        existing_subject = SubjectMaster.query.filter_by(subject_name=subject_name).first()

                        if existing_subject:
                            logger.warning("Subject already exists")
                            return jsonify({'message': 'Subject already exists', 'status': 409})
                        subject.subject_name = subject_name
                        subject.updeted_by = current_user_id
                        db.session.commit()
                        logger.info("Subjects updated Successfully")
                        return jsonify({'message': 'Subject updated successfully', 'status':200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error editing subject information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                         
            @self.subject_ns.doc('subject/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    subject = SubjectMaster.query.get(id) 
                    if not subject:
                        logger.warning("Subject not found")
                        return jsonify({'message': 'Subject not found', 'status': 404})
                    else: 
                        subject_data = {
                            'id': subject.subject_id,
                            'subject_name': subject.subject_name,
                            'is_active': subject.is_active,
                            'is_deleted': subject.is_deleted, 
                            'created_at':subject.created_at,
                            'updated_at':subject.updated_at,
                        }
                        logger.info("Subjects found Successfully")
                        return jsonify({'message': 'Subject found Successfully', 'status': 200,'data':subject_data})
                except Exception as e:
                    
                    logger.error(f"Error fetching subject information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
            
        @self.subject_ns.route('delete/<int:id>')
        class SubMenuDelete(Resource):
            @self.subject_ns.doc('subject/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        subject_entity = SubjectMaster.query.get(id)
                        if not subject_entity:
                            logger.warning("Subject not found")
                            return jsonify({'message': 'Subject not found', 'status': 404})
                        else:
                            
                            subject_entity.is_deleted=True
                            db.session.commit()
                            logger.info("Subjects deleted Successfully")
                            return jsonify({'message': 'Subject deleted successfully', 'status': 200})
                    except Exception as e:
                      
                        logger.error(f"Error delelting subject information: {str(e)}")
                        return jsonify({'message': str(e), 'status': 500})
                    
        @self.subject_ns.route('/activate/<int:id>')
        class SubjectActivate(Resource):
            @self.subject_ns.doc('subject/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    subject = SubjectMaster.query.get(id)
                    if not subject:
                        logger.warning("Subject not found")
                        return jsonify({'message': 'Subject not found', 'status': 404})

                    subject.is_active = 1
                    db.session.commit()
                    logger.info("Subjects activated Successfully")
                    return jsonify({'message': 'Subject activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error activating subject information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        @self.subject_ns.route('/deactivate/<int:id>')
        class SubjectDeactivate(Resource):
            @self.subject_ns.doc('subject/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    subject = SubjectMaster.query.get(id)
                    if not subject:
                        logger.warning("Subject not found")
                        return jsonify({'message': 'Subject not found', 'status': 404})

                    subject.is_active = 0
                    db.session.commit()
                    logger.info("Subjects deactivated Successfully")
                    return jsonify({'message': 'Subject deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error deactivating subject information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                

        self.api.add_namespace(self.subject_ns)