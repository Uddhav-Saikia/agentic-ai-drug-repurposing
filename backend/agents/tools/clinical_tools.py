"""
Tools for Clinical Intelligence Agent
"""
import requests
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import time

logger = logging.getLogger(__name__)


class ClinicalTrialsAPI:
    """
    Interface for ClinicalTrials.gov API
    Documentation: https://clinicaltrials.gov/api/gui
    """
    
    BASE_URL = "https://clinicaltrials.gov/api/v2"
    
    @staticmethod
    def search_studies(
        condition: str,
        drug_name: Optional[str] = None,
        status: Optional[List[str]] = None,
        max_results: int = 20
    ) -> Dict[str, Any]:
        """
        Search clinical trials by condition and drug
        
        Args:
            condition: Disease/condition to search
            drug_name: Drug/intervention name
            status: List of study statuses (e.g., ['COMPLETED', 'RECRUITING'])
            max_results: Maximum number of results
            
        Returns:
            Dictionary with search results
        """
        try:
            # Build query parameters
            query_parts = [condition]
            if drug_name:
                query_parts.append(drug_name)
            
            params = {
                "query.cond": condition,
                "pageSize": min(max_results, 100),
                "format": "json"
            }
            
            if drug_name:
                params["query.intr"] = drug_name
            
            if status:
                params["filter.overallStatus"] = ",".join(status)
            
            logger.info(f"Searching ClinicalTrials.gov for: {condition}")
            
            response = requests.get(
                f"{ClinicalTrialsAPI.BASE_URL}/studies",
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            studies = data.get("studies", [])
            
            # Extract relevant information
            results = {
                "total_count": len(studies),
                "studies": [],
                "sources": ["ClinicalTrials.gov"],
                "query_timestamp": datetime.utcnow().isoformat()
            }
            
            for study in studies:
                protocol = study.get("protocolSection", {})
                identification = protocol.get("identificationModule", {})
                status_module = protocol.get("statusModule", {})
                design = protocol.get("designModule", {})
                
                results["studies"].append({
                    "nct_id": identification.get("nctId"),
                    "title": identification.get("briefTitle"),
                    "status": status_module.get("overallStatus"),
                    "phase": design.get("phases", []),
                    "start_date": status_module.get("startDateStruct", {}).get("date"),
                    "completion_date": status_module.get("completionDateStruct", {}).get("date"),
                    "enrollment": status_module.get("enrollmentInfo", {}).get("count"),
                    "conditions": protocol.get("conditionsModule", {}).get("conditions", []),
                    "interventions": [
                        i.get("name") 
                        for i in protocol.get("armsInterventionsModule", {}).get("interventions", [])
                    ]
                })
            
            logger.info(f"Found {len(studies)} clinical trials")
            return results
            
        except requests.RequestException as e:
            logger.error(f"ClinicalTrials.gov API error: {e}")
            return {
                "total_count": 0,
                "studies": [],
                "error": str(e),
                "sources": ["ClinicalTrials.gov"],
                "query_timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def get_study_details(nct_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific study
        
        Args:
            nct_id: NCT identifier (e.g., NCT12345678)
            
        Returns:
            Dictionary with detailed study information
        """
        try:
            logger.info(f"Fetching details for study: {nct_id}")
            
            response = requests.get(
                f"{ClinicalTrialsAPI.BASE_URL}/studies/{nct_id}",
                params={"format": "json"},
                timeout=30
            )
            response.raise_for_status()
            
            data = response.json()
            return {
                "nct_id": nct_id,
                "data": data,
                "source": "ClinicalTrials.gov",
                "retrieved_at": datetime.utcnow().isoformat()
            }
            
        except requests.RequestException as e:
            logger.error(f"Error fetching study {nct_id}: {e}")
            return {
                "nct_id": nct_id,
                "error": str(e),
                "source": "ClinicalTrials.gov"
            }
    
    @staticmethod
    def analyze_study_outcomes(condition: str, drug_name: str) -> Dict[str, Any]:
        """
        Analyze clinical trial outcomes for a drug-condition pair
        
        Args:
            condition: Medical condition
            drug_name: Drug name
            
        Returns:
            Analysis of trial outcomes
        """
        try:
            # Search for completed studies
            studies_data = ClinicalTrialsAPI.search_studies(
                condition=condition,
                drug_name=drug_name,
                status=["COMPLETED"],
                max_results=50
            )
            
            studies = studies_data.get("studies", [])
            
            # Analyze phases
            phase_distribution = {}
            total_enrollment = 0
            
            for study in studies:
                phases = study.get("phase", [])
                enrollment = study.get("enrollment", 0)
                
                for phase in phases:
                    phase_distribution[phase] = phase_distribution.get(phase, 0) + 1
                
                if enrollment:
                    total_enrollment += enrollment
            
            return {
                "condition": condition,
                "drug": drug_name,
                "total_studies": len(studies),
                "phase_distribution": phase_distribution,
                "total_enrollment": total_enrollment,
                "completed_studies": len([s for s in studies if s.get("status") == "COMPLETED"]),
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing outcomes: {e}")
            return {
                "condition": condition,
                "drug": drug_name,
                "error": str(e)
            }


def search_clinical_trials_tool(condition: str, drug_name: str = "") -> str:
    """
    LangChain tool wrapper for searching clinical trials
    
    Args:
        condition: Medical condition to search
        drug_name: Optional drug name
        
    Returns:
        Formatted string with search results
    """
    results = ClinicalTrialsAPI.search_studies(
        condition=condition,
        drug_name=drug_name if drug_name else None,
        max_results=10
    )
    
    if results.get("error"):
        return f"Error searching clinical trials: {results['error']}"
    
    studies = results.get("studies", [])
    if not studies:
        return f"No clinical trials found for {condition}" + (f" with {drug_name}" if drug_name else "")
    
    output = f"Found {len(studies)} clinical trials:\n\n"
    for i, study in enumerate(studies[:5], 1):
        output += f"{i}. {study.get('title')} (NCT: {study.get('nct_id')})\n"
        output += f"   Status: {study.get('status')}, Phase: {study.get('phase')}\n"
        output += f"   Interventions: {', '.join(study.get('interventions', [])[:3])}\n\n"
    
    return output
