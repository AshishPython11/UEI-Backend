from app import db
from .adminuser import LanguageMaster,Institution,CourseMaster,SubjectMaster,TimestampMixin
from datetime import datetime 
from sqlalchemy.dialects.postgresql import UUID
import uuid
class LanguageKnown(db.Model,TimestampMixin):
    __tablename__ = 'tbl_student_language_known'
    language_known_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    student_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_student_login.student_id'), nullable=False)
    language_id = db.Column(UUID(as_uuid=True), db.ForeignKey(LanguageMaster.language_id), nullable=False)
    proficiency = db.Column(db.String(255))
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())


class Contact(db.Model,TimestampMixin):
    __tablename__ = 'tbl_student_contact'
    contact_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    student_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_student_login.student_id'), nullable=False)
    email_id = db.Column(db.String(255), nullable=False)
    mobile_isd_call = db.Column(db.String(255))
    mobile_no_call = db.Column(db.String(255))
    mobile_isd_watsapp = db.Column(db.String(255))
    mobile_no_watsapp = db.Column(db.String(255),nullable=True)
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

class StudentAddress(db.Model,TimestampMixin):
    __tablename__ = 'tbl_student_address'
    address_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    student_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_student_login.student_id'), nullable=False)
    address_type = db.Column(db.String(10), nullable=False)  # Current or Permanent
    address1 = db.Column(db.String(255))
    address2 = db.Column(db.String(255),nullable=True)
    country = db.Column(db.String, nullable=False)  # References country table
    state = db.Column(db.String, nullable=False)  # References state table
    city = db.Column(db.String, nullable=False)  # References city table
    district = db.Column(db.String, nullable=False)  # References district table
    pincode = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

class Student(db.Model,TimestampMixin):
    __tablename__ = 'tbl_student'
    student_id =db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    student_login_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_student_login.student_id'), nullable=False)
    student_registration_no = db.Column(db.String(255))
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255), nullable=False)
    gender = db.Column(db.String, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    father_name = db.Column(db.String(255))
    mother_name = db.Column(db.String(255))
    guardian_name = db.Column(db.String(255),nullable=True)
    is_kyc_verified = db.Column(db.Boolean, nullable=True)
    system_datetime = db.Column(db.DateTime, nullable=False)
    pic_path = db.Column(db.String(255),nullable=True)
    last_modified_datetime = db.Column(db.DateTime, nullable=False)
    aim = db.Column(db.String(255),nullable=True)
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_deleted = db.Column(db.Boolean, default=False)
class StudentLogin(db.Model,TimestampMixin):
    __tablename__ = 'tbl_student_login'
    student_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    userid = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    refresh_token = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Integer, default=1)
    otp = db.Column(db.String,nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

    def __repr__(self):
        return f"User('{self.userid}')"

class AcademicHistory(db.Model,TimestampMixin):
    __tablename__ = 'tbl_academic_history'
    academic_history_id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    student_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_student_login.student_id'), nullable=False)
    institution_id = db.Column(UUID(as_uuid=True), db.ForeignKey(Institution.institution_id), nullable=False)
    course_id = db.Column(UUID(as_uuid=True), db.ForeignKey(CourseMaster.course_id), nullable=False)
    class_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_class_master.class_id'), nullable=True)
    ending_date = db.Column(db.Date, nullable=False)
    system_datetime = db.Column(db.DateTime, nullable=False, default=datetime.now())
    starting_date = db.Column(db.Date)
    learning_style = db.Column(db.String(255))
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

class StudentHobby(db.Model,TimestampMixin):
    __tablename__ = 'tbl_student_hobbies'
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    hobby_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_hobby_master.hobby_id'), nullable=False)
    student_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_student_login.student_id'), nullable=False)
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

class SubjectPreference(db.Model,TimestampMixin):
    __tablename__ = 'tbl_student_subject_preference'
    subject_preference_id =db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    student_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_student_login.student_id'), nullable=False)
    course_id = db.Column(UUID(as_uuid=True), db.ForeignKey(CourseMaster.course_id), nullable=False)
    subject_id = db.Column(UUID(as_uuid=True), db.ForeignKey(SubjectMaster.subject_id), nullable=False)
    preference = db.Column(db.String(255))
    score_in_percentage = db.Column(db.Float)
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())


class Hobby(db.Model,TimestampMixin):
    __tablename__ = 'tbl_hobby_master'
    hobby_id =db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    hobby_name = db.Column(db.String(255))
    is_active = db.Column(db.Integer, default=1, nullable=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_deleted = db.Column(db.Boolean, default=False)  # New field

class ClassMaster(db.Model):
    __tablename__ = 'tbl_class_master'
    class_id =db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    class_name = db.Column(db.String(80), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)

class Feedback(db.Model):
   
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    question = db.Column(db.String(255), nullable=False)
    options = db.Column(db.String(255), nullable=False)  # Assuming options are stored as a comma-separated string
    created_by = db.Column(db.String, nullable=True)
    updated_by = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())
    is_deleted = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

class StudentFeedback(db.Model):
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    student_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_student_login.student_id'), nullable=False)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now())
    is_active = db.Column(db.Integer, default=1, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

class NewStudentAcademicHistory(db.Model):
    __tablename__ = 'new_student_academic_history'
    
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    student_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_student_login.student_id'), nullable=False)
    institution_type = db.Column(db.String(50), nullable=False) # School/College/Competition Exams 
    board= db.Column(db.String(255), nullable=True)  # CBSE/ICSE/Stateboard
    state_for_stateboard = db.Column(db.String(255), nullable=True)  
    class_or_course = db.Column(db.String(255), nullable=True)  
    year_or_semester = db.Column(db.String(50), nullable=True) 
    university_name = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now(), onupdate=datetime.now())
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String(255), nullable=True)
    updated_by = db.Column(db.String(255), nullable=True)
    learning_style = db.Column(db.String(255), nullable=True)  
    institute_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_institutions.institution_id'), nullable=False)
    course_id = db.Column(UUID(as_uuid=True), db.ForeignKey(CourseMaster.course_id), nullable=False)
    class_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_class_master.class_id'), nullable=False)
    