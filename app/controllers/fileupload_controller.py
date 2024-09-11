from flask import Blueprint, request, jsonify
from flask_restx import Resource, fields
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
import os
from flask import url_for
import base64
import json

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads', 'student')
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
current_path = os.getcwd()
full_path = os.path.join(current_path, UPLOAD_FOLDER)
class UploadFileController:
    def __init__(self, api):
        self.api = api
        self.upload_file_model = api.model('UploadFile', {
             'file': fields.Raw(required=True, description='File', location='files', type='file')
        })
        
        self.upload_file_bp = Blueprint('upload_file', __name__)
        self.upload_file_ns = api.namespace('upload_file', description='Upload file')
        self.upload_parser = self.api.parser()
        self.upload_parser.add_argument('file', location='files', type='file')   
        self.get_file_model =  api.model('GetFile', {        
            'Filename': fields.String(required=True, description='Image name with extention'),
        })
     
        self.register_routes()
      
    def register_routes(self):
        @self.upload_file_ns.route('/upload')
        class UploadFile(Resource):  
            def allowed_file(self, filename):
                return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
            def save_file_and_return_url(self, file):
                if file and self.allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(full_path, filename)
                    file.save(file_path)
                    
                    file_url =  full_path + '/' + filename
               
                    return file_url
                else:
                
                    return jsonify({'error': 'File type not allowed'})
                
            @self.upload_file_ns.doc('upload_file/upload', security='jwt', parser=self.upload_parser)
            @self.api.expect(self.upload_file_model)
            @jwt_required()
            def post(self):
                try:
                    file = request.files['file']
                    if not os.path.exists(full_path):
                        os.makedirs(full_path)
                 
                    if 'file' not in request.files:
            
                        return jsonify({'error': 'No file part'})
                    else:
                        file_url = self.save_file_and_return_url(file)
                        data ={
                            'image_url':file_url
                        }
                        return jsonify({'message': 'File uploaded successfully', 'status': 200,'data':data})
                except Exception as e:

                    return jsonify({'message': str(e), 'status': 500})
        @self.upload_file_ns.route('/get_image/<file_name>')
        class GetFile(Resource):
            def read_and_encode_file(self,file_path):
                if os.path.isfile(file_path):
                    with open(file_path, 'rb') as f:
                        encoded_bytes = base64.b64encode(f.read())
                        encoded_string = encoded_bytes.decode('utf-8')

                    return encoded_string
                else:
    
                    return None  

            @self.upload_file_ns.doc('upload_file/get', security='jwt')
            @jwt_required()
            def get(self,file_name):
                    try:
                        file_path = os.path.join(full_path, file_name)
                        if file_name:
                            file_content = self.read_and_encode_file(file_path)
                            if file_content:
                                file_content_with_prefix = f"data:image/png;base64,{file_content}"
                                json_data = json.dumps({"encoded_data": file_content})
                                print("working")
    
                                return jsonify({'message': 'File fetch successfully', 'status': 200,'data':file_content_with_prefix})
                            return jsonify({'error': 'File not found'})
                        return jsonify({'error': 'Please provide filename'})
                    except Exception as e:

                        return jsonify({'message': str(e), 'status': 500})


        self.api.add_namespace(self.upload_file_ns)
