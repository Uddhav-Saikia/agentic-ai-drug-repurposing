"""
Web Intelligence Agent - Specialized in literature and web data analysis
"""
import time
from typing import List, Any
from langchain.tools import Tool
from langchain_openai import ChatOpenAI

from agents.base_agent import BaseAgent, AgentTask, AgentResult
from agents.tools.web_tools import (
    PubMedAPI,
    WebIntelligence,
    search_pubmed_tool,
    analyze_literature_trends_tool
)
from core.config import settings


class WebIntelligenceAgent(BaseAgent):
    """
    Specialized agent for web intelligence and literature analysis
    
    Capabilities:
    - PubMed literature search
    - Publication trend analysis
    - Research focus identification
    - News and public data gathering
    """
    
    def __init__(self, llm: Any = None):
        """Initialize Web Intelligence Agent"""
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
            name="WebIntelligenceAgent",
            description="Expert in literature analysis and web intelligence gathering",
            llm=llm
        )
    
    async def execute(self, task: AgentTask) -> AgentResult:
        """
        Execute web intelligence analysis
        
        Args:
            task: Task with parameters: condition, drug_name
            
        Returns:
            AgentResult with web intelligence analysis
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
            
            if not condition or not drug_name:
                return self._create_result(
                    task_id=task.task_id,
                    status="failed",
                    data={},
                    error="Both condition and drug_name parameters are required"
                )
            
            self.logger.info(f"Gathering web intelligence for {drug_name} and {condition}")
            
            # Search PubMed literature
            literature_data = PubMedAPI.search_literature(
                drug_name=drug_name,
                condition=condition,
                max_results=50
            )
            
            # Analyze literature trends
            trend_analysis = PubMedAPI.analyze_literature_trends(
                drug_name=drug_name,
                condition=condition
            )
            
            # Search news articles (mock for now)
            news_data = WebIntelligence.search_news_articles(
                drug_name=drug_name,
                condition=condition
            )
            
            # Compile analysis
            articles = literature_data.get("articles", [])
            
            # Calculate research momentum score
            momentum_score = self._calculate_research_momentum(
                trend_analysis,
                len(articles)
            )
            
            # Identify research themes
            research_themes = self._identify_research_themes(articles)
            
            # Extract key findings
            key_findings = self._extract_key_findings(articles[:10])
            
            execution_time = time.time() - start_time
            
            return self._create_result(
                task_id=task.task_id,
                status="success",
                data={
                    "condition": condition,
                    "drug_name": drug_name,
                    "total_publications": len(articles),
                    "literature_data": literature_data,
                    "trend_analysis": trend_analysis,
                    "news_data": news_data,
                    "research_momentum_score": momentum_score,
                    "research_themes": research_themes,
                    "key_findings": key_findings,
                    "recommendation": self._generate_recommendation(
                        momentum_score,
                        trend_analysis,
                        len(articles)
                    )
                },
                execution_time=execution_time,
                confidence_score=0.85,  # Literature data is generally reliable
                sources=["PubMed", "NCBI", "News Sources"]
            )
            
        except Exception as e:
            self.logger.error(f"Web intelligence analysis failed: {e}")
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
                name="search_pubmed",
                func=lambda x: search_pubmed_tool(**eval(x) if isinstance(x, str) and x.startswith("{") else {"drug_name": x.split(" and ")[0], "condition": x.split(" and ")[1] if " and " in x else ""}),
                description="Search PubMed for literature. Input should be dict with 'drug_name' and 'condition' or string like 'drug_name and condition'"
            ),
            Tool(
                name="analyze_literature_trends",
                func=lambda x: analyze_literature_trends_tool(**eval(x) if isinstance(x, str) and x.startswith("{") else {"drug_name": x.split(" and ")[0], "condition": x.split(" and ")[1] if " and " in x else ""}),
                description="Analyze publication trends. Input should be dict with 'drug_name' and 'condition'"
            )
        ]
    
    def _calculate_research_momentum(
        self,
        trend_analysis: dict,
        total_pubs: int
    ) -> float:
        """Calculate research momentum score (0-10)"""
        score = 0.0
        
        # Publication volume (max 4 points)
        if total_pubs > 50:
            score += 4.0
        elif total_pubs > 20:
            score += 3.0
        elif total_pubs > 10:
            score += 2.0
        elif total_pubs > 0:
            score += 1.0
        
        # Trend direction (max 3 points)
        trend = trend_analysis.get("publication_trend", "")
        if trend == "Increasing":
            score += 3.0
        elif trend == "Stable":
            score += 1.5
        
        # Recent activity (max 3 points)
        year_dist = trend_analysis.get("year_distribution", {})
        if year_dist:
            recent_years = [y for y in year_dist.keys() if int(y) >= 2020]
            recent_count = sum([year_dist[y] for y in recent_years])
            score += min(recent_count / 10, 3.0)
        
        return round(min(score, 10.0), 2)
    
    def _identify_research_themes(self, articles: List[dict]) -> List[str]:
        """Identify main research themes from articles"""
        themes = []
        
        # Analyze publication types
        pub_types = []
        for article in articles:
            pub_types.extend(article.get("pub_type", []))
        
        # Count common types
        if "Clinical Trial" in str(pub_types):
            themes.append("Clinical research")
        if "Review" in str(pub_types):
            themes.append("Literature reviews")
        if "Meta-Analysis" in str(pub_types):
            themes.append("Meta-analyses")
        
        # Generic themes if nothing specific found
        if not themes:
            themes = ["Basic research", "Preclinical studies"]
        
        return themes[:5]
    
    def _extract_key_findings(self, articles: List[dict]) -> List[dict]:
        """Extract key findings from top articles"""
        findings = []
        
        for article in articles[:5]:
            findings.append({
                "title": article.get("title", ""),
                "authors": ", ".join(article.get("authors", [])[:2]),
                "journal": article.get("journal", ""),
                "year": article.get("pub_date", "")[:4] if article.get("pub_date") else "",
                "pmid": article.get("pmid", ""),
                "relevance": "High"  # Simplified - could use NLP for actual relevance
            })
        
        return findings
    
    def _generate_recommendation(
        self,
        momentum_score: float,
        trend_analysis: dict,
        total_pubs: int
    ) -> str:
        """Generate web intelligence recommendation"""
        trend = trend_analysis.get("publication_trend", "Unknown")
        
        if momentum_score >= 7:
            return f"Strong research momentum ({trend} trend, {total_pubs} publications). Active research area."
        elif momentum_score >= 4:
            return f"Moderate research activity ({trend} trend, {total_pubs} publications). Some scientific support."
        else:
            return f"Limited research activity ({trend} trend, {total_pubs} publications). Emerging or niche area."
