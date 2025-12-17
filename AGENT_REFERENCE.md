# Phase 2 Quick Reference

## 🚀 Quick Start

### 1. Verify Installation
```bash
cd backend
python test_phase2.py
```

### 2. Run Examples
```bash
cd backend
python example_usage.py
```

## 📚 Agent Reference

### Master Agent
```python
from agents.master_agent import MasterAgent

master = MasterAgent()
result = await master.process_query("Your natural language query here")

# Access results
print(result['final_report']['executive_summary'])
print(result['final_report']['key_findings'])
print(result['final_report']['risk_assessment'])
```

### Clinical Intelligence Agent
```python
from agents.clinical_agent import ClinicalIntelligenceAgent
from agents.base_agent import AgentTask

agent = ClinicalIntelligenceAgent()
task = AgentTask(
    task_id="clinical_001",
    description="Analyze clinical trials",
    parameters={
        "condition": "Alzheimer's Disease",
        "drug_name": "Donepezil"  # Optional
    }
)

result = await agent.execute(task)

# Access data
print(f"Total Trials: {result.data['total_trials']}")
print(f"Evidence Score: {result.data['evidence_score']}/10")
print(f"Recommendation: {result.data['recommendation']}")
```

### Patent Landscape Agent
```python
from agents.patent_agent import PatentLandscapeAgent

agent = PatentLandscapeAgent()
task = AgentTask(
    task_id="patent_001",
    description="Analyze patents",
    parameters={
        "drug_name": "Metformin",
        "condition": "Type 2 Diabetes"  # Optional
    }
)

result = await agent.execute(task)

# Access data
print(f"Active Patents: {result.data['active_patents']}")
print(f"IP Risk Score: {result.data['risk_score']}/10")
print(f"FTO Assessment: {result.data['ip_assessment']}")
```

### Market Intelligence Agent
```python
from agents.market_agent import MarketIntelligenceAgent

agent = MarketIntelligenceAgent()
task = AgentTask(
    task_id="market_001",
    description="Analyze market",
    parameters={
        "condition": "Parkinson's Disease",
        "region": "Global",  # Optional: US, EU, etc.
        "drug_name": "Levodopa"  # Optional
    }
)

result = await agent.execute(task)

# Access data
market_size = result.data['market_size']
print(f"Market Size: ${market_size['market_size_usd']/1e9:.1f}B")
print(f"CAGR: {market_size['projected_cagr']}%")
print(f"Attractiveness: {result.data['attractiveness_score']}/10")
```

### Web Intelligence Agent
```python
from agents.web_agent import WebIntelligenceAgent

agent = WebIntelligenceAgent()
task = AgentTask(
    task_id="web_001",
    description="Gather web intelligence",
    parameters={
        "condition": "COVID-19",
        "drug_name": "Hydroxychloroquine"
    }
)

result = await agent.execute(task)

# Access data
print(f"Publications: {result.data['total_publications']}")
print(f"Momentum Score: {result.data['research_momentum_score']}/10")
print(f"Trend: {result.data['trend_analysis']['publication_trend']}")
```

## 🔧 Tool Usage (Direct API Calls)

### Clinical Trials Search
```python
from agents.tools.clinical_tools import ClinicalTrialsAPI

# Search trials
results = ClinicalTrialsAPI.search_studies(
    condition="Alzheimer's Disease",
    drug_name="Donepezil",
    status=["COMPLETED", "RECRUITING"],
    max_results=20
)

print(f"Found {results['total_count']} trials")
for study in results['studies']:
    print(f"- {study['title']} ({study['nct_id']})")
```

### Patent Search
```python
from agents.tools.patent_tools import USPTOPatentAPI

# Search patents
patents = USPTOPatentAPI.search_patents(
    drug_name="Metformin",
    condition="Diabetes",
    max_results=20
)

# Analyze landscape
landscape = USPTOPatentAPI.analyze_patent_landscape("Metformin")
print(f"Active Patents: {landscape['active_patents']}")
print(f"Risk Level: {landscape['freedom_to_operate']['risk_level']}")
```

### Market Data
```python
from agents.tools.market_tools import MarketIntelligenceAPI

# Get market size
market = MarketIntelligenceAPI.get_market_size(
    condition="Type 2 Diabetes",
    region="Global"
)

print(f"Market Size: ${market['market_size_usd']/1e9:.1f}B")
print(f"Growth Rate: {market['projected_cagr']}%")

# Analyze competition
competition = MarketIntelligenceAPI.analyze_competitive_landscape(
    condition="Type 2 Diabetes"
)

print(f"Approved Drugs: {len(competition['approved_drugs'])}")
print(f"Pipeline Drugs: {len(competition['pipeline_drugs'])}")
```

