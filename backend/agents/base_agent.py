"""
Base Agent Class - Abstract interface for all specialized agents
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AgentTask(BaseModel):
    """Represents a task assigned to an agent"""
    task_id: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 1
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentResult(BaseModel):
    """Represents the result from an agent execution"""
    agent_name: str
    task_id: str
    status: str  # success, failed, partial
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    execution_time: float = 0.0
    confidence_score: float = 0.0
    sources: List[str] = Field(default_factory=list)
    completed_at: datetime = Field(default_factory=datetime.utcnow)


class BaseAgent(ABC):
    """
    Abstract base class for all specialized agents in the drug repurposing system.
    
    All worker agents (Clinical, Patent, Market, Web Intelligence) inherit from this class.
    """
    
    def __init__(self, name: str, description: str, llm: Optional[Any] = None):
        """
        Initialize base agent
        
        Args:
            name: Agent name/identifier
            description: Agent's role and capabilities
            llm: Language model instance (OpenAI, etc.)
        """
        self.name = name
        self.description = description
        self.llm = llm
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.execution_count = 0
        self.success_count = 0
        
    @abstractmethod
    async def execute(self, task: AgentTask) -> AgentResult:
        """
        Execute the assigned task
        
        Args:
            task: AgentTask containing task details and parameters
            
        Returns:
            AgentResult with execution results
        """
        pass
    
    @abstractmethod
    def get_tools(self) -> List[Any]:
        """
        Get the tools/functions available to this agent
        
        Returns:
            List of LangChain tools
        """
        pass
    
    def validate_task(self, task: AgentTask) -> bool:
        """
        Validate if the task can be executed by this agent
        
        Args:
            task: Task to validate
            
        Returns:
            True if task is valid, False otherwise
        """
        if not task.description:
            self.logger.error("Task description is empty")
            return False
        return True
    
    def _create_result(
        self,
        task_id: str,
        status: str,
        data: Dict[str, Any],
        error: Optional[str] = None,
        execution_time: float = 0.0,
        confidence_score: float = 0.0,
        sources: Optional[List[str]] = None
    ) -> AgentResult:
        """
        Helper method to create AgentResult
        
        Args:
            task_id: ID of the completed task
            status: Execution status
            data: Result data
            error: Error message if failed
            execution_time: Time taken to execute
            confidence_score: Confidence in results (0-1)
            sources: Data sources used
            
        Returns:
            AgentResult object
        """
        self.execution_count += 1
        if status == "success":
            self.success_count += 1
            
        return AgentResult(
            agent_name=self.name,
            task_id=task_id,
            status=status,
            data=data,
            error=error,
            execution_time=execution_time,
            confidence_score=confidence_score,
            sources=sources or [],
            completed_at=datetime.utcnow()
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get agent execution statistics
        
        Returns:
            Dictionary with stats
        """
        success_rate = (
            self.success_count / self.execution_count 
            if self.execution_count > 0 else 0.0
        )
        
        return {
            "name": self.name,
            "executions": self.execution_count,
            "successes": self.success_count,
            "success_rate": success_rate
        }
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
