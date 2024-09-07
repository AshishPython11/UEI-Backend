from datetime import datetime
from .student import StudentLogin,Student
from .adminuser import AdminBasicInformation,AdminLogin,TimestampMixin
from app import db


class ChangePwdLog(db.Model,TimestampMixin):
    __tablename__ = 'tbl_change_pwd_log'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    admin_id = db.Column(db.Integer,db.ForeignKey(AdminLogin.admin_id),nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey(StudentLogin.student_id),nullable=True)
    old_pwd = db.Column(db.String(255), nullable=False)
    new_pwd = db.Column(db.String(255), nullable=False)
    log_system_datetime = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

class EditLog(db.Model,TimestampMixin):
    __tablename__ = 'tbl_edit_log'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    admin_id = db.Column(db.Integer,db.ForeignKey(AdminLogin.admin_id),nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey(StudentLogin.student_id),nullable=True)
    user_type = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    remarks = db.Column(db.String(255))
    log_system_datetime = db.Column(db.DateTime, nullable=False)
    action_type = db.Column(db.String(255))
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

class LoginLog(db.Model,TimestampMixin):
    __tablename__ = 'tbl_login_log'
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey(StudentLogin.student_id), nullable=True)
    admin_id = db.Column(db.Integer, db.ForeignKey(AdminLogin.admin_id), nullable=True)
    userid = db.Column(db.String(255), nullable=False)
    login_time = db.Column(db.DateTime, nullable=False)
    ipaddress = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
