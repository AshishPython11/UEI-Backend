import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:Admin@localhost/gurukulai'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:root@localhost:5432/SakshemIT'
    # SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:root@localhost:5432/Test'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'Ashish@123'
    # MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_SERVER = 'smtpout.secureserver.net'
    # MAIL_PORT = 465
    MAIL_USE_TLS = True
    # MAIL_USERNAME = 'ashishpython11@gmail.com'
    # MAIL_PASSWORD = 'ngwu fxqp yjay fjxa'
    MAIL_USERNAME = 'info@gyansetu.ai'
    MAIL_PASSWORD = 'gyansetu@123'
# import os

# class Config:
#     SECRET_KEY = os.environ.get('SECRET_KEY') or 'hiral'
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'hiral123'
