"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


# Query Schemas
class QueryCreate(BaseModel):
    """Schema for creating a new query"""
    query_text: str = Field(..., min_length=10, max_length=2000, description="Natural language query")
    user_id: Optional[str] = Field(None, description="User identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query_text": "Find drug repurposing opportunities for Alzheimer's disease",
                "user_id": "user123"
            }
        }


class QueryResponse(BaseModel):
    """Schema for query response"""
    id: int
    query_text: str
    status: str
    user_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class QueryStatus(BaseModel):
    """Schema for query status"""
    id: int
    status: str
    progress: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


# Task Schemas
class TaskResponse(BaseModel):
    """Schema for task response"""
    id: int
    query_id: int
    agent_type: str
    status: str
    task_description: Optional[str]
    result: Optional[Dict[str, Any]]
    error: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Report Schemas
class ReportResponse(BaseModel):
    """Schema for report response"""
    id: int
    query_id: int
    title: Optional[str]
    content: Optional[str]
    summary: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReportDetail(BaseModel):
    """Schema for detailed report with all sections"""
    id: int
    query_id: int
    title: Optional[str]
    executive_summary: Optional[str]
    condition: Optional[str]
    drug_name: Optional[str]
    overall_confidence: Optional[float]
    sections: Optional[Dict[str, Any]]
    key_findings: Optional[List[str]]
    recommendations: Optional[Dict[str, str]]
    risk_assessment: Optional[Dict[str, str]]
    next_steps: Optional[List[str]]
    data_sources: Optional[List[str]]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Drug Candidate Schemas
class DrugCandidateResponse(BaseModel):
    """Schema for drug candidate response"""
    id: int
    report_id: int
    drug_name: str
    indication: Optional[str]
    confidence_score: Optional[float]
    market_data: Optional[Dict[str, Any]]
    patent_data: Optional[Dict[str, Any]]
    clinical_data: Optional[Dict[str, Any]]
    web_intelligence: Optional[Dict[str, Any]]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Analysis Result Schema
class AnalysisResult(BaseModel):
    """Complete analysis result"""
    query: QueryResponse
    tasks: List[TaskResponse]
    report: Optional[ReportDetail]
    drug_candidates: List[DrugCandidateResponse] = []
    status: str
    message: Optional[str] = None


# Agent Status Schema
class AgentStatusResponse(BaseModel):
    """Agent health and status"""
    agent_name: str
    status: str
    executions: int
    success_rate: float
    average_execution_time: Optional[float] = None


class SystemStatus(BaseModel):
    """Overall system status"""
    status: str
    agents: List[AgentStatusResponse]
    database: str
    redis: str
    timestamp: datetime
