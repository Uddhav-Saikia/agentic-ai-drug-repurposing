"""
Celery tasks for asynchronous agent execution
"""
import asyncio
from datetime import datetime
from typing import Dict, Any

from core.celery_app import celery_app
from core.database import SessionLocal
from models.database_models import Query, Task, Report, DrugCandidate
from agents.master_agent import MasterAgent
from services.report_service import ReportService


@celery_app.task(name="run_analysis_task")
def run_analysis_task(query_id: int):
    """
    Execute drug repurposing analysis for a query
    
    This is the main background task that:
    1. Updates query status to "processing"
    2. Creates task records for each agent
    3. Executes Master Agent analysis
    4. Stores results in database
    5. Updates query status to "completed" or "failed"
    """
    db = SessionLocal()
    
    try:
        # Get query
        query = db.query(Query).filter(Query.id == query_id).first()
        if not query:
            raise ValueError(f"Query {query_id} not found")
        
        # Update status to processing
        query.status = "processing"
        query.updated_at = datetime.utcnow()
        db.commit()
        
        # Create task records for each agent type
        agent_types = ["clinical", "patent", "market", "web"]
        task_records = []
        
        for agent_type in agent_types:
            task = Task(
                query_id=query_id,
                agent_type=agent_type,
                task_description=f"Analyze {query.query_text} using {agent_type} intelligence",
                status="pending"
            )
            db.add(task)
            task_records.append(task)
        
        db.commit()
        
        # Execute Master Agent analysis
        master_agent = MasterAgent()
        
        # Run async analysis in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            master_agent.process_query(query.query_text)
        )
        loop.close()
        
        # Update task statuses based on result
        for task_record in task_records:
            agent_result = next(
                (r for r in result.get("agent_results", []) if r.get("agent_type") == task_record.agent_type),
                None
            )
            
            if agent_result:
                task_record.status = "completed" if agent_result.get("success") else "failed"
                task_record.result = agent_result.get("data", {})
                task_record.error = agent_result.get("error")
                task_record.started_at = datetime.utcnow()  # Approximation
                task_record.completed_at = datetime.utcnow()
            else:
                task_record.status = "failed"
                task_record.error = "No result from agent"
        
        db.commit()
        
        # Create report
        report_service = ReportService(db)
        report_data = _extract_report_data(result)
        
        report = report_service.create_report(
            query_id=query_id,
            title=report_data["title"],
            content=report_data["content"],
            summary=report_data["summary"],
            metadata=report_data["metadata"]
        )
        
        # Create drug candidates
        for candidate_data in report_data.get("drug_candidates", []):
            report_service.create_drug_candidate(
                report_id=report.id,
                drug_name=candidate_data["drug_name"],
                indication=candidate_data["indication"],
                confidence_score=candidate_data["confidence_score"],
                market_data=candidate_data.get("market_data"),
                patent_data=candidate_data.get("patent_data"),
                clinical_data=candidate_data.get("clinical_data"),
                web_intelligence=candidate_data.get("web_intelligence")
            )
        
        # Update query status to completed
        query.status = "completed"
        query.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "query_id": query_id,
            "status": "completed",
            "report_id": report.id,
            "drug_candidates_count": len(report_data.get("drug_candidates", []))
        }
    
    except Exception as e:
        # Update query status to failed
        query = db.query(Query).filter(Query.id == query_id).first()
        if query:
            query.status = "failed"
            query.updated_at = datetime.utcnow()
            db.commit()
        
        # Mark all pending tasks as failed
        tasks = db.query(Task).filter(
            Task.query_id == query_id,
            Task.status.in_(["pending", "running"])
        ).all()
        
        for task in tasks:
            task.status = "failed"
            task.error = str(e)
            task.completed_at = datetime.utcnow()
        
        db.commit()
        
        raise
    
    finally:
        db.close()


def _extract_report_data(master_result: Dict[str, Any]) -> Dict[str, Any]:
    """Extract structured report data from Master Agent result"""
    
    # Extract metadata
    metadata = {
        "executive_summary": master_result.get("executive_summary", ""),
        "condition": master_result.get("condition", ""),
        "drug_name": master_result.get("drug_name", ""),
        "overall_confidence": master_result.get("overall_confidence", 0.0),
        "sections": {},
        "key_findings": master_result.get("key_findings", []),
        "recommendations": master_result.get("recommendations", {}),
        "risk_assessment": master_result.get("risk_assessment", {}),
        "next_steps": master_result.get("next_steps", []),
        "data_sources": []
    }
    
    # Extract sections from agent results
    agent_results = master_result.get("agent_results", [])
    for agent_result in agent_results:
        agent_type = agent_result.get("agent_type", "unknown")
        agent_data = agent_result.get("data", {})
        
        metadata["sections"][agent_type] = agent_data
        
        # Extract data sources
        if "sources" in agent_data:
            metadata["data_sources"].extend(agent_data["sources"])
    
    # Build content string
    content_parts = [
        f"# {master_result.get('condition', 'Analysis Report')}",
        "",
        "## Executive Summary",
        master_result.get("executive_summary", ""),
        ""
    ]
    
    for section_name, section_data in metadata["sections"].items():
        content_parts.append(f"## {section_name.title()} Intelligence")
        content_parts.append(str(section_data))
        content_parts.append("")
    
    content = "\n".join(content_parts)
    
    # Extract drug candidates
    drug_candidates = []
    drug_name = master_result.get("drug_name", "Unknown Drug")
    condition = master_result.get("condition", "Unknown Condition")
    
    # Create candidate from aggregated data
    candidate = {
        "drug_name": drug_name,
        "indication": condition,
        "confidence_score": master_result.get("overall_confidence", 0.0),
        "market_data": metadata["sections"].get("market", {}),
        "patent_data": metadata["sections"].get("patent", {}),
        "clinical_data": metadata["sections"].get("clinical", {}),
        "web_intelligence": metadata["sections"].get("web", {})
    }
    drug_candidates.append(candidate)
    
    return {
        "title": f"Drug Repurposing Analysis: {drug_name} for {condition}",
        "content": content,
        "summary": master_result.get("executive_summary", "")[:500],
        "metadata": metadata,
        "drug_candidates": drug_candidates
    }


@celery_app.task(name="cleanup_old_reports")
def cleanup_old_reports(days: int = 30):
    """
    Periodic task to clean up old reports
    
    Args:
        days: Delete reports older than this many days
    """
    from datetime import timedelta
    
    db = SessionLocal()
    
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Delete old queries (cascade will delete tasks, reports, candidates)
        old_queries = db.query(Query).filter(
            Query.created_at < cutoff_date,
            Query.status.in_(["completed", "failed"])
        ).all()
        
        count = len(old_queries)
        
        for query in old_queries:
            db.delete(query)
        
        db.commit()
        
        return {
            "deleted_queries": count,
            "cutoff_date": cutoff_date.isoformat()
        }
    
    finally:
        db.close()
