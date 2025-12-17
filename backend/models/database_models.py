"""
Database models for drug repurposing system
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from core.database import Base


class Query(Base):
    """User queries for drug repurposing requirements"""
    __tablename__ = "queries"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=True, index=True)
    query_text = Column(Text, nullable=False)
    status = Column(String(50), default="pending", index=True)  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = relationship("Task", back_populates="query", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="query", cascade="all, delete-orphan")


class Task(Base):
    """Individual agent tasks"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_type = Column(String(100), nullable=False)  # clinical, patent, market, web
    task_description = Column(Text, nullable=True)
    status = Column(String(50), default="pending", index=True)  # pending, running, completed, failed
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    query = relationship("Query", back_populates="tasks")


class Report(Base):
    """Generated analysis reports"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey("queries.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    report_metadata = Column("metadata", JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    query = relationship("Query", back_populates="reports")
    drug_candidates = relationship("DrugCandidate", back_populates="report", cascade="all, delete-orphan")


class DrugCandidate(Base):
    """Identified drug repurposing candidates"""
    __tablename__ = "drug_candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    drug_name = Column(String(255), nullable=False)
    indication = Column(String(500), nullable=True)
    confidence_score = Column(Float, nullable=True)
    market_data = Column(JSON, nullable=True)
    patent_data = Column(JSON, nullable=True)
    clinical_data = Column(JSON, nullable=True)
    web_intelligence = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    report = relationship("Report", back_populates="drug_candidates")


class Embedding(Base):
    """Vector embeddings for semantic search"""
    __tablename__ = "embeddings"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    embedding = Column(Text, nullable=True)  # Stored as JSON array or pgvector type
    embedding_metadata = Column("metadata", JSON, nullable=True)
    source = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
