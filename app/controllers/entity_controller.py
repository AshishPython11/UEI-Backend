from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db,app,api,authorizations,logger
from flask_restx import  Api, Namespace, Resource, fields
from app.models.adminuser import AdminBasicInformation, EntityType
from sqlalchemy import desc
class EntityController:
    def __init__(self,api):
        self.api = api
        self.entity_model = self.api.model('Entity', {
            'entity_type': fields.String(required=True, description='Entity Type'),
        })

        self.entity_ns = Namespace('entity', description='Entity Data', authorizations=authorizations)
        self.entity_bp = Blueprint('entity', __name__)
        
        self.register_routes()
   

        
    def register_routes(self):
        @self.entity_ns.route('/list')
        class EntityList(Resource):
            @self.entity_ns.doc('entity/list', security='jwt')
            @jwt_required()
            def get(self):
                try:

                    entityes = EntityType.query.filter_by(is_deleted=False).order_by(desc(EntityType.updated_at)).all()
                    entityes_data = []
                    
                    for entity in entityes:
                        created_by = 'Admin'
                        updated_by = 'Admin'
                        if entity.created_by is not None:
                            createadmindata = AdminBasicInformation.query.filter_by(admin_login_id = entity.created_by).first()
                            if createadmindata is not None:
                                created_by = createadmindata.first_name
                            else :
                                created_by = 'Admin'
                        if entity.updated_by is not None:   
                            updateadmindata = AdminBasicInformation.query.filter_by(admin_login_id = entity.updated_by).first()
                            if updateadmindata is not None:
                                updated_by = updateadmindata.first_name
                            else :
                                updated_by = 'Admin'
                        entity_data = {
                            'id': entity.entity_id,
                            'entity_type': entity.entity_type,
                            'is_active': entity.is_active,
                            'created_at':entity.created_at,
                            'updated_at':entity.updated_at,
                            'created_by':created_by,
                            'updated_by':updated_by,
                        }
                        entityes_data.append(entity_data)
                    
                    if not entityes_data:
                        logger.info('No Entity found')
                        return jsonify({'message': 'No Entity found', 'status': 404})
                    else:
                        logger.info('Entities found successfully')
                        return jsonify({'message': 'Entities found Successfully', 'status': 200, 'data': entityes_data})
                except Exception as e:
                    
                    logger.error(f"Error fetching entity information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                
        
        @self.entity_ns.route('/add')
        class EntityAdd(Resource):
            @self.entity_ns.doc('entity/add', security='jwt')
            @self.api.expect(self.entity_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    entity_type = data.get('entity_type')
                    current_user_id = get_jwt_identity()
                    print(data)
                    if not entity_type :
                        logger.warning('Entity type not provided')
                        return jsonify({'message': 'Please Provide Entity type','status':201})
                    else:
                        existing_entity = EntityType.query.filter_by(entity_type=entity_type).first()

                        if existing_entity:
                            logger.warning('Entity type already exists')
                            return jsonify({'message': 'Entity already exists', 'status': 409})
                        entity =  EntityType(entity_type=entity_type,is_active=1,created_by=current_user_id)
                        db.session.add(entity)
                        db.session.commit()
                        logger.info('Entity created successfully')
                        return jsonify({'message': 'Entity created successfully','status':200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error adding entity information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        @self.entity_ns.route('/edit/<int:id>')
        class EntityEdit(Resource):
            @self.entity_ns.doc('entity/edit', security='jwt')
            @self.entity_ns.expect(self.entity_model)
            @jwt_required()
            def put(self, id):
                try:
                    data = request.json
                    entity_type = data.get('entity_type')
                    current_user_id = get_jwt_identity()
                    if not entity_type:
                        logger.warning('Entity type not provided')
                        return jsonify({'message': 'Please provide entity type', 'status': 400})
                    else:
                        entity = EntityType.query.get(id)
                    if not entity:
                        return jsonify({'message': 'Entity not found', 'status': 404})
                    else:
                        existing_entity = EntityType.query.filter_by(entity_type=entity_type).first()
                        if existing_entity:
                            logger.warning('Entity type already exists')
                            return jsonify({'message': 'Entity already exists', 'status': 409})
                        entity.entity_type = entity_type
                        entity.updated_by  = current_user_id
                        db.session.commit()
                        logger.info('Entity updated successfully')
                        return jsonify({'message': 'Entity updated successfully', 'status':200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error editing entity information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                         
            @self.entity_ns.doc('entity/get', security='jwt')
            @jwt_required()
            def get(self, id):
                try:
                    entity = EntityType.query.get(id)  
                    if not entity:
                        logger.warning('Entity type not provided')
                        return jsonify({'message': 'Entity not found', 'status': 404})
                    else:
                        entity_data = {
                            'id': entity.entity_id,
                            'entity_type': entity.entity_type,
                            'is_active': entity.is_active,
                            'created_at':entity.created_at,
                            'updated_at':entity.updated_at,
                        }
                        logger.info('Entity found successfully')
                        return jsonify({'message': 'Entity found Successfully', 'status': 200,'data':entity_data})
                except Exception as e:
                    
                    logger.error(f"Error fetching entity information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
        @self.entity_ns.route('delete/<int:id>')
        class EntityDelete(Resource):
            @self.entity_ns.doc('entity/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
                        form_entity = EntityType.query.get(id)
                        if not form_entity:
                            logger.warning('Entity type not provided')
                            return jsonify({'message': 'entity not found', 'status': 404})
                        else:
                            # form_entity.is_active = 0
                            form_entity.is_deleted=True
                            db.session.commit()
                            logger.info('Entity deleted successfully')
                            return jsonify({'message': 'Entity deleted successfully', 'status': 200})
                    except Exception as e:
                        
                        logger.error(f"Error DELETING entity information: {str(e)}")
                        return jsonify({'message': str(e), 'status': 500})
                    
        @self.entity_ns.route('/activate/<int:id>')
        class EntityActivate(Resource):
            @self.entity_ns.doc('entity/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    entity = EntityType.query.get(id)
                    if not entity:
                        logger.warning('Entity type not provided')
                        return jsonify({'message': 'Entity not found', 'status': 404})
                    else:
                        entity.is_active = 1
                        
                        db.session.commit()
                        logger.info('Entity activated successfully')
                        return jsonify({'message': 'Entity activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error activating entity information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})

        @self.entity_ns.route('/deactivate/<int:id>')
        class EntityDeactivate(Resource):
            @self.entity_ns.doc('entity/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    entity = EntityType.query.get(id)
                    if not entity:
                        logger.warning('Entity type not provided')
                        return jsonify({'message': 'Entity not found', 'status': 404})
                    else:
                        entity.is_active = 0
                        db.session.commit()
                        logger.info('Entity deactivated successfully')
                        return jsonify({'message': 'Entity deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error deactivating entity information: {str(e)}")
                    return jsonify({'message': str(e), 'status': 500})
                

        self.api.add_namespace(self.entity_ns)