### PubMed Search
```python
from agents.tools.web_tools import PubMedAPI

# Search literature
literature = PubMedAPI.search_literature(
    drug_name="Metformin",
    condition="Alzheimer's Disease",
    max_results=50
)

print(f"Found {literature['total_count']} publications")

# Analyze trends
trends = PubMedAPI.analyze_literature_trends(
    drug_name="Metformin",
    condition="Alzheimer's Disease"
)

print(f"Publication Trend: {trends['publication_trend']}")
print(f"Total Publications: {trends['total_publications']}")
```

## ⚡ Parallel Execution

```python
import asyncio
from agents.clinical_agent import ClinicalIntelligenceAgent
from agents.patent_agent import PatentLandscapeAgent
from agents.market_agent import MarketIntelligenceAgent

# Create agents
clinical = ClinicalIntelligenceAgent()
patent = PatentLandscapeAgent()
market = MarketIntelligenceAgent()

# Create tasks
tasks = [
    clinical.execute(clinical_task),
    patent.execute(patent_task),
    market.execute(market_task)
]

# Execute in parallel
results = await asyncio.gather(*tasks)

# Process results
for result in results:
    print(f"{result.agent_name}: {result.status}")
```

## 📊 Understanding Results

### AgentResult Structure
```python
result = await agent.execute(task)

# Common fields
result.agent_name       # "ClinicalIntelligenceAgent"
result.task_id          # "clinical_001"
result.status           # "success" | "failed" | "partial"
result.data             # Dict with agent-specific results
result.error            # Error message if failed
result.execution_time   # Time in seconds
result.confidence_score # 0.0 to 1.0
result.sources          # List of data sources used
result.completed_at     # Timestamp
```

### Master Agent Result Structure
```python
result = await master.process_query(query)

result['status']              # "completed" | "failed"
result['query']               # Original query
result['decomposition']       # Parsed query structure
result['agent_results']       # List of all agent results
result['aggregated_data']     # Summary statistics
result['final_report']        # Synthesized report
result['execution_time']      # Total time
result['timestamp']           # Completion time
```

### Final Report Structure
```python
report = result['final_report']

report['title']                     # Report title
report['executive_summary']         # LLM-generated summary
report['condition']                 # Medical condition
report['drug_name']                 # Drug name (if applicable)
report['overall_confidence']        # 0.0 to 1.0
report['sections']                  # Dict with agent sections
report['key_findings']              # List of key insights
report['recommendations']           # Agent recommendations
report['risk_assessment']           # Risk profile
report['next_steps']                # Suggested actions
report['data_sources']              # All sources used
report['metadata']                  # Execution metadata
```

## 🎯 Scoring Systems

| Agent | Score Name | Range | Meaning |
|-------|-----------|-------|---------|
| Clinical | Evidence Score | 0-10 | Strength of clinical evidence |
| Patent | Risk Score | 0-10 | IP infringement risk (higher = more risk) |
| Market | Attractiveness Score | 0-10 | Commercial opportunity |
| Web | Momentum Score | 0-10 | Research activity level |

**Interpretation**:
- **0-3**: Low
- **4-6**: Moderate  
- **7-10**: High

## ⚙️ Configuration

Edit `.env` file:
```bash
# Required
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview

# Agent Settings
MAX_CONCURRENT_AGENTS=4
AGENT_TIMEOUT_SECONDS=300
ENABLE_AGENT_MEMORY=True

# Vector DB
VECTOR_DIMENSION=1536
SIMILARITY_THRESHOLD=0.7
```

## 🐛 Common Issues

### Issue: "OPENAI_API_KEY not found"
**Solution**: Set in `.env` file
```bash
OPENAI_API_KEY=sk-your-actual-key
```

### Issue: "Module not found"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "API timeout"
**Solution**: Increase timeout in `.env`
```bash
AGENT_TIMEOUT_SECONDS=600
```

### Issue: "ClinicalTrials.gov API error"
**Solution**: Check internet connection, API may be rate-limited

## 📈 Performance Tips

1. **Use parallel execution** for multiple agents
2. **Set reasonable timeouts** (default: 300s)
3. **Cache results** with Redis (Phase 5)
4. **Limit max_results** in API calls (20-50 optimal)
5. **Monitor token usage** for LLM calls

## 🔗 API Endpoints (Phase 3)

Coming in Phase 3:
```python
# FastAPI endpoints
POST   /api/v1/queries          # Submit new query
GET    /api/v1/queries/{id}     # Get query status
GET    /api/v1/reports/{id}     # Get report
GET    /api/v1/agents/status    # Agent health
```

## 📚 Additional Resources

- **LangChain**: https://python.langchain.com/
- **ClinicalTrials.gov API**: https://clinicaltrials.gov/api/gui
- **PubMed API**: https://www.ncbi.nlm.nih.gov/books/NBK25501/
- **USPTO**: https://www.uspto.gov/patents/search

## 🆘 Need Help?

1. Run verification: `python test_phase2.py`
2. Check logs in `backend/logs/app.log`
3. Review example: `python example_usage.py`
4. Check configuration in `.env` file
