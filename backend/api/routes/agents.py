"""
Agent management and monitoring endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from models.schemas import AgentStatusResponse, SystemStatus
from services.agent_service import AgentService

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/status", response_model=SystemStatus)
async def get_system_status(db: Session = Depends(get_db)):
    """
    Get overall system status
    
    Returns:
    - Agent health and statistics
    - Database connectivity
    - Redis connectivity
    """
    service = AgentService(db)
    system_status = await service.get_system_status()
    
    return system_status


@router.get("/{agent_type}/status", response_model=AgentStatusResponse)
async def get_agent_status(agent_type: str, db: Session = Depends(get_db)):
    """
    Get status for specific agent
    
    Parameters:
    - agent_type: clinical, patent, market, or web
    
    Returns:
    - Execution count
    - Success rate
    - Average execution time
    """
    valid_agents = ["clinical", "patent", "market", "web", "master"]
    
    if agent_type not in valid_agents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid agent type. Must be one of: {', '.join(valid_agents)}"
        )
    
    service = AgentService(db)
    agent_status = service.get_agent_status(agent_type)
    
    return agent_status


@router.post("/reset-stats", status_code=status.HTTP_204_NO_CONTENT)
async def reset_agent_statistics(db: Session = Depends(get_db)):
    """
    Reset all agent execution statistics
    
    This is useful for testing or when you want to clear historical metrics
    """
    service = AgentService(db)
    service.reset_statistics()
    
    return None
