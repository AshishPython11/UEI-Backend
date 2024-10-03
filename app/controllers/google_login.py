from flask import Blueprint, redirect, url_for, session, jsonify
from authlib.integrations.flask_client import OAuth
from werkzeug.security import generate_password_hash
import json
import os
import random
from app import oauth,db
from flask_jwt_extended import create_access_token, JWTManager, jwt_required, get_jwt_identity
from app.models.student import StudentLogin 


google_bp = Blueprint('google', __name__)

with open('uei_key.json') as f:
    client_secrets = json.load(f)

google = oauth.register(
    name='google',
    client_id=client_secrets['web']['client_id'],
    client_secret=client_secrets['web']['client_secret'],
    access_token_url=client_secrets['web']['token_uri'],
    authorize_url=client_secrets['web']['auth_uri'],
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration'
)

@google_bp.route('/login')
def login():
    redirect_uri = url_for('google.authorize', _external=True)
    return google.authorize_redirect(redirect_uri)
@google_bp.route('/authorize')
def authorize():
    try:
      
        token = google.authorize_access_token()
        resp = google.get('https://openidconnect.googleapis.com/v1/userinfo')
        user_info = resp.json()
        print(user_info)

        session['profile'] = user_info
        session.permanent = True

        user_email = user_info['email']
        existing_user = StudentLogin.query.filter_by(userid=user_email, is_active=1).first()

        if existing_user is None:

            new_user = StudentLogin(
                userid=user_email,
                password=generate_password_hash("default_password"), 
                is_active=1,
                otp=random.randint(1000, 9999)
            )
            db.session.add(new_user)
            db.session.commit()
            user_id = new_user.userid
        else:
            user_id = existing_user.userid

        access_token = create_access_token(identity=user_id)

        print("User logged in successfully")

        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'token_type': 'Bearer'
        }), 200

    except Exception as e:
        return f'Error during authorization: {e}', 500

@google_bp.route('/logout')
def logout():
    session.pop('profile', None)
    return redirect('/')

