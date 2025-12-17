"""
Market Intelligence Agent - Specialized in market analysis and competitive intelligence
"""
import time
from typing import List, Any
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI

from agents.base_agent import BaseAgent, AgentTask, AgentResult
from agents.tools.market_tools import (
    MarketIntelligenceAPI,
    get_market_size_tool,
    analyze_competition_tool
)
from core.config import settings


class MarketIntelligenceAgent(BaseAgent):
    """
    Specialized agent for market analysis and commercial assessment
    
    Capabilities:
    - Market size estimation
    - Competitive landscape analysis
    - Pricing and reimbursement data
    - Commercial viability assessment
    """
    
    def __init__(self, llm: Any = None):
        """Initialize Market Intelligence Agent"""
        if llm is None and settings.GEMINI_API_KEY:
            try:
                llm = ChatGoogleGenerativeAI(
                    model=settings.GEMINI_MODEL,
                    temperature=0.7,
                    google_api_key=settings.GEMINI_API_KEY
                )
            except Exception:
                llm = None  # Allow creation without LLM for testing
        
        super().__init__(
            name="MarketIntelligenceAgent",
            description="Expert in market analysis and commercial intelligence",
            llm=llm
        )
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """
        Execute market intelligence analysis
        
        Args:
            task: Task with parameters: condition, drug_name (optional), region
            
        Returns:
            AgentResult with market analysis
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
            region = task.parameters.get("region", "Global")
            
            if not condition:
                return self._create_result(
                    task_id=task.task_id,
                    status="failed",
                    data={},
                    error="Condition parameter is required"
                )
            
            self.logger.info(f"Analyzing market for {condition} in {region}")
            
            # Get market size data
            market_size = MarketIntelligenceAPI.get_market_size(
                condition=condition,
                region=region
            )
            
            # Analyze competitive landscape
            competition = MarketIntelligenceAPI.analyze_competitive_landscape(
                condition=condition
            )
            
            # Get pricing data if drug specified
            pricing_data = {}
            if drug_name:
                pricing_data = MarketIntelligenceAPI.get_pricing_data(
                    drug_name=drug_name,
                    region=region
                )
            
            # Calculate market attractiveness score
            attractiveness_score = self._calculate_market_attractiveness(
                market_size,
                competition
            )
            
            # Assess commercial viability
            viability_assessment = self._assess_commercial_viability(
                market_size,
                competition,
                attractiveness_score
            )
            
            execution_time = time.time() - start_time
            
            return self._create_result(
                task_id=task.task_id,
                status="success",
                data={
                    "condition": condition,
                    "drug_name": drug_name,
                    "region": region,
                    "market_size": market_size,
                    "competitive_landscape": competition,
                    "pricing_data": pricing_data,
                    "attractiveness_score": attractiveness_score,
                    "viability_assessment": viability_assessment,
                    "recommendation": self._generate_recommendation(
                        attractiveness_score,
                        market_size,
                        competition
                    )
                },
                execution_time=execution_time,
                confidence_score=0.75,  # Market data has some uncertainty
                sources=["IQVIA", "Market Reports", "Industry Analysis"]
            )
            
        except Exception as e:
            self.logger.error(f"Market intelligence analysis failed: {e}")
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
                name="get_market_size",
                func=lambda x: get_market_size_tool(**eval(x) if isinstance(x, str) and x.startswith("{") else {"condition": x}),
                description="Get market size for a condition. Input should be condition name or dict with 'condition' and optional 'region'"
            ),
            Tool(
                name="analyze_competition",
                func=analyze_competition_tool,
                description="Analyze competitive landscape for a condition. Input should be a condition name"
            )
        ]
    
    def _calculate_market_attractiveness(
        self, 
        market_size: dict,
        competition: dict
    ) -> float:
        """Calculate market attractiveness score (0-10)"""
        score = 0.0
        
        # Market size factor (max 4 points)
        size_usd = market_size.get("market_size_usd", 0)
        if size_usd > 20e9:  # >$20B
            score += 4.0
        elif size_usd > 10e9:  # >$10B
            score += 3.0
        elif size_usd > 5e9:  # >$5B
            score += 2.0
        else:
            score += 1.0
        
        # Growth factor (max 3 points)
        cagr = market_size.get("projected_cagr", 0)
        if cagr > 10:
            score += 3.0
        elif cagr > 7:
            score += 2.0
        elif cagr > 4:
            score += 1.0
        
        # Competition factor (max 3 points)
        # Lower competition = higher score
        top_3_share = competition.get("top_3_market_share", 100)
        if top_3_share < 50:  # Fragmented market
            score += 3.0
        elif top_3_share < 70:
            score += 2.0
        else:  # Concentrated market
            score += 1.0
        
        return round(min(score, 10.0), 2)
    
    def _assess_commercial_viability(
        self,
        market_size: dict,
        competition: dict,
        attractiveness_score: float
    ) -> dict:
        """Assess commercial viability"""
        # Calculate patient opportunity
        patient_pop = market_size.get("patient_population", 0)
        treatment_rate = market_size.get("treatment_rate", 0)
        untreated_patients = patient_pop * (1 - treatment_rate)
        
        # Assess market entry barriers
        approved_drugs = len(competition.get("approved_drugs", []))
        pipeline_drugs = len(competition.get("pipeline_drugs", []))
        
        if approved_drugs < 3:
            entry_barrier = "Low"
        elif approved_drugs < 7:
            entry_barrier = "Moderate"
        else:
            entry_barrier = "High"
        
        # Overall viability
        if attractiveness_score >= 7:
            viability = "High"
            description = "Attractive market with strong growth potential"
        elif attractiveness_score >= 4:
            viability = "Moderate"
            description = "Reasonable market opportunity with some challenges"
        else:
            viability = "Low"
            description = "Limited market potential or high competition"
        
        return {
            "viability_level": viability,
            "description": description,
            "untreated_patient_population": int(untreated_patients),
            "market_entry_barrier": entry_barrier,
            "competitive_intensity": "High" if approved_drugs > 5 else "Moderate",
            "key_success_factors": self._identify_success_factors(
                market_size,
                competition
            )
        }
    
    def _identify_success_factors(
        self,
        market_size: dict,
        competition: dict
    ) -> List[str]:
        """Identify key success factors for market entry"""
        factors = []
        
        cagr = market_size.get("projected_cagr", 0)
        if cagr > 8:
            factors.append("Strong market growth supports new entrants")
        
        approved_drugs = len(competition.get("approved_drugs", []))
        if approved_drugs < 5:
            factors.append("Limited competition creates opportunities")
        
        factors.append("Differentiated value proposition essential")
        factors.append("Strong clinical data required for market access")
        factors.append("Favorable pricing and reimbursement critical")
        
        return factors
    
    def _generate_recommendation(
        self,
        attractiveness_score: float,
        market_size: dict,
        competition: dict
    ) -> str:
        """Generate market recommendation"""
        size_b = market_size.get("market_size_usd", 0) / 1e9
        cagr = market_size.get("projected_cagr", 0)
        
        if attractiveness_score >= 7:
            return f"Highly attractive market (${size_b:.1f}B, {cagr}% CAGR). Strong commercial opportunity."
        elif attractiveness_score >= 4:
            return f"Moderately attractive market (${size_b:.1f}B, {cagr}% CAGR). Competitive but viable."
        else:
            return f"Limited market attractiveness (${size_b:.1f}B, {cagr}% CAGR). High competition or slow growth."
