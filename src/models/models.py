from sqlalchemy import Column, Integer, String, JSON, DateTime, Float, ForeignKey, Boolean
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


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(128), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    documents = relationship("Document", back_populates="owner", cascade="all, delete-orphan")
    collections = relationship("Collection", back_populates="owner", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(255), nullable=False)
    file_hash = Column(String(64), unique=True)  # Для проверки дубликатов
    owner_id = Column(Integer, ForeignKey("users.id"))
    processed_file_id = Column(Integer, ForeignKey("processed_files.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="documents")
    processed_file = relationship("ProcessedFile")
    collections = relationship("CollectionDocument", back_populates="document", cascade="all, delete-orphan")
    statistics = relationship("DocumentStatistics", uselist=False, back_populates="document",
                              cascade="all, delete-orphan")


class Collection(Base):
    __tablename__ = "collections"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner = relationship("User", back_populates="collections")
    documents = relationship("CollectionDocument", back_populates="collection", cascade="all, delete-orphan")
    statistics = relationship("CollectionStatistics", uselist=False, back_populates="collection",
                              cascade="all, delete-orphan")


class CollectionDocument(Base):
    __tablename__ = "collection_documents"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    collection_id = Column(Integer, ForeignKey("collections.id"))
    added_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("Document", back_populates="collections")
    collection = relationship("Collection", back_populates="documents")


class DocumentStatistics(Base):
    __tablename__ = "document_statistics"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), unique=True)
    tf_idf_data = Column(JSON)  # {word: {"tf": float, "idf": float}}
    processed_at = Column(DateTime)

    document = relationship("Document", back_populates="statistics")


class CollectionStatistics(Base):
    __tablename__ = "collection_statistics"

    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, ForeignKey("collections.id"), unique=True)
    tf_idf_data = Column(JSON)  # {word: {"tf": float, "idf": float}}
    processed_at = Column(DateTime)
    documents_count = Column(Integer)

    collection = relationship("Collection", back_populates="statistics")