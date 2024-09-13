import json
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from app import db, api, authorizations
from flask_restx import Api, Namespace, Resource, fields
from app.models.chatbot import ChatData,CustomChatData
from app.models.student import Student, StudentLogin
class ChatbotController:
    def __init__(self,api):
        self.api = api
        self.chatbot_model = api.model('Chatbot', {
            'student_id': fields.String(required=True, description='student_id'),
            'chat_question': fields.String(required=True, description='Question'),
            'response': fields.String(required=True, description='Response'),
        })
        self.custom_chatdata=api.model('CustomChatData', {
                'student_id': fields.Integer(required=True, description='Student ID'),
                'chat_title': fields.String(required=True, description='Chat Title'),
                'chat_conversation': fields.String(required=True, description='Chat Conversation'),
               
            })
        
        self.chatbot_bp = Blueprint('Chatbot', __name__)
        self.chatbot_ns = Namespace('Chatbot', description='Chatbot Details', authorizations=authorizations)
        self.register_routes()
    
        
    def register_routes(self):
        @self.chatbot_ns.route('/list_based_on_id/<int:student_id>')
        class ChatbotList(Resource):
            @self.chatbot_ns.doc('Chatbot/list_based_on_id', security='jwt')
            @jwt_required()
            def get(self, student_id):
                try:
        
                    chatbot_query = CustomChatData.query.filter_by(is_deleted=False,student_id=student_id).all()
                    chatbot_data_list = []
                    
                    for chatbot in chatbot_query:
                        chatbot_data = {
                            'id':chatbot.id,
                            'student_id': chatbot.student_id,
                            'chat_title': chatbot.chat_title,
                            'chat_conversation': chatbot.chat_conversation,
                            'flagged': chatbot.flagged,
                            'created_at': chatbot.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'updated_at': chatbot.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                            
                        }
                        chatbot_data_list.append(chatbot_data)
                    
                    if not chatbot_data_list:
              
                        return jsonify({'message': 'No Chat found', 'status': 404})
                    else:
                       
                        return jsonify({'message': 'Chat found Successfully', 'status': 200, 'data': chatbot_data_list})
                except Exception as e:

                        return jsonify({'message': str(e), 'status': 500})
        @self.chatbot_ns.route('/getalldata')
        class ChatbotList(Resource):
            @self.chatbot_ns.doc('Chatbot/getalldata', security='jwt')
            @jwt_required()
            def get_student_name(self, student_id):
        
                student = Student.query.get(student_id)
                return f"{student.first_name} {student.last_name}" if student else None
            def get(self):
                try:
           
                    chatbot_query = CustomChatData.query.filter_by(is_deleted=False).all()
                    chatbot_data_list = []
                    
                    for chatbot in chatbot_query:
                    
                        student_name = self.get_student_name(chatbot.student_id)
                        if not student_name:
                            student_name = "Unknown"
                        
                        chatbot_data = {
                            'student_name': student_name,
                            'chat_title': chatbot.chat_title,
                            'chat_conversation': chatbot.chat_conversation,
                  
                            'created_at': chatbot.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                            'updated_at': chatbot.updated_at.strftime('%Y-%m-%d %H:%M:%S')
                        }
                        chatbot_data_list.append(chatbot_data)
                    
                    if not chatbot_data_list:
             
                        return jsonify({'message': 'No Chat found', 'status': 404})
                    else:
                   
                        return jsonify({'message': 'Chat found Successfully', 'status': 200, 'data': chatbot_data_list})
                except Exception as e:
               
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.chatbot_ns.route('/add')
        class ChatbotAdd(Resource):
            @self.chatbot_ns.doc('Chatbot/add', security='jwt')
            @self.api.expect(self.chatbot_model)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    student_id = data.get('student_id')               
                    chat_question = data.get('chat_question')
                    response = data.get('response')
                    if not student_id :
         
                        return jsonify({'message': 'Please Provide student_id', 'status': 201})
                    else:
                        Chat = ChatData(student_id=student_id,chat_question=chat_question,response=response)
                        db.session.add(Chat)
                        db.session.commit()
                   
                        return jsonify({'message': 'Chat created successfully', 'status': 200})
                except Exception as e:
                        db.session.rollback()
                
                        return jsonify({'message': str(e), 'status': 500})
        @self.chatbot_ns.route('/delete/<int:id>')
        class ChatbotDelete(Resource):
            @self.chatbot_ns.doc('Chatbot/delete', security='jwt')
            @jwt_required()
            def delete(self, id):
                    try:
               
                        chatbot_entity = CustomChatData.query.get(id)
                        if not chatbot_entity:
                     
                            return jsonify({'message': 'Chat History not found', 'status': 404})
                        else:
                   
                            chatbot_entity.is_deleted=True
                            db.session.commit()
                        
                            return jsonify({'message': 'Chatbot activated successfully', 'status': 200})
                    except Exception as e:
                       
         
                        return jsonify({'message': str(e), 'status': 500})
                    
        @self.chatbot_ns.route('/activate/<int:id>')
        class ChatbotActivate(Resource):
            @self.chatbot_ns.doc('Chatbot/activate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    chatbot = ChatData.query.get(id)
                    if not chatbot:
           
                        return jsonify({'message': 'Chatbot not found', 'status': 404})
                    else:
                        chatbot.is_active = 1
                        db.session.commit()
                   
                        return jsonify({'message': 'Chatbot activated successfully', 'status': 200})
                except Exception as e:
                        db.session.rollback()
                  
                        return jsonify({'message': str(e), 'status': 500})

        @self.chatbot_ns.route('/deactivate/<int:id>')
        class ChatbotDeactivate(Resource):
            @self.chatbot_ns.doc('Chatbot/deactivate', security='jwt')
            @jwt_required()
            def put(self, id):
                try:
                    chatbot = ChatData.query.get(id)
                    if not chatbot:
                       
                        return jsonify({'message': 'Chatbot not found', 'status': 404})
                    else:
                        chatbot.is_active = 0
                    
                        db.session.commit()
                 
                        return jsonify({'message': 'Chatbot deactivated successfully', 'status': 200})
                except Exception as e:
                        db.session.rollback()

                        return jsonify({'message': str(e), 'status': 500})
                
        @self.chatbot_ns.route('/chat_data_store')
        class ChatDataAdd(Resource):
            @self.chatbot_ns.doc('ChatData/chat_data_store', security='jwt')
            @self.chatbot_ns.expect(self.custom_chatdata)
            @jwt_required()
            def post(self):
                try:
                    data = request.json
                    student_id = data.get('student_id')
                    chat_title = data.get('chat_title')
                    chat_conversation = data.get('chat_conversation')
                    flagged = data.get('flagged', True)
                    if not student_id or not chat_title or not chat_conversation:
            
                        return jsonify({'message': 'Please provide all required fields: student_id, chat_title, chat_conversation', 'status': 400})

                    student_login = StudentLogin.query.filter_by(student_id=student_id).first()

                    if not student_login:
                        return jsonify({'message': f'Student with ID {student_id} not found', 'status': 404})
                    login_id = student_login.student_id
                    chat_data = CustomChatData(student_id=login_id, chat_title=chat_title, chat_conversation=chat_conversation,flagged=flagged)
                    db.session.add(chat_data)
                    db.session.commit()
         
                    return jsonify({'message': 'Chat data created successfully', 'status': 200})
                except Exception as e:
            
                    return jsonify({'message': str(e), 'status': 500})


                
        self.api.add_namespace(self.chatbot_ns)