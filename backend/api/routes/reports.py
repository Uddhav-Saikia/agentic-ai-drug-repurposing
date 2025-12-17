"""
Report endpoints - placeholder for Phase 3
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_reports():
    """List reports - to be implemented in Phase 3"""
    return {"message": "Reports endpoint - to be implemented in Phase 3"}
