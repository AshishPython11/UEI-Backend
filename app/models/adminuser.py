from app import db
from enum import Enum
import uuid
from datetime import datetime 
from sqlalchemy.dialects.postgresql import UUID
class add_enum(Enum):
    current_address = 0
    permanent_address = 1 


class TimestampMixin(object):
    # updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

    @classmethod
    def __declare_last__(cls):
        @db.event.listens_for(cls, 'before_update')
        def set_updated_at_before_update(mapper, connection, target):
            target.updated_at = datetime.now()

class AdminLogin(db.Model,TimestampMixin):
    __tablename__ = 'tbl_admin_login'
    # admin_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    admin_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    userid = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Integer, default=1)
    otp = db.Column(db.String,nullable=True)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

    def __repr__(self):
        return f"Admin('{self.userid}')"
class AdminBasicInformation(db.Model,TimestampMixin):
    __tablename__ = 'tbl_admin_basic_information'
    # admin_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    admin_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    admin_login_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_admin_login.admin_id'),nullable=True)
    admin_registration_no = db.Column(db.String(255))
    department_id = db.Column(UUID(as_uuid=True),db.ForeignKey('tbl_department_master.department_id'), nullable=False)  # References department_master table
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    father_name = db.Column(db.String(255))
    mother_name = db.Column(db.String(255))
    guardian_name = db.Column(db.String(255))
    is_kyc_verified = db.Column(db.Boolean, nullable=True)
    system_datetime = db.Column(db.DateTime, nullable=False)
    pic_path = db.Column(db.String(255))
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    last_modified_datetime = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

class AdminAddress(db.Model,TimestampMixin):
    __tablename__ = 'tbl_admin_address'
    admin_address_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    admin_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_admin_login.admin_id'),nullable=False)
    address1 = db.Column(db.String(255))
    address2 = db.Column(db.String(255),nullable=True)
    country = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    district = db.Column(db.String, nullable=False)
    pincode = db.Column(db.String, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    address_type = db.Column(db.String(100), nullable=True) 
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

class AdminContact(db.Model,TimestampMixin):
    __tablename__ = 'tbl_admin_contact'
    admin_contact_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    admin_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_admin_login.admin_id'),nullable=False)
    email_id = db.Column(db.String(255), nullable=False)
    mobile_isd_call = db.Column(db.String(255))
    mobile_no_call = db.Column(db.String(255))
    mobile_isd_watsapp = db.Column(db.String(255))
    mobile_no_watsapp = db.Column(db.String(255))
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

class AdminLanguageKnown(db.Model,TimestampMixin):
    __tablename__ = 'tbl_admin_language_known'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    admin_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_admin_login.admin_id'), nullable=False)
    language_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_language_master.language_id'), nullable=False)
    proficiency = db.Column(db.String, nullable=True)
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

class AdminDescription(db.Model,TimestampMixin):
    __tablename__ = 'tbl_admin_description'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    admin_id = db.Column(UUID(as_uuid=True),db.ForeignKey('tbl_admin_login.admin_id'),nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

class AdminProfession(db.Model,TimestampMixin):
    __tablename__ = 'tbl_admin_profession'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    admin_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_admin_login.admin_id'), nullable=False)
    institution_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_institutions.institution_id'), nullable=False)
    course_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_course_master.course_id'), nullable=False)  # References course table
    subject_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_subject_master.subject_id'), nullable=False)  # References subject tablecl
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

    def __repr__(self):
        return f"User('{self.userid}')"

class DepartmentMaster(db.Model,TimestampMixin):
    __tablename__ = 'tbl_department_master'
    department_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    department_name = db.Column(db.String(255))
    is_active = db.Column(db.Integer,nullable=True, default=1)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    icon = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)  # New field

class UserType(db.Model,TimestampMixin):
    __tablename__ = 'tbl_user_type'
    user_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    user_type = db.Column(db.String(255))
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())


# Define tbl_language_master first
class LanguageMaster(db.Model,TimestampMixin):
    __tablename__ = 'tbl_language_master'
    language_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    language_name = db.Column(db.String(255))
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    icon = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)  # New field


class EntityType(db.Model,TimestampMixin):
    __tablename__ = 'tbl_entity_type'
    entity_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    entity_type = db.Column(db.String(255))
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_deleted = db.Column(db.Boolean, default=False)

class Institution(db.Model,TimestampMixin):
    __tablename__ = 'tbl_institutions'
    institution_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    institution_name = db.Column(db.String(255))
    entity_id = db.Column(UUID(as_uuid=True), db.ForeignKey(EntityType.entity_id), nullable=True)
    address = db.Column(db.String(255),nullable=True)
    country = db.Column(db.String, nullable=True)
    state = db.Column(db.String, nullable=True)
    city = db.Column(db.String, nullable=True)
    district = db.Column(db.String, nullable=True)
    pincode = db.Column(db.String, nullable=True)
    website_url = db.Column(db.String(255),nullable=True)
    mobile_no = db.Column(db.String(255), nullable=True)
    email_id = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_deleted = db.Column(db.Boolean, default=False)

class CourseMaster(db.Model,TimestampMixin):
    __tablename__ = 'tbl_course_master'
    course_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    course_name = db.Column(db.String(255))
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    icon = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)  # New field

class SubjectMaster(db.Model,TimestampMixin):
    __tablename__ = 'tbl_subject_master'
    subject_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    subject_name = db.Column(db.String(255))
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    icon = db.Column(db.String, nullable=True)
    description = db.Column(db.String, nullable=True)
    is_deleted = db.Column(db.Boolean, default=False)  # New field