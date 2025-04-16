from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, ForeignKey
from datetime import datetime

from sqlalchemy.orm import relationship

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

    word_stats = relationship(
        "WordStat",
        back_populates="processed_file",
        foreign_keys="[WordStat.processed_file_id]"
    )


class WordStat(Base):
    __tablename__ = "word_stats"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, ForeignKey("processed_files.file_id"), index=True)  # Внешний ключ
    term = Column(String, index=True)
    tf = Column(Integer)
    idf = Column(Float)

    processed_file_id = Column(Integer, ForeignKey("processed_files.id"))

    processed_file = relationship(
        "ProcessedFile",
        back_populates="word_stats",
        foreign_keys="[WordStat.processed_file_id]"
    )
