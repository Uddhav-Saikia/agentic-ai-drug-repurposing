"""
Master Agent - Orchestrates the entire drug repurposing analysis workflow
"""
import asyncio
import time
from typing import Dict, Any, List
from datetime import datetime
import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from agents.base_agent import AgentTask, AgentResult
from agents.clinical_agent import ClinicalIntelligenceAgent
from agents.patent_agent import PatentLandscapeAgent
from agents.market_agent import MarketIntelligenceAgent
from agents.web_agent import WebIntelligenceAgent
from core.config import settings

logger = logging.getLogger(__name__)


class QueryDecomposition(BaseModel):
    """Structured output for query decomposition"""
    condition: str = Field(description="Medical condition or disease")
    drug_name: str = Field(description="Drug or compound name (if specified)")
    analysis_type: str = Field(description="Type of analysis: repurposing, assessment, landscape")
    required_agents: List[str] = Field(description="List of agents needed: clinical, patent, market, web")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters")


class MasterAgent:
    """
    Master Agent orchestrates the entire drug repurposing pipeline
    
    Responsibilities:
    1. Decompose user queries into sub-tasks
    2. Assign tasks to specialized worker agents
    3. Execute agents in parallel
    4. Aggregate results into cohesive report
    5. Provide synthesis and recommendations
    """
    
    def __init__(self):
        """Initialize Master Agent with LLM and worker agents"""
        self.llm = None
        if settings.GEMINI_API_KEY:
            try:
                self.llm = ChatGoogleGenerativeAI(
                    model=settings.GEMINI_MODEL,
                    temperature=0.2,  # Low temperature for consistent decomposition
                    google_api_key=settings.GEMINI_API_KEY
                )
            except Exception:
                self.llm = None  # Allow creation without LLM for testing
        
        # Initialize worker agents
        self.clinical_agent = ClinicalIntelligenceAgent(llm=self.llm)
        self.patent_agent = PatentLandscapeAgent(llm=self.llm)
        self.market_agent = MarketIntelligenceAgent(llm=self.llm)
        self.web_agent = WebIntelligenceAgent(llm=self.llm)
        
        self.logger = logging.getLogger(__name__ + ".MasterAgent")
        
    async def process_query(self, query: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Main entry point for processing user queries
        
        Args:
            query: Natural language query from researcher
            user_id: User identifier
            
        Returns:
            Complete analysis report
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Processing query: {query}")
            
            # Step 1: Decompose query
            decomposition = await self._decompose_query(query)
            self.logger.info(f"Query decomposed: {decomposition.dict()}")
            
            # Step 2: Create tasks for worker agents
            tasks = self._create_agent_tasks(decomposition)
            self.logger.info(f"Created {len(tasks)} agent tasks")
            
            # Step 3: Execute agents in parallel
            agent_results = await self._execute_agents_parallel(tasks)
            self.logger.info(f"Completed {len(agent_results)} agent executions")
            
            # Step 4: Aggregate results
            aggregated_data = self._aggregate_results(agent_results)
            
            # Step 5: Synthesize final report
            final_report = await self._synthesize_report(
                query=query,
                decomposition=decomposition,
                agent_results=agent_results,
                aggregated_data=aggregated_data
            )
            
            execution_time = time.time() - start_time
            
            return {
                "query": query,
                "user_id": user_id,
                "status": "completed",
                "decomposition": decomposition.dict(),
                "agent_results": [r.dict() for r in agent_results],
                "aggregated_data": aggregated_data,
                "final_report": final_report,
                "execution_time": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Query processing failed: {e}", exc_info=True)
            return {
                "query": query,
                "user_id": user_id,
                "status": "failed",
                "error": str(e),
                "execution_time": time.time() - start_time,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _decompose_query(self, query: str) -> QueryDecomposition:
        """
        Decompose natural language query into structured tasks
        
        Args:
            query: User's natural language query
            
        Returns:
            QueryDecomposition with structured parameters
        """
        # Create parser
        parser = PydanticOutputParser(pydantic_object=QueryDecomposition)
        
        # Create prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in drug repurposing research. 
            Analyze the user's query and extract:
            1. Medical condition/disease
            2. Drug name (if mentioned)
            3. Type of analysis needed
            4. Which agents should be involved (clinical, patent, market, web)
            
            {format_instructions}
            """),
            ("user", "{query}")
        ])
        
        # Execute
        chain = prompt | self.llm | parser
        
        try:
            result = await asyncio.to_thread(
                chain.invoke,
                {
                    "query": query,
                    "format_instructions": parser.get_format_instructions()
                }
            )
            return result
        except Exception as e:
            self.logger.warning(f"LLM decomposition failed, using fallback: {e}")
            # Fallback to simple parsing
            return self._fallback_decomposition(query)
    
    def _fallback_decomposition(self, query: str) -> QueryDecomposition:
        """Fallback query decomposition using simple heuristics"""
        query_lower = query.lower()
        
        # Try to extract condition and drug
        words = query.split()
        condition = ""
        drug_name = ""
        
        # Simple keyword extraction
        disease_keywords = ["disease", "cancer", "diabetes", "alzheimer", "parkinson"]
        for keyword in disease_keywords:
            if keyword in query_lower:
                condition = keyword.capitalize()
                break
        
        # If no condition found, use first capitalized word
        if not condition:
            for word in words:
                if word[0].isupper() and len(word) > 3:
                    condition = word
                    break
        
        return QueryDecomposition(
            condition=condition or "Unknown condition",
            drug_name=drug_name,
            analysis_type="repurposing",
            required_agents=["clinical", "patent", "market", "web"],
            parameters={"region": "Global"}
        )
    
    def _create_agent_tasks(self, decomposition: QueryDecomposition) -> Dict[str, AgentTask]:
        """
        Create tasks for each required agent
        
        Args:
            decomposition: Structured query decomposition
            
        Returns:
            Dictionary mapping agent names to tasks
        """
        tasks = {}
        base_params = {
            "condition": decomposition.condition,
            "drug_name": decomposition.drug_name,
            **decomposition.parameters
        }
        
        # Create task for each required agent
        if "clinical" in decomposition.required_agents:
            tasks["clinical"] = AgentTask(
                task_id=f"clinical_{int(time.time())}",
                description=f"Analyze clinical trials for {decomposition.condition}",
                parameters=base_params
            )
        
        if "patent" in decomposition.required_agents:
            tasks["patent"] = AgentTask(
                task_id=f"patent_{int(time.time())}",
                description=f"Analyze patent landscape for {decomposition.drug_name or decomposition.condition}",
                parameters=base_params
            )
        
        if "market" in decomposition.required_agents:
            tasks["market"] = AgentTask(
                task_id=f"market_{int(time.time())}",
                description=f"Analyze market opportunity for {decomposition.condition}",
                parameters=base_params
            )
        
        if "web" in decomposition.required_agents:
            tasks["web"] = AgentTask(
                task_id=f"web_{int(time.time())}",
                description=f"Gather web intelligence for {decomposition.drug_name} and {decomposition.condition}",
                parameters=base_params
            )
        
        return tasks
    
    async def _execute_agents_parallel(
        self, 
        tasks: Dict[str, AgentTask]
    ) -> List[AgentResult]:
        """
        Execute multiple agents in parallel
        
        Args:
            tasks: Dictionary of agent tasks
            
        Returns:
            List of agent results
        """
        # Create coroutines for each agent
        coroutines = []
        agent_names = []
        
        for agent_name, task in tasks.items():
            if agent_name == "clinical":
                coroutines.append(self.clinical_agent.execute(task))
            elif agent_name == "patent":
                coroutines.append(self.patent_agent.execute(task))
            elif agent_name == "market":
                coroutines.append(self.market_agent.execute(task))
            elif agent_name == "web":
                coroutines.append(self.web_agent.execute(task))
            agent_names.append(agent_name)
        
        # Execute in parallel with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*coroutines, return_exceptions=True),
                timeout=settings.AGENT_TIMEOUT_SECONDS
            )
            
            # Handle any exceptions
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Agent {agent_names[i]} failed: {result}")
                    # Create failed result
                    processed_results.append(AgentResult(
                        agent_name=agent_names[i],
                        task_id=tasks[agent_names[i]].task_id,
                        status="failed",
                        data={},
                        error=str(result)
                    ))
                else:
                    processed_results.append(result)
            
            return processed_results
            
        except asyncio.TimeoutError:
            self.logger.error("Agent execution timeout")
            return []
    
    def _aggregate_results(self, results: List[AgentResult]) -> Dict[str, Any]:
        """
        Aggregate results from all agents
        
        Args:
            results: List of agent results
            
        Returns:
            Aggregated data summary
        """
        aggregated = {
            "total_agents": len(results),
            "successful_agents": len([r for r in results if r.status == "success"]),
            "failed_agents": len([r for r in results if r.status == "failed"]),
            "average_confidence": 0.0,
            "total_execution_time": sum([r.execution_time for r in results]),
            "all_sources": []
        }
        
        # Calculate average confidence
        successful = [r for r in results if r.status == "success"]
        if successful:
            aggregated["average_confidence"] = sum([r.confidence_score for r in successful]) / len(successful)
        
        # Collect all sources
        for result in results:
            aggregated["all_sources"].extend(result.sources)
        aggregated["all_sources"] = list(set(aggregated["all_sources"]))
        
        # Extract key metrics from each agent
        for result in results:
            if result.status == "success":
                aggregated[f"{result.agent_name}_data"] = result.data
        
        return aggregated
    
    async def _synthesize_report(
        self,
        query: str,
        decomposition: QueryDecomposition,
        agent_results: List[AgentResult],
        aggregated_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Synthesize final report from all agent results
        
        Args:
            query: Original user query
            decomposition: Query decomposition
            agent_results: Results from all agents
            aggregated_data: Aggregated data summary
            
        Returns:
            Final synthesized report
        """
        # Extract recommendations from each agent
        recommendations = {}
        for result in agent_results:
            if result.status == "success":
                recommendations[result.agent_name] = result.data.get("recommendation", "")
        
        # Generate executive summary using LLM
        executive_summary = await self._generate_executive_summary(
            query,
            decomposition,
            recommendations
        )
        
        # Compile final report
        report = {
            "title": f"Drug Repurposing Analysis: {decomposition.condition}",
            "executive_summary": executive_summary,
            "query": query,
            "condition": decomposition.condition,
            "drug_name": decomposition.drug_name,
            "analysis_date": datetime.utcnow().isoformat(),
            "overall_confidence": aggregated_data.get("average_confidence", 0.0),
            "sections": {
                "clinical_intelligence": self._format_clinical_section(agent_results),
                "patent_landscape": self._format_patent_section(agent_results),
                "market_intelligence": self._format_market_section(agent_results),
                "web_intelligence": self._format_web_section(agent_results)
            },
            "key_findings": self._extract_key_findings(agent_results),
            "recommendations": recommendations,
            "risk_assessment": self._assess_overall_risk(agent_results),
            "next_steps": self._suggest_next_steps(agent_results),
            "data_sources": aggregated_data.get("all_sources", []),
            "metadata": {
                "agents_executed": aggregated_data.get("total_agents", 0),
                "successful_agents": aggregated_data.get("successful_agents", 0),
                "total_execution_time": aggregated_data.get("total_execution_time", 0)
            }
        }
        
        return report
    
    async def _generate_executive_summary(
        self,
        query: str,
        decomposition: QueryDecomposition,
        recommendations: Dict[str, str]
    ) -> str:
        """Generate executive summary using LLM"""
        prompt = f"""
        Generate a concise executive summary for a drug repurposing analysis.
        
        Query: {query}
        Condition: {decomposition.condition}
        Drug: {decomposition.drug_name or "Not specified"}
        
        Agent Recommendations:
        {chr(10).join([f"- {k}: {v}" for k, v in recommendations.items()])}
        
        Provide a 3-4 sentence executive summary highlighting key opportunities and risks.
        """
        
        try:
            response = await asyncio.to_thread(self.llm.invoke, prompt)
            return response.content
        except Exception as e:
            self.logger.error(f"Executive summary generation failed: {e}")
            return "Analysis completed across clinical, patent, market, and web intelligence domains."
    
    def _format_clinical_section(self, results: List[AgentResult]) -> Dict[str, Any]:
        """Format clinical intelligence section"""
        clinical_result = next((r for r in results if r.agent_name == "ClinicalIntelligenceAgent"), None)
        if clinical_result and clinical_result.status == "success":
            return clinical_result.data
        return {"status": "not_available"}
    
    def _format_patent_section(self, results: List[AgentResult]) -> Dict[str, Any]:
        """Format patent landscape section"""
        patent_result = next((r for r in results if r.agent_name == "PatentLandscapeAgent"), None)
        if patent_result and patent_result.status == "success":
            return patent_result.data
        return {"status": "not_available"}
    
    def _format_market_section(self, results: List[AgentResult]) -> Dict[str, Any]:
        """Format market intelligence section"""
        market_result = next((r for r in results if r.agent_name == "MarketIntelligenceAgent"), None)
        if market_result and market_result.status == "success":
            return market_result.data
        return {"status": "not_available"}
    
    def _format_web_section(self, results: List[AgentResult]) -> Dict[str, Any]:
        """Format web intelligence section"""
        web_result = next((r for r in results if r.agent_name == "WebIntelligenceAgent"), None)
        if web_result and web_result.status == "success":
            return web_result.data
        return {"status": "not_available"}
    
    def _extract_key_findings(self, results: List[AgentResult]) -> List[str]:
        """Extract key findings across all agents"""
        findings = []
        
        for result in results:
            if result.status == "success":
                data = result.data
                
                if result.agent_name == "ClinicalIntelligenceAgent":
                    findings.append(f"Clinical: {data.get('total_trials', 0)} trials found with evidence score {data.get('evidence_score', 0)}/10")
                
                elif result.agent_name == "PatentLandscapeAgent":
                    findings.append(f"Patents: {data.get('active_patents', 0)} active patents identified")
                
                elif result.agent_name == "MarketIntelligenceAgent":
                    market_size = data.get('market_size', {})
                    size_b = market_size.get('market_size_usd', 0) / 1e9
                    findings.append(f"Market: ${size_b:.1f}B opportunity with {market_size.get('projected_cagr', 0)}% CAGR")
                
                elif result.agent_name == "WebIntelligenceAgent":
                    findings.append(f"Literature: {data.get('total_publications', 0)} publications with momentum score {data.get('research_momentum_score', 0)}/10")
        
        return findings
    
    def _assess_overall_risk(self, results: List[AgentResult]) -> Dict[str, str]:
        """Assess overall risk profile"""
        risks = {
            "clinical_risk": "Unknown",
            "ip_risk": "Unknown",
            "market_risk": "Unknown",
            "overall_risk": "Moderate"
        }
        
        # Assess each dimension
        for result in results:
            if result.status == "success":
                data = result.data
                
                if result.agent_name == "ClinicalIntelligenceAgent":
                    evidence_score = data.get('evidence_score', 0)
                    risks["clinical_risk"] = "Low" if evidence_score >= 6 else "Moderate" if evidence_score >= 3 else "High"
                
                elif result.agent_name == "PatentLandscapeAgent":
                    risk_score = data.get('risk_score', 5)
                    risks["ip_risk"] = "Low" if risk_score <= 3 else "Moderate" if risk_score <= 6 else "High"
                
                elif result.agent_name == "MarketIntelligenceAgent":
                    attractiveness = data.get('attractiveness_score', 5)
                    risks["market_risk"] = "Low" if attractiveness >= 6 else "Moderate" if attractiveness >= 3 else "High"
        
        # Calculate overall
        risk_values = {"Low": 1, "Moderate": 2, "High": 3, "Unknown": 2}
        avg_risk = sum([risk_values.get(v, 2) for k, v in risks.items() if k != "overall_risk"]) / 3
        
        if avg_risk < 1.7:
            risks["overall_risk"] = "Low"
        elif avg_risk < 2.3:
            risks["overall_risk"] = "Moderate"
        else:
            risks["overall_risk"] = "High"
        
        return risks
    
    def _suggest_next_steps(self, results: List[AgentResult]) -> List[str]:
        """Suggest next steps based on analysis"""
        steps = [
            "Conduct detailed review of clinical trial results",
            "Engage patent attorney for freedom-to-operate analysis",
            "Develop detailed market entry strategy",
            "Initiate discussions with key opinion leaders",
            "Evaluate regulatory pathway and requirements"
        ]
        return steps[:3]  # Return top 3 steps
