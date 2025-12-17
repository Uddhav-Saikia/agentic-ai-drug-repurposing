"""
Example usage of the Master Agent and worker agents
Run this to test the agentic system
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.master_agent import MasterAgent
import json
from datetime import datetime


async def example_query_1():
    """Example: Find drug repurposing opportunities for Alzheimer's disease"""
    print("=" * 80)
    print("Example 1: Drug Repurposing for Alzheimer's Disease")
    print("=" * 80)
    
    master = MasterAgent()
    
    query = "Find drug repurposing opportunities for Alzheimer's disease"
    
    print(f"\nQuery: {query}")
    print(f"Processing... (this may take 30-60 seconds)\n")
    
    result = await master.process_query(query)
    
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    print(f"\nStatus: {result['status']}")
    print(f"Execution Time: {result['execution_time']:.2f} seconds")
    
    if result['status'] == 'completed':
        report = result['final_report']
        print(f"\nTitle: {report['title']}")
        print(f"\nExecutive Summary:\n{report['executive_summary']}")
        
        print(f"\n\nKey Findings:")
        for i, finding in enumerate(report['key_findings'], 1):
            print(f"  {i}. {finding}")
        
        print(f"\n\nOverall Risk Assessment:")
        for risk_type, level in report['risk_assessment'].items():
            print(f"  {risk_type}: {level}")
        
        print(f"\n\nRecommendations:")
        for agent, recommendation in report['recommendations'].items():
            print(f"  [{agent}]: {recommendation}")
        
        # Save full report
        filename = f"report_alzheimers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n\nFull report saved to: {filename}")
    else:
        print(f"\nError: {result.get('error', 'Unknown error')}")


async def example_query_2():
    """Example: Analyze specific drug for COVID-19"""
    print("\n\n" + "=" * 80)
    print("Example 2: Metformin for COVID-19 Treatment")
    print("=" * 80)
    
    master = MasterAgent()
    
    query = "Analyze metformin as a potential treatment for COVID-19"
    
    print(f"\nQuery: {query}")
    print(f"Processing... (this may take 30-60 seconds)\n")
    
    result = await master.process_query(query)
    
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    
    print(f"\nStatus: {result['status']}")
    print(f"Execution Time: {result['execution_time']:.2f} seconds")
    
    if result['status'] == 'completed':
        report = result['final_report']
        
        print(f"\nKey Findings:")
        for finding in report['key_findings']:
            print(f"  • {finding}")
        
        print(f"\n\nAgent Results Summary:")
        print(f"  Total Agents: {report['metadata']['agents_executed']}")
        print(f"  Successful: {report['metadata']['successful_agents']}")
        print(f"  Overall Confidence: {report['overall_confidence']:.2%}")
        
        # Save report
        filename = f"report_metformin_covid_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n\nFull report saved to: {filename}")


async def example_agent_direct():
    """Example: Use a worker agent directly"""
    print("\n\n" + "=" * 80)
    print("Example 3: Direct Agent Usage (Clinical Intelligence)")
    print("=" * 80)
    
    from agents.clinical_agent import ClinicalIntelligenceAgent
    from agents.base_agent import AgentTask
    
    agent = ClinicalIntelligenceAgent()
    
    task = AgentTask(
        task_id="test_001",
        description="Analyze clinical trials for diabetes",
        parameters={
            "condition": "Type 2 Diabetes",
            "drug_name": "Metformin"
        }
    )
    
    print(f"\nTask: {task.description}")
    print(f"Parameters: {task.parameters}")
    print(f"\nExecuting agent...\n")
    
    result = await agent.execute(task)
    
    print(f"Status: {result.status}")
    print(f"Confidence: {result.confidence_score:.2%}")
    print(f"Execution Time: {result.execution_time:.2f}s")
    
    if result.status == "success":
        data = result.data
        print(f"\nResults:")
        print(f"  Total Trials: {data.get('total_trials', 0)}")
        print(f"  Evidence Score: {data.get('evidence_score', 0)}/10")
        print(f"  Recommendation: {data.get('recommendation', 'N/A')}")


async def example_parallel_agents():
    """Example: Execute multiple agents in parallel"""
    print("\n\n" + "=" * 80)
    print("Example 4: Parallel Agent Execution")
    print("=" * 80)
    
    from agents.clinical_agent import ClinicalIntelligenceAgent
    from agents.patent_agent import PatentLandscapeAgent
    from agents.market_agent import MarketIntelligenceAgent
    from agents.base_agent import AgentTask
    
    # Create tasks
    clinical_task = AgentTask(
        task_id="clinical_001",
        description="Clinical analysis",
        parameters={"condition": "Parkinson's Disease", "drug_name": "Amantadine"}
    )
    
    patent_task = AgentTask(
        task_id="patent_001",
        description="Patent analysis",
        parameters={"drug_name": "Amantadine", "condition": "Parkinson's Disease"}
    )
    
    market_task = AgentTask(
        task_id="market_001",
        description="Market analysis",
        parameters={"condition": "Parkinson's Disease", "region": "Global"}
    )
    
    # Create agents
    clinical_agent = ClinicalIntelligenceAgent()
    patent_agent = PatentLandscapeAgent()
    market_agent = MarketIntelligenceAgent()
    
    print("\nExecuting 3 agents in parallel...")
    start_time = asyncio.get_event_loop().time()
    
    # Execute in parallel
    results = await asyncio.gather(
        clinical_agent.execute(clinical_task),
        patent_agent.execute(patent_task),
        market_agent.execute(market_task)
    )
    
    end_time = asyncio.get_event_loop().time()
    
    print(f"\nCompleted in {end_time - start_time:.2f} seconds\n")
    
    for result in results:
        print(f"{result.agent_name}:")
        print(f"  Status: {result.status}")
        print(f"  Confidence: {result.confidence_score:.2%}")
        print(f"  Execution Time: {result.execution_time:.2f}s\n")


async def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("DRUG REPURPOSING AGENTIC AI - EXAMPLES")
    print("=" * 80)
    
    # Run examples
    try:
        # Example 1: Full pipeline with Master Agent
        await example_query_1()
        
        # Example 2: Another full query
        await example_query_2()
        
        # Example 3: Direct agent usage
        await example_agent_direct()
        
        # Example 4: Parallel execution
        await example_parallel_agents()
        
        print("\n" + "=" * 80)
        print("ALL EXAMPLES COMPLETED")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nError running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check if Gemini API key is set
    if not os.getenv("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY environment variable not set!")
        print("Please set it in your .env file or environment.")
        sys.exit(1)
    
    # Run examples
    asyncio.run(main())
