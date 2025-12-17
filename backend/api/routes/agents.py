"""
Agent endpoints - placeholder for Phase 3
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def agent_status():
    """Get agent status - to be implemented in Phase 3"""
    return {"message": "Agent status endpoint - to be implemented in Phase 3"}
