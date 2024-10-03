from datetime import timedelta
from flask import Flask, jsonify,request
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
from flask_jwt_extended import JWTManager,get_unverified_jwt_headers
from flask import Flask, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from flask_migrate import Migrate
from authlib.integrations.flask_client import OAuth
import os
import json  # Import the json module
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
log_directory = os.getcwd() 
log_file = os.path.join(log_directory, 'app.log') 
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

file_handler = RotatingFileHandler(log_file, maxBytes=10**6, backupCount=3)
file_handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
# Initialize Flask app
app = Flask(__name__, static_folder='app/resources')
CORS(app, resources={r"/*/*": {"origins": "*"}})
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads', 'student')

# Load configurations from config.py
app.config.from_object('app.config.Config')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=2)

# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=5)
# Initialize SQLAlchemy
db = SQLAlchemy(app)
oauth = OAuth(app)
# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize JWT
jwt = JWTManager(app)

@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):
    return jsonify({
        'message': 'Token has expired',
        'status': 401
    })
api = Api(
   app, 
   version='1.0', 
   title='Auth API', 
   description='Authentication APIs',
   security='jwt'
)

authorizations = {
  'jwt': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': 'Bearer token authorization in the format "Bearer <JWT>"'
    }
}
# Swagger configuration
SWAGGER_URL = '/swagger'
API_URL = '/swagger.json' 
swagger_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Flask API",
         'securityDefinitions': {
            'jwt': {
                'type': 'apiKey',
                'name': 'Authorization',
                'in': 'header',
                'description': 'JWT Authorization header using the Bearer scheme'
            }
        }
    }
)
app.register_blueprint(swagger_blueprint, url_prefix=SWAGGER_URL)

