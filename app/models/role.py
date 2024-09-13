from datetime import datetime 
from .student import Student
from .adminuser import AdminBasicInformation,TimestampMixin
from app import db
from sqlalchemy.orm import relationship


class RoleVsAdminMaster(db.Model,TimestampMixin):
    __tablename__ = 'tbl_role_vs_admin_master'
    role_admin_master_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    admin_id = db.Column(db.Integer, db.ForeignKey(AdminBasicInformation.admin_id), nullable=False)  # References admin_basic_information table
    role_master_id = db.Column(db.Integer, db.ForeignKey('tbl_role_master_data.role_master_id'), nullable=False)  # References role_master table
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_deleted = db.Column(db.Boolean, default=False)  # New field
    admin = relationship('AdminBasicInformation', backref='role_assignments')
    role = relationship('RoleMasterData', backref='admin_assignments')


class Role(db.Model,TimestampMixin):
    __tablename__ = 'tbl_role'
    role_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey(Student.student_id), nullable=False)
    role_name = db.Column(db.String(255))
    log_datetime = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_deleted = db.Column(db.Boolean, default=False)  # New field

    def __repr__(self):
        return f"User('{self.userid}')"


class MenuMaster(db.Model,TimestampMixin):
    __tablename__ = 'tbl_menu_master'
    menu_master_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    # application_type_id = db.Column(db.Integer, nullable=False)
    # menu_type_id = db.Column(db.Integer, nullable=False)
    menu_name = db.Column(db.String(255))
    priority = db.Column(db.Integer)
    is_active = db.Column(db.Boolean,default=1)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    icon = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)  # New field

class MenuMasterData(db.Model,TimestampMixin):
    __tablename__ = 'tbl_menu_master_data'
    menu_master_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    # application_type_id = db.Column(db.Integer, nullable=False)
    # menu_type_id = db.Column(db.Integer, nullable=False)
    menu_name = db.Column(db.String(255))
    priority = db.Column(db.Integer)
    is_active = db.Column(db.Integer, default=1,nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    icon = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)  # New field

class SubMenuMaster(db.Model,TimestampMixin):
    __tablename__ = 'tbl_submenu_master'
    submenu_master_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    menu_master_id = db.Column(db.Integer, db.ForeignKey('tbl_menu_master.menu_master_id'), nullable=False)
    # application_type_id = db.Column(db.Integer, nullable=False)
    # menu_type_id = db.Column(db.Integer, nullable=False)
    menu_name = db.Column(db.String(255))
    priority = db.Column(db.Integer)
    is_active = db.Column(db.Boolean,default=1)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_deleted = db.Column(db.Boolean, default=False)  # New field

class SubMenuMasterData(db.Model,TimestampMixin):
    __tablename__ = 'tbl_submenu_master_data'
    submenu_master_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    menu_master_id = db.Column(db.Integer, db.ForeignKey('tbl_menu_master_data.menu_master_id'), nullable=False)
    # application_type_id = db.Column(db.Integer, nullable=False)
    # menu_type_id = db.Column(db.Integer, nullable=False)
    menu_name = db.Column(db.String(255))
    priority = db.Column(db.Integer)
    is_active = db.Column(db.Integer, default=1,nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_deleted = db.Column(db.Boolean, default=False)  # New field


class RoleMaster(db.Model,TimestampMixin):
    __tablename__ = 'tbl_role_master'
    role_master_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    role_name = db.Column(db.String(255))
    is_active = db.Column(db.Boolean,default=1)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_deleted = db.Column(db.Boolean, default=False)  # New field


class RoleMasterData(db.Model,TimestampMixin):
    __tablename__ = 'tbl_role_master_data'
    role_master_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    role_name = db.Column(db.String(255))
    is_active = db.Column(db.Integer, default=1,nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_deleted = db.Column(db.Boolean, default=False)  # New field

class FormMaster(db.Model,TimestampMixin):
    __tablename__ = 'tbl_form_master'
    form_master_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    menu_master_id = db.Column(db.Integer, db.ForeignKey('tbl_menu_master.menu_master_id'), nullable=False)  # References menu_master table
    sub_menu_master_id = db.Column(db.Integer, db.ForeignKey('tbl_submenu_master.submenu_master_id'), nullable=True)  # References menu_master table
    form_name = db.Column(db.String(255))
    form_url = db.Column(db.String(255))
    form_description = db.Column(db.String(255),nullable=True)
    is_menu_visible = db.Column(db.Boolean)
    is_active = db.Column(db.Boolean,default=1)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_deleted = db.Column(db.Boolean, default=False)  # New field


class FormMasterData(db.Model,TimestampMixin):
    __tablename__ = 'tbl_form_master_data'
    form_master_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    menu_master_id = db.Column(db.Integer, db.ForeignKey('tbl_menu_master_data.menu_master_id'), nullable=False)  # References menu_master table
    sub_menu_master_id = db.Column(db.Integer, db.ForeignKey('tbl_submenu_master_data.submenu_master_id'), nullable=True)  # References menu_master table
    form_name = db.Column(db.String(255))
    form_url = db.Column(db.String(255))
    form_description = db.Column(db.String(255),nullable=True)
    is_menu_visible = db.Column(db.Boolean)
    is_active = db.Column(db.Integer, default=1,nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_deleted = db.Column(db.Boolean, default=False)  # New field

class RoleVsFormMaster(db.Model,TimestampMixin):
    __tablename__ = 'tbl_role_vs_form_master'
    role_form_master_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    form_master_id = db.Column(db.Integer, db.ForeignKey('tbl_form_master_data.form_master_id'), nullable=False)  # References form_master table
    role_master_id = db.Column(db.Integer, db.ForeignKey('tbl_role_master_data.role_master_id'), nullable=False)  # References role_master table
    is_search = db.Column(db.Boolean)
    is_save = db.Column(db.Boolean)
    is_update = db.Column(db.Boolean,default=1)
    is_active = db.Column(db.Boolean,default=1,nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_deleted = db.Column(db.Boolean, default=False)  # New field
    


class RoleVsFormMasterData(db.Model,TimestampMixin):
    __tablename__ = 'tbl_role_vs_form_master_data'
    role_form_master_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    form_master_id = db.Column(db.Integer, db.ForeignKey('tbl_form_master_data.form_master_id'), nullable=False)  # References form_master table
    role_master_id = db.Column(db.Integer, db.ForeignKey('tbl_role_master_data.role_master_id'), nullable=False)  # References role_master table
    is_search = db.Column(db.Boolean)
    is_save = db.Column(db.Boolean)
    is_update = db.Column(db.Boolean,default=1)
    is_active = db.Column(db.Integer, default=1,nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_deleted = db.Column(db.Boolean, default=False)  # New field
    role = relationship('RoleMasterData', backref='form_assignments')
    form = relationship('FormMasterData', backref='role_assignments')



class ManageRole(db.Model,TimestampMixin):
    __tablename__ = 'tbl_manage_role'
    manage_role_id=db.Column(db.Integer,primary_key=True)
    role_master_id = db.Column(db.String(255))
    form_master_id = db.Column(db.String(255))
    is_search = db.Column(db.Boolean, default=True)
    is_save = db.Column(db.Boolean, default=True)
    is_update = db.Column(db.Boolean, default=True)
    admin_id = db.Column(db.String(255),nullable=True)
    is_active = db.Column(db.Integer, default=1)
    is_delete = db.Column(db.Boolean, default=False)

