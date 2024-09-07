import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations,logger
from flask_restx import Api, Namespace, Resource, fields
from app.models.adminuser import AdminBasicInformation, LanguageMaster
from sqlalchemy import desc
class LanguageController:
    def __init__(self,api):
        self.api = api
        self.language_model = api.model('Language', {
            'language_name': fields.String(required=True, description='Language Name'),
        })
        
        self.language_bp = Blueprint('language', __name__)
        self.language_ns = Namespace('language', description='Language Details', authorizations=authorizations)
        
       
        self.register_routes()

        
    def register_routes(self):
        @self.language_ns.route('/list')
        class LanguageList(Resource):
            @self.language_ns.doc('language/list', security='jwt')
            @jwt_required()
            def get(self):
                try:
             
                    languagees = LanguageMaster.query.filter_by(is_deleted=False).order_by(desc(LanguageMaster.updated_at)).all()
                    languagees_data = []
                    
                    for language in languagees:
                        created_by = 'Admin'
                        updated_by = 'Admin'
                        if language.created_by is not None:
                            createadmindata = AdminBasicInformation.query.filter_by(admin_login_id = language.created_by).first()
                            if createadmindata is not None:
                                created_by = createadmindata.first_name
                            else :
                                created_by = 'Admin'
                        if language.updated_by is not None:   
                            updateadmindata = AdminBasicInformation.query.filter_by(admin_login_id = language.updated_by).first()
                            if updateadmindata is not None:
                                updated_by = updateadmindata.first_name
                            else :
                                updated_by = 'Admin'
                        language_data = {
                            'id': language.language_id,
                            'language_name': language.language_name,
                            'description':language.description,
                            'icon':language.icon,
                            'is_active': language.is_active,
                            'is_deleted': language.is_deleted, 
                            'created_at':language.created_at,
                            'updated_at':language.updated_at,
                            'created_by':created_by,
                            'updated_by':updated_by,
                        }
                        languagees_data.append(language_data)
                    
                    if not languagees_data:
                        logger.warning("No languages found")
                        return jsonify({'message': 'No Language found', 'status': 404})
                    else:
                        logger.info("Languages fetched successfully")
                        return jsonify({'message': 'Languages found Successfully', 'status': 200, 'data': languagees_data})
                except Exception as e:
                    
                    logger.error(f"Error fetching language information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        @self.language_ns.route('/add')
        class LanguageAdd(Resource):
            @self.language_ns.doc('language/add', security='jwt')
            @self.api.expect(self.language_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    language_name = data.get('language_name')
                    description = data.get('description')
                    icon = data.get('icon')
                    current_user_id = get_jwt_identity()
                    if not language_name:
                        logger.warning("No languages name found")
                        return jsonify({'message': 'Please Provide Language name', 'status': 201})
                    else:
                        language = LanguageMaster(language_name=language_name,description=description,icon=icon,is_active=1,created_by=current_user_id)
                        db.session.add(language)
                        db.session.commit()
                        logger.info("Languages created successfully")
                        return jsonify({'message': 'Language created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error adding language information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.language_ns.route('/edit/<int:id>')
        class LanguageEdit(Resource):
            @self.language_ns.doc('language/edit', security='jwt')
            @api.expect(self.language_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    language_name = data.get('language_name')
                    description = data.get('description')
                    icon = data.get('icon')
                    current_user_id = get_jwt_identity()
                    if not language_name:
                        logger.warning("No languages name found")
                        return jsonify({'message': 'Please provide language name', 'status': 400})
                    else:
                        language = LanguageMaster.query.get(id)
                        if not language:
                            logger.warning("No languages found")
                            return jsonify({'message': 'Language not found', 'status': 404})
                        else:
                            language.language_name = language_name
                            language.description = description
                            language.icon = icon
                            language.updated_by = current_user_id
                            db.session.commit()
                            logger.info("Languages updated successfully")
                            return jsonify({'message': 'Language updated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error aditing language information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                    
            @self.language_ns.doc('language/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    language = LanguageMaster.query.get(id)
                    if not language:
                        logger.warning("No languages found")
                        return jsonify({'message': 'Language not found', 'status': 404})
                    else:
                        language_data = {
                            'id': language.language_id,
                            'language_name': language.language_name,
                            'is_active': language.is_active,
                            'is_deleted': language.is_deleted, 
                            'created_at':language.created_at,
                            'updated_at':language.updated_at,
                        }
                        print(language_data)
                        logger.info("Languages found successfully")
                        return jsonify({'message': 'Language found Successfully', 'status': 200,'data':language_data})
                except Exception as e:
                   
                    logger.error(f"Error fetching language information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.language_ns.route('delete/<int:id>')
        class LanguageDelete(Resource):
            @self.language_ns.doc('language/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        language_entity = LanguageMaster.query.get(id)
                        if not language_entity:
                            logger.warning("No languages entity found")
                            return jsonify({'message': 'Language not found', 'status': 404})
                        else:
                          
                            language_entity.is_deleted=True
                            db.session.commit()
                            logger.info("Languages deleted successfully")
                            return jsonify({'message': 'Language deleted successfully', 'status': 200})
                    except Exception as e:
                        
                        logger.error(f"Error deleting language information: {str(e)}")
                        return jsonify({'message': str(e), 'status': 500})
                    
        @self.language_ns.route('/activate/<int:id>')
        class LanguageActivate(Resource):
            @self.language_ns.doc('language/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    language = LanguageMaster.query.get(id)
                    if not language:
                        logger.warning("No languages found")
                        return jsonify({'message': 'Language not found', 'status': 404})

                    language.is_active = 1
                    db.session.commit()
                    logger.info("Languages activated successfully")
                    return jsonify({'message': 'Language activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error activating language information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.language_ns.route('/deactivate/<int:id>')
        class LanguageDeactivate(Resource):
            @self.language_ns.doc('language/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    language = LanguageMaster.query.get(id)
                    if not language:
                        logger.warning("No languages found")
                        return jsonify({'message': 'Language not found', 'status': 404})

                    language.is_active = 0
                    db.session.commit()
                    logger.info("Languages deactivated successfully")
                    return jsonify({'message': 'Language deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error deactivating language information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})


        
        self.api.add_namespace(self.language_ns)