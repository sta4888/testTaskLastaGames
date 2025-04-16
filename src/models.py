from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class ProcessedFile(Base):
    __tablename__ = "processed_files"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True)
    result = Column(JSON)
    error = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)