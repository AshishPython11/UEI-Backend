from app import db
from datetime import datetime
from .adminuser import TimestampMixin
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Chatbot(db.Model, TimestampMixin):
    __tablename__ = "tbl_chatbot"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    student_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("tbl_student_login.student_id"), nullable=False
    )
    chat_question = db.Column(db.String(255))
    response = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now()
    )
    is_active = db.Column(db.Integer, default=1, nullable=False)


class ChatData(db.Model, TimestampMixin):
    __tablename__ = "tbl_chat_data"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    student_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("tbl_student_login.student_id"), nullable=False
    )
    chat_question = db.Column(db.String(255))
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
     # New field
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now()
    )
    is_active = db.Column(db.Integer, default=1, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)


class ChatCache(db.Model, TimestampMixin):
    __tablename__ = "tbl_chat_cache"
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    student_stream = db.Column(db.String(255))
    student_course = db.Column(db.String(255))
    chat_question = db.Column(db.String(255))
    response = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    is_active = db.Column(db.Integer, default=1,nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)  # New field
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now()
    )
class CustomChatData(db.Model):
    __tablename__ = 'custom_chat_data' 

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    student_id = db.Column(db.Integer, nullable=False)
    chat_title = db.Column(db.Text, nullable=False)
    chat_conversation = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    flagged = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<CustomChatData {self.id}>'
from sqlalchemy import Index

# Assuming ChatConversionData class is defined in your models


class ChatConversionData(db.Model):
    __tablename__ = 'chat_conversation_data' 
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    student_id = db.Column(UUID(as_uuid=True), db.ForeignKey('tbl_student_login.student_id'), nullable=False)
    chat_question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)
    is_deleted = db.Column(db.Boolean, default=False)
    idx_chat_question = Index('idx_chat_question', chat_question)

    def __repr__(self):
        return f'<ChatConversationHistory {self.id}>'

    
