"""
Report API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from models.schemas import ReportResponse, ReportDetail, DrugCandidateResponse
from services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/{report_id}", response_model=ReportDetail)
async def get_report(report_id: int, db: Session = Depends(get_db)):
    """
    Get detailed report by ID
    
    Returns complete report with all analysis sections:
    - Executive summary
    - Clinical intelligence
    - Patent landscape
    - Market intelligence
    - Web intelligence
    - Risk assessment
    - Recommendations
    """
    service = ReportService(db)
    report = service.get_report_detail(report_id)
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report with ID {report_id} not found"
        )
    
    return report


@router.get("/{report_id}/candidates", response_model=List[DrugCandidateResponse])
async def get_drug_candidates(report_id: int, db: Session = Depends(get_db)):
    """
    Get all drug candidates identified in a report
    
    Returns list of drug candidates with:
    - Drug name and indication
    - Confidence score
    - Clinical, patent, market, and web intelligence data
    """
    service = ReportService(db)
    candidates = service.get_drug_candidates(report_id)
    
    return candidates


@router.get("/", response_model=List[ReportResponse])
async def list_reports(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List all reports with pagination
    """
    service = ReportService(db)
    reports = service.list_reports(limit=limit, offset=offset)
    
    return reports


@router.get("/query/{query_id}", response_model=List[ReportResponse])
async def get_reports_by_query(query_id: int, db: Session = Depends(get_db)):
    """
    Get all reports for a specific query
    """
    service = ReportService(db)
    reports = service.get_reports_by_query(query_id)
    
    return reports
