"""
Agent service - business logic for agent monitoring and statistics
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from datetime import datetime
import redis

from models.database_models import Task
from models.schemas import AgentStatusResponse, SystemStatus
from core.config import settings


class AgentService:
    """Service for monitoring agents and system health"""
    
    def __init__(self, db: Session):
        self.db = db
        try:
            self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        except Exception:
            self.redis_client = None
    
    async def get_system_status(self) -> SystemStatus:
        """Get overall system health status"""
        # Check database
        db_status = "healthy"
        try:
            self.db.execute("SELECT 1")
        except Exception:
            db_status = "unhealthy"
        
        # Check Redis
        redis_status = "healthy"
        if self.redis_client:
            try:
                self.redis_client.ping()
            except Exception:
                redis_status = "unhealthy"
        else:
            redis_status = "unavailable"
        
        # Get agent statistics
        agent_types = ["clinical", "patent", "market", "web", "master"]
        agent_statuses = [
            self.get_agent_status(agent_type)
            for agent_type in agent_types
        ]
        
        # Determine overall status
        if db_status == "healthy" and redis_status in ["healthy", "unavailable"]:
            overall_status = "healthy"
        else:
            overall_status = "degraded"
        
        return SystemStatus(
            status=overall_status,
            agents=agent_statuses,
            database=db_status,
            redis=redis_status,
            timestamp=datetime.utcnow()
        )
    
    def get_agent_status(self, agent_type: str) -> AgentStatusResponse:
        """Get statistics for a specific agent"""
        # Query tasks for this agent type
        tasks = self.db.query(Task).filter(Task.agent_type == agent_type).all()
        
        total_executions = len(tasks)
        successful = sum(1 for t in tasks if t.status == "completed")
        failed = sum(1 for t in tasks if t.status == "failed")
        
        success_rate = (successful / total_executions * 100) if total_executions > 0 else 0.0
        
        # Calculate average execution time
        execution_times = []
        for task in tasks:
            if task.started_at and task.completed_at:
                duration = (task.completed_at - task.started_at).total_seconds()
                execution_times.append(duration)
        
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else None
        
        # Determine status
        if total_executions == 0:
            status = "idle"
        elif failed / total_executions > 0.5 if total_executions > 0 else False:
            status = "unhealthy"
        else:
            status = "healthy"
        
        return AgentStatusResponse(
            agent_name=agent_type,
            status=status,
            executions=total_executions,
            success_rate=success_rate,
            average_execution_time=avg_execution_time
        )
    
    def reset_statistics(self):
        """Reset all agent statistics (for testing)"""
        # In a production system, you might want to archive this data
        # For now, we'll just clear the Redis cache if available
        if self.redis_client:
            try:
                self.redis_client.flushdb()
            except Exception:
                pass
