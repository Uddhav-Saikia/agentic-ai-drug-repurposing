"""
Report service - business logic for report management
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json

from models.database_models import Report, DrugCandidate
from models.schemas import ReportResponse, ReportDetail, DrugCandidateResponse


class ReportService:
    """Service for managing reports and drug candidates"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_report(self, report_id: int) -> Optional[Report]:
        """Get report by ID"""
        return self.db.query(Report).filter(Report.id == report_id).first()
    
    def get_report_detail(self, report_id: int) -> Optional[ReportDetail]:
        """Get detailed report with parsed content"""
        report = self.get_report(report_id)
        if not report:
            return None
        
        metadata = report.report_metadata or {}
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
    
    def get_drug_candidates(self, report_id: int) -> List[DrugCandidateResponse]:
        """Get all drug candidates for a report"""
        candidates = self.db.query(DrugCandidate).filter(
            DrugCandidate.report_id == report_id
        ).all()
        
        return [DrugCandidateResponse.model_validate(c) for c in candidates]
    
    def list_reports(self, limit: int = 100, offset: int = 0) -> List[Report]:
        """List all reports"""
        return self.db.query(Report)\
            .order_by(Report.created_at.desc())\
            .offset(offset)\
            .limit(limit)\
            .all()
    
    def get_reports_by_query(self, query_id: int) -> List[Report]:
        """Get all reports for a specific query"""
        return self.db.query(Report)\
            .filter(Report.query_id == query_id)\
            .order_by(Report.created_at.desc())\
            .all()
    
    def create_report(
        self,
        query_id: int,
        title: str,
        content: str,
        summary: str,
        metadata: Dict[str, Any]
    ) -> Report:
        """Create a new report"""
        report = Report(
            query_id=query_id,
            title=title,
            content=content,
            summary=summary,
            report_metadata=metadata
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report
    
    def create_drug_candidate(
        self,
        report_id: int,
        drug_name: str,
        indication: str,
        confidence_score: float,
        market_data: Optional[Dict[str, Any]] = None,
        patent_data: Optional[Dict[str, Any]] = None,
        clinical_data: Optional[Dict[str, Any]] = None,
        web_intelligence: Optional[Dict[str, Any]] = None
    ) -> DrugCandidate:
        """Create a new drug candidate"""
        candidate = DrugCandidate(
            report_id=report_id,
            drug_name=drug_name,
            indication=indication,
            confidence_score=confidence_score,
            market_data=market_data,
            patent_data=patent_data,
            clinical_data=clinical_data,
            web_intelligence=web_intelligence
        )
        self.db.add(candidate)
        self.db.commit()
        self.db.refresh(candidate)
        return candidate
