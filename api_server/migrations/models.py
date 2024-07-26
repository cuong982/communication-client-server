from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)  # 'text', 'voice', 'video'
    media_path = Column(String(512), nullable=True)  # Path to media file for voice/video
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    is_read = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
