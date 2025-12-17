"""
Query service - business logic for query management
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.database_models import Query, Task, Report, DrugCandidate
from models.schemas import QueryCreate, QueryResponse, QueryStatus, AnalysisResult, TaskResponse, ReportDetail, DrugCandidateResponse


class QueryService:
    """Service for managing queries and their execution"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_query(self, query_data: QueryCreate) -> Query:
        """Create a new query"""
        query = Query(
            query_text=query_data.query_text,
            user_id=query_data.user_id,
            status="pending"
        )
        self.db.add(query)
        self.db.commit()
        self.db.refresh(query)
        return query
    
    def get_query(self, query_id: int) -> Optional[Query]:
        """Get query by ID"""
        return self.db.query(Query).filter(Query.id == query_id).first()
    
    def get_query_status(self, query_id: int) -> Optional[QueryStatus]:
        """Get detailed query status with progress"""
        query = self.get_query(query_id)
        if not query:
            return None
        
        # Get all tasks for this query
        tasks = self.db.query(Task).filter(Task.query_id == query_id).all()
        
        # Calculate progress
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == "completed")
        failed_tasks = sum(1 for t in tasks if t.status == "failed")
        running_tasks = sum(1 for t in tasks if t.status == "running")
        
        progress = {
            "total": total_tasks,
            "completed": completed_tasks,
            "failed": failed_tasks,
            "running": running_tasks,
            "percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "tasks": [
                {
                    "agent_type": t.agent_type,
                    "status": t.status,
                    "started_at": t.started_at.isoformat() if t.started_at else None,
                    "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                }
                for t in tasks
            ]
        }
        
        # Determine message
        if query.status == "completed":
            message = "Analysis complete"
        elif query.status == "failed":
            message = f"Analysis failed: {failed_tasks} task(s) failed"
        elif query.status == "processing":
            message = f"Processing: {completed_tasks}/{total_tasks} tasks completed"
        else:
            message = "Query pending"
        
        return QueryStatus(
            id=query.id,
            status=query.status,
            progress=progress,
            message=message
        )
    
    def get_analysis_result(self, query_id: int) -> Optional[AnalysisResult]:
        """Get complete analysis result"""
        query = self.get_query(query_id)
        if not query:
            return None
        
        # Get tasks
        tasks = self.db.query(Task).filter(Task.query_id == query_id).all()
        task_responses = [TaskResponse.model_validate(t) for t in tasks]
        
        # Get report
        report = self.db.query(Report).filter(Report.query_id == query_id).first()
        report_detail = None
        drug_candidates = []
        
        if report:
            # Parse report content into structured format
            report_detail = self._parse_report(report)
            
            # Get drug candidates
            candidates = self.db.query(DrugCandidate).filter(DrugCandidate.report_id == report.id).all()
            drug_candidates = [DrugCandidateResponse.model_validate(c) for c in candidates]
        
        return AnalysisResult(
            query=QueryResponse.model_validate(query),
            tasks=task_responses,
            report=report_detail,
            drug_candidates=drug_candidates,
            status=query.status,
            message=f"Found {len(drug_candidates)} drug candidates" if drug_candidates else None
        )
    
    def list_queries(
        self,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Query]:
        """List queries with filters"""
        query = self.db.query(Query)
        
        if user_id:
            query = query.filter(Query.user_id == user_id)
        
        if status:
            query = query.filter(Query.status == status)
        
        query = query.order_by(Query.created_at.desc())
        query = query.offset(offset).limit(limit)
        
        return query.all()
    
    def delete_query(self, query_id: int) -> bool:
        """Delete query (cascade deletes tasks, reports, candidates)"""
        query = self.get_query(query_id)
        if not query:
            return False
        
        self.db.delete(query)
        self.db.commit()
        return True
    
    def update_query_status(self, query_id: int, status: str) -> Optional[Query]:
        """Update query status"""
        query = self.get_query(query_id)
        if not query:
            return None
        
        query.status = status
        query.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(query)
        return query
    
    def _parse_report(self, report: Report) -> ReportDetail:
        """Parse report content into structured format"""
        metadata = report.report_metadata or {}
        
        # Extract sections from metadata
        sections = metadata.get("sections", {})
        
        return ReportDetail(
            id=report.id,
            query_id=report.query_id,
            title=report.title,
            executive_summary=metadata.get("executive_summary"),
            condition=metadata.get("condition"),
            drug_name=metadata.get("drug_name"),
            overall_confidence=metadata.get("overall_confidence"),
            sections=sections,
            key_findings=metadata.get("key_findings", []),
            recommendations=metadata.get("recommendations", {}),
            risk_assessment=metadata.get("risk_assessment", {}),
            next_steps=metadata.get("next_steps", []),
            data_sources=metadata.get("data_sources", []),
            metadata=metadata,
            created_at=report.created_at
        )