# Import controllers
from app.controllers.admin_contact_controller import AdminContactController
from app.controllers.auth_controller import AuthController
from app.controllers.department_controller import DepartmentController
from app.controllers.course_controller import CourseController
from app.controllers.subject_controller import SubjectController
from app.controllers.institute_controller import InstituteController
from app.controllers.entity_controller import EntityController
from app.controllers.form_controller import FormController
from app.controllers.menu_controller import MenuController
from app.controllers.submenu_controller import SubMenuController
from app.controllers.role_controller import RoleController
from app.controllers.rolevsadmin_controller import RolevsAdminController
from app.controllers.rolevsform_controller import RolevsFormController
from app.controllers.admin_basicinfo_controller import AdminBasicInformationController
from app.controllers.admin_address_controller import AdminAddressController
from app.controllers.admin_language_known_controller import AdminLanguageKnownController
from app.controllers.admin_profile_description_controller import AdminProfileDescriptionController
from app.controllers.admin_profession_controller import AdminProfessionController
from app.controllers.language_controller import LanguageController
from app.controllers.student_controller import StudentController
from app.controllers.student_address_controller import StudentAddressController
from app.controllers.student_language_known_controller import StudentLanguageKnownController
from app.controllers.student_academic_history_controller import StudentAcademicHistoryController
from app.controllers.student_hobby_controller import StudentHobbyController
from app.controllers.hobby_master_controller import HobbyController
from app.controllers.subject_preference_controller import SubjectPreferenceController
from app.controllers.fileupload_controller import UploadFileController
from app.controllers.student_contact_controller import StudentContactController
from app.controllers.chat_controller import ChatController
from app.controllers.chatbot_controller import ChatbotController
from app.controllers.calculate_completion_controller import CalculateCompletion
from app.controllers.class_controller import ClassController
from app.controllers.student_profile_controller import ProfileController
from app.controllers.feedback_controller import FeedbackController
from app.controllers.new_student_academic_history_controller import NewStudentAcademicHistoryController
# from app.controllers.google_login import google_bp
# Instantiate controllers
auth_controller = AuthController(api)
subject_controller = SubjectController(api)
department_controller = DepartmentController(api)
course_controller = CourseController(api)
institute_controller = InstituteController(api)
entity_controller = EntityController(api)
form_controller = FormController(api)
menu_controller = MenuController(api)
submenu_controller = SubMenuController(api)
role_controller = RoleController(api)
rolevsadmin_controller = RolevsAdminController(api)
rolevsform_controller = RolevsFormController(api)
admin_basicinfo_controller = AdminBasicInformationController(api)
admin_address_controller = AdminAddressController(api)
admin_language_known_controller = AdminLanguageKnownController(api)
admin_profile_description_controller = AdminProfileDescriptionController(api)
admin_profession_controller = AdminProfessionController(api)
language_controller = LanguageController(api)
student_controller = StudentController(api)
student_address_controller = StudentAddressController(api)
student_language_known_controller = StudentLanguageKnownController(api)
student_academic_history_controller = StudentAcademicHistoryController(api)
student_hobby_controller = StudentHobbyController(api)
hobby_master_controller = HobbyController(api)
subject_preference_controller = SubjectPreferenceController(api)
file_upload_controller = UploadFileController(api)
student_contact_controller = StudentContactController(api)
admin_contact_controller = AdminContactController(api)
chat_controller = ChatController(api)
chatbot_controller = ChatbotController(api)
calculate_completion_controller=CalculateCompletion(api)
class_controller=ClassController(api)
student_profile_controller=ProfileController(api)
feedback_controller=FeedbackController(api)
new_academic_history=NewStudentAcademicHistoryController(api)
# Register blueprints
app.register_blueprint(auth_controller.auth_bp)
app.register_blueprint(subject_controller.subject_bp)
app.register_blueprint(department_controller.department_bp)
app.register_blueprint(course_controller.course_bp)
app.register_blueprint(institute_controller.institution_bp)
app.register_blueprint(entity_controller.entity_bp)
app.register_blueprint(form_controller.form_bp)
app.register_blueprint(menu_controller.menu_bp)
app.register_blueprint(submenu_controller.submenu_bp)
app.register_blueprint(role_controller.role_bp)
app.register_blueprint(rolevsadmin_controller.rolevsadmin_bp)
app.register_blueprint(rolevsform_controller.rolevsform_bp)
app.register_blueprint(admin_basicinfo_controller.admin_basicinfo_bp)
app.register_blueprint(admin_address_controller.admin_address_bp)
app.register_blueprint(admin_language_known_controller.admin_language_known_bp)
app.register_blueprint(admin_profile_description_controller.admin_profile_description_bp)
app.register_blueprint(admin_profession_controller.admin_profession_bp)
app.register_blueprint(language_controller.language_bp)
app.register_blueprint(student_controller.student_bp)
app.register_blueprint(student_address_controller.student_address_bp)
app.register_blueprint(student_language_known_controller.student_language_known_bp)
app.register_blueprint(student_academic_history_controller.student_academic_history_bp)
app.register_blueprint(hobby_master_controller.hobby_bp)
app.register_blueprint(student_hobby_controller.student_hobby_bp)
app.register_blueprint(subject_preference_controller.subject_preference_bp)
app.register_blueprint(file_upload_controller.upload_file_bp)
app.register_blueprint(student_contact_controller.student_contact_bp)
app.register_blueprint(admin_contact_controller.admin_contact_bp)
app.register_blueprint(chat_controller.chat_bp)
app.register_blueprint(chatbot_controller.chatbot_bp)
app.register_blueprint(calculate_completion_controller.calculate_completion_bp)
app.register_blueprint(class_controller.class_bp)
app.register_blueprint(student_profile_controller.profile_bp)
app.register_blueprint(feedback_controller.feedback_bp)
app.register_blueprint(new_academic_history.new_student_academic_history_bp)
# app.register_blueprint(google_bp, url_prefix='/google')
# api.init_app(app)

# Route for serving Swagger JSON
@app.route('/swagger.json')
def swagger():
    with open('swagger.json', 'r') as f:
        return jsonify(json.load(f))
 
if __name__ == "__main__":
    app.run(debug=True)