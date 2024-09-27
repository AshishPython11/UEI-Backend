from datetime import datetime,timedelta
import random
import os
from flask import Blueprint, render_template, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from app.models.student import StudentLogin
from app.models.adminuser import AdminLogin
from app.models.log import ChangePwdLog,LoginLog
from flask_restx import Api, Namespace, Resource, fields
from app import db,api,authorizations,app
import jwt
from flask_jwt_extended import JWTManager,jwt_required, unset_jwt_cookies
from flask_mail import Mail, Message
import string
import json
import secrets
mail = Mail(app)

class AuthController:
    def __init__(self,api):
        self.api = api
        self.signup_model = api.model('Signup', {
            'userid': fields.String(required=True, description='User ID'),
            'password': fields.String(required=True, description='Password'),
            'user_type': fields.String(required=True, description='User type (student or admin)')
        })

        self.login_model = api.model('Login', {
            'userid': fields.String(required=True, description='User ID'),
            'password': fields.String(required=True, description='Password'),
            'user_type': fields.String(required=True, description='User type (student or admin)')
        }) 
        self.forgotpassword_model = api.model('Forgotpassword', {
            'email': fields.String(required=True, description='Email'),
            'user_type': fields.String(required=True, description='User type (student or admin)')
        }) 
        self.change_password_model = api.model('ChangePasswordModel', {
            'email': fields.String(required=True, description='User Email'),
            'old_password': fields.String(required=True, description='Old Password'),
            'new_password': fields.String(required=True, description='New Password'),
            'user_type': fields.String(required=True, description='User type (student or admin)')
        })  
        self.reset_password_model = api.model('ResetPasswordModel', {
            'email': fields.String(required=True, description='User Email'),
            'new_password': fields.String(required=True, description='New Password'),
            'conf_password': fields.String(required=True, description='Confirm Password'),
            'user_type': fields.String(required=True, description='User type (student or admin)')
        })  
        self.auth_bp = Blueprint('auth', __name__)
        self.auth_ns = Namespace('auth', description='Authentication operations', authorizations=authorizations)
       
        self.register_routes()
    
        # Function to send reset password email
    def register_routes(self):
        @self.auth_ns.route('/signup')
        class Signup(Resource):
            @self.auth_ns.doc('signup')
            @self.api.expect(self.signup_model)
           

            def send_change_password_email(self, email, password):
                reset_password_link = f"https://qaweb.gyansetu.ai/changepassword?email={email}&password={password}"
                html_content = render_template('forgotpassword.html', reset_password_link=reset_password_link)
                msg = Message('Reset Your Password', sender=app.config.get('MAIL_USERNAME'), recipients=[email])
                msg.html = html_content
                try:
                    mail.send(msg)
                    print(f"Change password email sent successfully to {email}")
                except Exception as e:
                    print(f"Failed to send change password email to {email}. Error: {e}")

            def send_registration_email(self, email):
                msg = Message('Welcome to Our Platform', sender=app.config.get('MAIL_USERNAME'), recipients=[email])
                msg.body = f"Hello,\n\nThank you for registering with us. Your account is now active.\n\nBest regards,\nYour GyansetuTeam"
                try:
                    mail.send(msg)
                    print(f"Registration email sent successfully to {email}")
                except Exception as e:
                    print(f"Failed to send registration email to {email}. Error: {e}")
            @self.api.expect(self.signup_model)
            def post(self):
                try:
                    data = request.json
                    userid = data.get('userid')
                    password = data.get('password')
                    if not userid or not password:
                        return jsonify({'message': 'Userid and password are required', 'status': 400})
                    
                    otp = random.randint(1000, 9999)
                    
                    if data.get('user_type') == 'student':
                        if StudentLogin.query.filter_by(userid=userid, is_active=1).first():
                           
                            return jsonify({'message': 'Userid already exists', 'status': 400})
                        
                        new_user = StudentLogin(userid=userid, password=generate_password_hash(password), is_active=1, otp=otp)
                        user_type = 'student'

                    elif data.get('user_type') == 'admin':
                        if AdminLogin.query.filter_by(userid=userid).first():
                           
                            return jsonify({'message': 'Userid already exists', 'status': 400})
                        
                        new_user = AdminLogin(userid=userid, password=generate_password_hash(password), is_active=1, otp=otp)
                        user_type = 'admin'

                    else:
                        return jsonify({'message': 'Invalid user type', 'status': 400})
                    
                    try:
                        db.session.add(new_user)
                        db.session.commit()
           
                        
                    except Exception as e:
         
                        return jsonify({'message': 'Failed to register user', 'status': 500})
                    
                    if user_type == 'student':
                        self.send_registration_email(userid)
                    elif user_type == 'admin':
                        self.send_change_password_email(userid, password)
                    
                    return jsonify({'message': 'User created successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
       
                    return jsonify({'message': str(e), 'status': 500})
               
        @self.auth_ns.route('/login')
        class Login(Resource):
            @self.auth_ns.doc('login')
            @self.api.expect(self.login_model)
            def post(self):
                
                try:
                    data = request.json
                    userid = data.get('userid')
                    password = data.get('password')

                    if not userid or not password:
                        return jsonify({'message': 'userid and password are required', 'status': 400})

                    user_type = data.get('user_type')
                    user = None

                    if user_type == 'student':
                        user = StudentLogin.query.filter_by(userid=userid, is_active=1).first()
                    else:
                        user = AdminLogin.query.filter_by(userid=userid, is_active=1).first()

                    if user is None:
                        return jsonify({'message': 'User does not exist', 'status': 401})

                    if not check_password_hash(user.password, password):
                        return jsonify({'message': 'Invalid userid or password', 'status': 401})

                    if user_type == 'student':
                        id = user.student_id
                        login_data = LoginLog(student_id=id, userid=userid, login_time=datetime.now(), ipaddress=request.remote_addr, is_active=1)
                    else:
                        id = user.admin_id
                        login_data = LoginLog(admin_id=id, userid=userid, login_time=datetime.now(), ipaddress=request.remote_addr, is_active=1)

                    access_token = create_access_token(identity=id)
                    bearer_token = f"Bearer {access_token}"
                    user.refresh_token = access_token

                    userdata = {
                        'id': id,
                        'userid': user.userid,
                        'user_type': user_type
                    }

                    db.session.add(login_data)
                    db.session.commit()

                    return jsonify({'token': bearer_token, 'data': userdata, 'message': 'User Logged In Successfully', 'status': 200})

                except Exception as e:
                    db.session.rollback()
                    
                    return jsonify({'message': str(e), 'status': 500})

        @self.auth_ns.route('/logout')
        class Logout(Resource):
            @self.auth_ns.doc('logout', security='jwt')
            @jwt_required()
            def post(self):
                try:
                    response = jsonify({'message': 'User logged out successfully', 'status': 200})
                    unset_jwt_cookies(response)
                    return response
                except Exception as e:
                    db.session.rollback()
                    
                 
                    return jsonify({'message': str(e), 'status': 500})
            

        
        @self.auth_ns.route('/forgotpassword')
        class ForgotPassword(Resource):
            def send_reset_email(self,email,user_type):
                user = email
                print(user)
                reset_password_link = f"http://qaweb.gyansetu.ai/changepassword?email={email}&user_type={user_type}"
                html_content = render_template('forgotpassword.html', user=user, reset_password_link=reset_password_link)
                msg = Message('Reset Your Password', sender=app.config.get('MAIL_USERNAME'), recipients=[email])
                msg.html = html_content
                
                mail.send(msg)


            @self.auth_ns.doc('forgotpassword', security='jwt')
            @self.api.expect(self.forgotpassword_model)
            def post(self):
                try:
                    data = request.json
                    email = data.get('email')
                    user_type = data.get('user_type')
                  
                    if not email:
                        return jsonify({'message': 'Please provide email', 'status': 400})
                    else:   
                        if(user_type == 'student'):
                            user = StudentLogin.query.filter_by(userid=email,is_active=1).first()
                        else:
                            user = AdminLogin.query.filter_by(userid=email,is_active=1).first()
                    
                    if not user:
                        return jsonify({'message': 'Email not registered', 'status': 404})

               
                    try:
                        self.send_reset_email(email,user_type)
                    except Exception as e:
                        print(e)
                        return jsonify({'message': 'Failed to send reset password email', 'status': 500})

                    return jsonify({'message': 'Reset password instructions sent to email', 'status': 200})
                except Exception as e:
                    db.session.rollback()
             
                    return jsonify({'message': str(e), 'status': 500})
            
        @self.auth_ns.route('/changepassword')
        class ChangePassword(Resource):
            @self.auth_ns.doc('changepassword', security='jwt')
            @self.api.expect(self.change_password_model)
            def post(self):
                try:
                    data = request.json
                    email = data.get('email')
                    old_password = data.get('old_password')
                    new_password = data.get('new_password')
                    user_type = data.get('user_type')

                
                    if not email or not old_password or not new_password:
                        return jsonify({'message': 'Please provide email, old password, and new password', 'status': 400})


                    if user_type == 'student':
                        user = StudentLogin.query.filter_by(userid=email,is_active=1).first()
                        change_log =  ChangePwdLog(student_id=user.student_id,old_pwd=generate_password_hash(old_password),new_pwd=generate_password_hash(new_password),log_system_datetime=datetime.now())
                    elif user_type == 'admin':
                        user = AdminLogin.query.filter_by(userid=email,is_active=1).first()
                        change_log =  ChangePwdLog(admin_id=user.admin_id,old_pwd=generate_password_hash(old_password),new_pwd=generate_password_hash(new_password),log_system_datetime=datetime.now())
                    else:
                        return jsonify({'message': 'Invalid user type', 'status': 400})

                    if not user:
                        return jsonify({'message': 'User not found', 'status': 404})

             
                 
                    if not check_password_hash(user.password, old_password):
                
                        return jsonify({'message': 'Incorrect old password', 'status': 401})
                    else:
                 
                        user.password = generate_password_hash(new_password)
                        db.session.add(change_log)
                        db.session.commit()
                        return jsonify({'message': 'Password changed successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
              
                    return jsonify({'message': str(e), 'status': 500})
                

        @self.auth_ns.route('/resetpassword')
        class ResetPassword(Resource):
            @self.auth_ns.doc('resetpassword', security='jwt')
            @self.api.expect(self.change_password_model)
            def post(self):
                try:
                    data = request.json
                    email = data.get('email')
                    new_password = data.get('new_password')
                    conf_password = data.get('conf_password')
                    user_type = data.get('user_type')

                
                    if not email or not new_password or not conf_password:
                        return jsonify({'message': 'Please provide email, new password, and confirm password', 'status': 400})

                   
                    if user_type == 'student':
                        user = StudentLogin.query.filter_by(userid=email,is_active=1).first()
                       
                    elif user_type == 'admin':
                        user = AdminLogin.query.filter_by(userid=email,is_active=1).first()
                        
                    else:
                        return jsonify({'message': 'Invalid user type', 'status': 400})


                    if not user:
                        return jsonify({'message': 'User not found', 'status': 404})
                    else:
                       
                        user.password = generate_password_hash(new_password)
                      
                        db.session.commit()
                        return jsonify({'message': 'Password changed successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                    
                    return jsonify({'message': str(e), 'status': 500})
                
        @self.auth_ns.route('/activate/<user_id>')
        class ActivateUser(Resource):
            @self.auth_ns.doc('activate_user', security='jwt')
            @jwt_required()
            def put(self, user_id):
                try:
  
                    user = StudentLogin.query.filter_by(userid=user_id).first()
                    if not user:
                        user = AdminLogin.query.filter_by(userid=user_id).first()

                    if not user:
                        return jsonify({'message': 'User not found', 'status': 404})

              
                    user.is_active = 1
                    db.session.commit()

                    return jsonify({'message': 'User activated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
            
                    return jsonify({'message': str(e), 'status': 500})

        @self.auth_ns.route('/deactivate/<user_id>')
        class DeactivateUser(Resource):
            @self.auth_ns.doc('deactivate_user', security='jwt')
            @jwt_required()
            def put(self, user_id):
                try:
               
                    user = StudentLogin.query.filter_by(userid=user_id).first()
                    if not user:
                        user = AdminLogin.query.filter_by(userid=user_id).first()

                    if not user:
                        return jsonify({'message': 'User not found', 'status': 404})

                  
                    user.is_active = 0
                    db.session.commit()

                    return jsonify({'message': 'User deactivated successfully', 'status': 200})
                except Exception as e:
                    db.session.rollback()
                  
                    return jsonify({'message': str(e), 'status': 500})

        self.api.add_namespace(self.auth_ns)


