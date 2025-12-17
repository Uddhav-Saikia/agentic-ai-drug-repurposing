"""
Query API endpoints for drug repurposing analysis
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from core.database import get_db
from models.schemas import QueryCreate, QueryResponse, QueryStatus, AnalysisResult
from models.database_models import Query, Task, Report
from services.query_service import QueryService
from services.celery_tasks import run_analysis_task

router = APIRouter(prefix="/queries", tags=["queries"])


@router.post("/", response_model=QueryResponse, status_code=status.HTTP_201_CREATED)
async def create_query(
    query_data: QueryCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Submit a new drug repurposing query
    
    This endpoint accepts a natural language query and initiates analysis:
    - Creates query record in database
    - Triggers Master Agent orchestration asynchronously
    - Returns query ID for status tracking
    
    Example queries:
    - "Find drug repurposing opportunities for Alzheimer's disease"
    - "Analyze potential of metformin for type 2 diabetes treatment"
    - "What drugs could be repurposed for COVID-19 treatment?"
    """
    service = QueryService(db)
    
    # Create query record
    query = service.create_query(query_data)
    
    # Trigger background analysis task
    background_tasks.add_task(run_analysis_task, query.id)
    
    return query


@router.get("/{query_id}", response_model=QueryResponse)
async def get_query(query_id: int, db: Session = Depends(get_db)):
    """
    Get query details by ID
    
    Returns basic query information including status
    """
    service = QueryService(db)
    query = service.get_query(query_id)
    
    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Query with ID {query_id} not found"
        )
    
    return query


@router.get("/{query_id}/status", response_model=QueryStatus)
async def get_query_status(query_id: int, db: Session = Depends(get_db)):
    """
    Get detailed query status with progress information
    
    Returns:
    - Current status (pending, processing, completed, failed)
    - Progress breakdown by agent
    - Completion percentage
    - Error messages if any
    """
    service = QueryService(db)
    status_info = service.get_query_status(query_id)
    
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Query with ID {query_id} not found"
        )
    
    return status_info


@router.get("/{query_id}/result", response_model=AnalysisResult)
async def get_analysis_result(query_id: int, db: Session = Depends(get_db)):
    """
    Get complete analysis result including report and drug candidates
    
    Returns full analysis when status is 'completed':
    - Query information
    - Task execution details
    - Generated report with all sections
    - Identified drug candidates
    """
    service = QueryService(db)
    result = service.get_analysis_result(query_id)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Query with ID {query_id} not found"
        )
    
    if result.status == "processing":
        raise HTTPException(
            status_code=status.HTTP_202_ACCEPTED,
            detail="Analysis is still in progress"
        )
    
    return result


@router.get("/", response_model=List[QueryResponse])
async def list_queries(
    user_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List queries with optional filtering
    
    Parameters:
    - user_id: Filter by user
    - status: Filter by status (pending, processing, completed, failed)
    - limit: Maximum number of results
    - offset: Pagination offset
    """
    service = QueryService(db)
    queries = service.list_queries(
        user_id=user_id,
        status=status,
        limit=limit,
        offset=offset
    )
    
    return queries


@router.delete("/{query_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_query(query_id: int, db: Session = Depends(get_db)):
    """
    Delete a query and all associated data
    
    This will cascade delete:
    - All tasks
    - All reports
    - All drug candidates
    """
    service = QueryService(db)
    success = service.delete_query(query_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Query with ID {query_id} not found"
        )
    
    return None
