"""
Clinical Intelligence Agent - Specialized in clinical trials analysis
"""
import time
from typing import List, Any
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

from agents.base_agent import BaseAgent, AgentTask, AgentResult
from agents.tools.clinical_tools import (
    ClinicalTrialsAPI,
    search_clinical_trials_tool
)
from core.config import settings


class ClinicalIntelligenceAgent(BaseAgent):
    """
    Specialized agent for analyzing clinical trials data from ClinicalTrials.gov
    
    Capabilities:
    - Search clinical trials by condition and drug
    - Analyze trial outcomes and phases
    - Assess clinical evidence strength
    """
    
    def __init__(self, llm: Any = None):
        """Initialize Clinical Intelligence Agent"""
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
            name="ClinicalIntelligenceAgent",
            description="Expert in clinical trials analysis and evidence assessment",
            llm=llm
        )
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """
        Execute clinical intelligence analysis
        
        Args:
            task: Task with parameters: condition, drug_name
            
        Returns:
            AgentResult with clinical trials analysis
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
            condition = task.parameters.get("condition", "")
            drug_name = task.parameters.get("drug_name", "")
            
            if not condition:
                return self._create_result(
                    task_id=task.task_id,
                    status="failed",
                    data={},
                    error="Condition parameter is required"
                )
            
            self.logger.info(f"Analyzing clinical trials for {condition} with {drug_name}")
            
            # Search clinical trials
            trials_data = ClinicalTrialsAPI.search_studies(
                condition=condition,
                drug_name=drug_name if drug_name else None,
                status=["COMPLETED", "RECRUITING", "ACTIVE_NOT_RECRUITING"],
                max_results=30
            )
            
            # Analyze outcomes if drug specified
            outcomes_data = {}
            if drug_name:
                outcomes_data = ClinicalTrialsAPI.analyze_study_outcomes(
                    condition=condition,
                    drug_name=drug_name
                )
            
            # Compile analysis
            studies = trials_data.get("studies", [])
            
            # Calculate clinical evidence score
            evidence_score = self._calculate_evidence_score(studies)
            
            # Analyze trial phases
            phase_analysis = self._analyze_phases(studies)
            
            # Identify key trials
            key_trials = self._identify_key_trials(studies, drug_name)
            
            execution_time = time.time() - start_time
            
            return self._create_result(
                task_id=task.task_id,
                status="success",
                data={
                    "condition": condition,
                    "drug_name": drug_name,
                    "total_trials": len(studies),
                    "trials_by_status": self._count_by_status(studies),
                    "phase_analysis": phase_analysis,
                    "evidence_score": evidence_score,
                    "key_trials": key_trials[:5],
                    "outcomes_analysis": outcomes_data,
                    "recommendation": self._generate_recommendation(
                        len(studies), 
                        evidence_score, 
                        phase_analysis
                    )
                },
                execution_time=execution_time,
                confidence_score=evidence_score / 10.0,  # Normalize to 0-1
                sources=["ClinicalTrials.gov"]
            )
            
        except Exception as e:
            self.logger.error(f"Clinical intelligence analysis failed: {e}")
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
                name="search_clinical_trials",
                func=lambda x: search_clinical_trials_tool(**eval(x) if isinstance(x, str) and x.startswith("{") else {"condition": x}),
                description="Search ClinicalTrials.gov for studies. Input should be a condition name or dict with 'condition' and optional 'drug_name'"
            )
        ]
    
    def _calculate_evidence_score(self, studies: List[dict]) -> float:
        """Calculate evidence strength score (0-10)"""
        if not studies:
            return 0.0
        
        score = 0.0
        
        # More trials = higher score (max 3 points)
        score += min(len(studies) / 10, 3.0)
        
        # Completed trials (max 3 points)
        completed = len([s for s in studies if s.get("status") == "COMPLETED"])
        score += min(completed / 5, 3.0)
        
        # Advanced phases (max 4 points)
        phase_3 = len([s for s in studies if "PHASE3" in str(s.get("phase", [])).upper()])
        phase_4 = len([s for s in studies if "PHASE4" in str(s.get("phase", [])).upper()])
        score += min((phase_3 * 1.5 + phase_4 * 2) / 5, 4.0)
        
        return round(min(score, 10.0), 2)
    
    def _analyze_phases(self, studies: List[dict]) -> dict:
        """Analyze distribution of trial phases"""
        phases = {
            "EARLY_PHASE1": 0,
            "PHASE1": 0,
            "PHASE2": 0,
            "PHASE3": 0,
            "PHASE4": 0
        }
        
        for study in studies:
            study_phases = study.get("phase", [])
            for phase in study_phases:
                phase_upper = phase.upper().replace(" ", "_")
                if phase_upper in phases:
                    phases[phase_upper] += 1
        
        return phases
    
    def _count_by_status(self, studies: List[dict]) -> dict:
        """Count trials by status"""
        status_counts = {}
        for study in studies:
            status = study.get("status", "UNKNOWN")
            status_counts[status] = status_counts.get(status, 0) + 1
        return status_counts
    
    def _identify_key_trials(self, studies: List[dict], drug_name: str) -> List[dict]:
        """Identify most relevant trials"""
        # Prioritize completed Phase 3/4 trials
        key_trials = []
        
        for study in studies:
            phases = study.get("phase", [])
            status = study.get("status", "")
            interventions = study.get("interventions", [])
            
            # Check if drug is mentioned in interventions
            drug_match = drug_name and any(
                drug_name.lower() in str(i).lower() 
                for i in interventions
            )
            
            relevance_score = 0
            if status == "COMPLETED":
                relevance_score += 3
            if "PHASE3" in str(phases).upper() or "PHASE4" in str(phases).upper():
                relevance_score += 2
            if drug_match:
                relevance_score += 2
            
            key_trials.append({
                "trial": study,
                "relevance_score": relevance_score
            })
        
        # Sort by relevance
        key_trials.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return [kt["trial"] for kt in key_trials]
    
    def _generate_recommendation(
        self, 
        total_trials: int, 
        evidence_score: float,
        phase_analysis: dict
    ) -> str:
        """Generate clinical recommendation"""
        if total_trials == 0:
            return "No clinical trials found. Further research needed."
        
        if evidence_score >= 7.0:
            return "Strong clinical evidence. Multiple trials with advanced phases."
        elif evidence_score >= 4.0:
            return "Moderate clinical evidence. Some trials in progress or completed."
        else:
            return "Limited clinical evidence. Early-stage or few trials available."
