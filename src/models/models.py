from sqlalchemy import Column, Integer, String, JSON, DateTime
from datetime import datetime

from models.database import Base


class ProcessedFile(Base):
    __tablename__ = "processed_files"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True)
    result = Column(JSON)
    error = Column(String)
    status = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)