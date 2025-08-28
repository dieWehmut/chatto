from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    invite_code = Column(String(50), unique=True, index=True)
    username = Column(String(100), index=True)
    is_admin = Column(Boolean, default=False)
    is_online = Column(Boolean, default=False)
    last_active = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    messages = relationship("Message", back_populates="user", foreign_keys="Message.user_id")
    deleted_messages = relationship("Message", foreign_keys="Message.deleted_by")

class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    content = Column(Text, nullable=False)
    message_type = Column(String(20), default='text')  # text, image, file
    file_path = Column(String(500), nullable=True)  # 文件存储路径
    file_name = Column(String(200), nullable=True)  # 原始文件名
    file_size = Column(Integer, nullable=True)  # 文件大小（字节）
    is_from_admin = Column(Boolean, default=False)
    target_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # 管理员消息的目标用户
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    user = relationship("User", back_populates="messages", foreign_keys=[user_id])
    target_user = relationship("User", foreign_keys=[target_user_id])
    deleted_by_user = relationship("User", foreign_keys=[deleted_by])