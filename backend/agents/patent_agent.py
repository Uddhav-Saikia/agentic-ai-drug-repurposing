"""
Patent Landscape Agent - Specialized in IP and freedom-to-operate analysis
"""
import time
from typing import List, Any
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

from agents.base_agent import BaseAgent, AgentTask, AgentResult
from agents.tools.patent_tools import (
    USPTOPatentAPI,
    search_patents_tool,
    analyze_patent_landscape_tool
)
from core.config import settings


class PatentLandscapeAgent(BaseAgent):
    """
    Specialized agent for patent analysis and freedom-to-operate assessment
    
    Capabilities:
    - Search USPTO patent database
    - Analyze patent landscape
    - Assess freedom-to-operate risks
    - Identify patent barriers
    """
    
    def __init__(self, llm: Any = None):
        """Initialize Patent Landscape Agent"""
        if llm is None and settings.OPENAI_API_KEY:
            try:
                llm = ChatOpenAI(
                    model=settings.OPENAI_MODEL,
                    temperature=0.3,
                    api_key=settings.OPENAI_API_KEY
                )
            except Exception:
                llm = None  # Allow creation without LLM for testing
        
        super().__init__(
            name="PatentLandscapeAgent",
            description="Expert in patent analysis and IP landscape assessment",
            llm=llm
        )
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """
        Execute patent landscape analysis
        
        Args:
            task: Task with parameters: drug_name, condition (optional)
            
        Returns:
            AgentResult with patent analysis
        """
        start_time = time.time()
        
        try:
            if not self.validate_task(task):
                return self._create_result(
                    task_id=task.task_id,
                    status="failed",
                    data={},
                    error="Invalid task parameters"
                )
            
            # Extract parameters
            drug_name = task.parameters.get("drug_name", "")
            condition = task.parameters.get("condition", "")
            
            if not drug_name:
                return self._create_result(
                    task_id=task.task_id,
                    status="failed",
                    data={},
                    error="Drug name parameter is required"
                )
            
            self.logger.info(f"Analyzing patent landscape for {drug_name}")
            
            # Search patents
            patent_data = USPTOPatentAPI.search_patents(
                drug_name=drug_name,
                condition=condition if condition else None,
                max_results=50
            )
            
            # Analyze patent landscape
            landscape_analysis = USPTOPatentAPI.analyze_patent_landscape(drug_name)
            
            # Compile results
            patents = patent_data.get("patents", [])
            
            # Assess IP barriers
            ip_assessment = self._assess_ip_barriers(landscape_analysis)
            
            # Identify key patents
            key_patents = self._identify_key_patents(patents)
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(landscape_analysis)
            
            execution_time = time.time() - start_time
            
            return self._create_result(
                task_id=task.task_id,
                status="success",
                data={
                    "drug_name": drug_name,
                    "condition": condition,
                    "total_patents": len(patents),
                    "active_patents": landscape_analysis.get("active_patents", 0),
                    "expired_patents": landscape_analysis.get("expired_patents", 0),
                    "patent_landscape": landscape_analysis,
                    "ip_assessment": ip_assessment,
                    "key_patents": key_patents[:5],
                    "risk_score": risk_score,
                    "recommendation": self._generate_recommendation(
                        landscape_analysis,
                        risk_score
                    )
                },
                execution_time=execution_time,
                confidence_score=0.8,  # Patent data is generally reliable
                sources=["USPTO Patent Database"]
            )
            
        except Exception as e:
            self.logger.error(f"Patent landscape analysis failed: {e}")
            return self._create_result(
                task_id=task.task_id,
                status="failed",
                data={},
                error=str(e),
                execution_time=time.time() - start_time
            )
    
    def get_tools(self) -> List[Tool]:
        """Get LangChain tools for this agent"""
        return [
            Tool(
                name="search_patents",
                func=lambda x: search_patents_tool(**eval(x) if isinstance(x, str) and x.startswith("{") else {"drug_name": x}),
                description="Search USPTO patents for a drug. Input should be a drug name or dict with 'drug_name' and optional 'condition'"
            ),
            Tool(
                name="analyze_patent_landscape",
                func=analyze_patent_landscape_tool,
                description="Analyze patent landscape for a drug. Input should be a drug name"
            )
        ]
    
    def _assess_ip_barriers(self, landscape: dict) -> dict:
        """Assess intellectual property barriers"""
        active_patents = landscape.get("active_patents", 0)
        fto = landscape.get("freedom_to_operate", {})
        
        if active_patents == 0:
            barrier_level = "Low"
            description = "No active patent barriers identified"
        elif active_patents <= 5:
            barrier_level = "Moderate"
            description = "Some active patents exist, but landscape is relatively clear"
        elif active_patents <= 15:
            barrier_level = "High"
            description = "Significant patent barriers present, careful navigation required"
        else:
            barrier_level = "Very High"
            description = "Extensive patent protection, high risk of infringement"
        
        return {
            "barrier_level": barrier_level,
            "description": description,
            "active_patent_count": active_patents,
            "freedom_to_operate": fto,
            "mitigation_strategies": self._suggest_mitigation_strategies(active_patents)
        }
    
    def _identify_key_patents(self, patents: List[dict]) -> List[dict]:
        """Identify most important patents"""
        key_patents = []
        
        for patent in patents:
            importance_score = 0
            
            # Active patents are more important
            if patent.get("status") == "Active":
                importance_score += 3
            
            # More citations = more important
            citations = patent.get("citations", 0)
            importance_score += min(citations / 5, 2)
            
            # More claims = broader coverage
            claims = patent.get("claims_count", 0)
            importance_score += min(claims / 20, 2)
            
            key_patents.append({
                "patent": patent,
                "importance_score": importance_score
            })
        
        # Sort by importance
        key_patents.sort(key=lambda x: x["importance_score"], reverse=True)
        
        return [kp["patent"] for kp in key_patents]
    
    def _calculate_risk_score(self, landscape: dict) -> float:
        """Calculate IP risk score (0-10, higher = more risk)"""
        active_patents = landscape.get("active_patents", 0)
        
        # Base risk on active patents
        risk = min(active_patents / 2, 10.0)
        
        return round(risk, 2)
    
    def _suggest_mitigation_strategies(self, active_patents: int) -> List[str]:
        """Suggest strategies to mitigate IP risks"""
        strategies = []
        
        if active_patents > 10:
            strategies.append("Consider licensing agreements with key patent holders")
            strategies.append("Explore alternative formulations or delivery methods")
            strategies.append("Conduct comprehensive freedom-to-operate analysis")
        elif active_patents > 5:
            strategies.append("Review patent claims for potential design-around opportunities")
            strategies.append("Monitor patent expiration dates")
        else:
            strategies.append("Standard patent clearance procedures should suffice")
        
        strategies.append("Consult with patent attorney for detailed analysis")
        
        return strategies
    
    def _generate_recommendation(self, landscape: dict, risk_score: float) -> str:
        """Generate patent recommendation"""
        fto = landscape.get("freedom_to_operate", {})
        risk_level = fto.get("risk_level", "Unknown")
        
        if risk_score <= 3.0:
            return f"Low IP risk ({risk_level}). Favorable patent landscape for development."
        elif risk_score <= 6.0:
            return f"Moderate IP risk ({risk_level}). Patent clearance recommended before proceeding."
        else:
            return f"High IP risk ({risk_level}). Significant patent barriers. Detailed FTO analysis essential."
