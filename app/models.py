from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    type = Column(String(50), nullable=False)  # "text", "voice", "video"
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
