"""
Tools for Patent Landscape Agent
"""
import requests
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import re

logger = logging.getLogger(__name__)


class USPTOPatentAPI:
    """
    Interface for USPTO Patent Search
    Note: This is a simplified implementation. Real USPTO API requires authentication.
    """
    
    BASE_URL = "https://developer.uspto.gov"
    
    @staticmethod
    def search_patents(
        drug_name: str,
        condition: Optional[str] = None,
        max_results: int = 20
    ) -> Dict[str, Any]:
        """
        Search for patents related to drug and condition
        
        Args:
            drug_name: Drug/compound name
            condition: Medical condition (optional)
            max_results: Maximum results to return
            
        Returns:
            Dictionary with patent search results
        """
        try:
            # Build search query
            query = drug_name
            if condition:
                query += f" AND {condition}"
            
            logger.info(f"Searching patents for: {query}")
            
            # Mock data for demonstration (replace with real API in production)
            results = {
                "total_count": 15,
                "patents": [
                    {
                        "patent_number": "US10123456",
                        "title": f"Method of treating {condition or 'disease'} with {drug_name}",
                        "filing_date": "2020-01-15",
                        "grant_date": "2022-03-20",
                        "status": "Active",
                        "assignee": "Pharma Corp",
                        "claims_count": 25,
                        "citations": 12,
                        "abstract": f"A pharmaceutical composition comprising {drug_name} for treatment of {condition or 'various conditions'}..."
                    },
                    {
                        "patent_number": "US10234567",
                        "title": f"Formulation of {drug_name} for therapeutic use",
                        "filing_date": "2019-05-10",
                        "grant_date": "2021-08-15",
                        "status": "Active",
                        "assignee": "Medical Innovations Inc",
                        "claims_count": 18,
                        "citations": 8,
                        "abstract": f"Novel formulations and dosing regimens for {drug_name}..."
                    }
                ],
                "sources": ["USPTO Patent Database"],
                "query_timestamp": datetime.utcnow().isoformat(),
                "note": "This is mock data. Real USPTO API integration requires authentication."
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Patent search error: {e}")
            return {
                "total_count": 0,
                "patents": [],
                "error": str(e),
                "sources": ["USPTO"],
                "query_timestamp": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def analyze_patent_landscape(drug_name: str) -> Dict[str, Any]:
        """
        Analyze patent landscape and freedom-to-operate
        
        Args:
            drug_name: Drug name to analyze
            
        Returns:
            Patent landscape analysis
        """
        try:
            # Search for patents
            patent_data = USPTOPatentAPI.search_patents(drug_name, max_results=50)
            patents = patent_data.get("patents", [])
            
            # Analyze patent status
            active_patents = [p for p in patents if p.get("status") == "Active"]
            expired_patents = [p for p in patents if p.get("status") == "Expired"]
            
            # Analyze assignees
            assignees = {}
            for patent in patents:
                assignee = patent.get("assignee", "Unknown")
                assignees[assignee] = assignees.get(assignee, 0) + 1
            
            # Analyze timeline
            filing_years = {}
            for patent in patents:
                filing_date = patent.get("filing_date", "")
                if filing_date:
                    year = filing_date.split("-")[0]
                    filing_years[year] = filing_years.get(year, 0) + 1
            
            return {
                "drug_name": drug_name,
                "total_patents": len(patents),
                "active_patents": len(active_patents),
                "expired_patents": len(expired_patents),
                "top_assignees": dict(sorted(assignees.items(), key=lambda x: x[1], reverse=True)[:5]),
                "filing_trend": dict(sorted(filing_years.items())),
                "freedom_to_operate": {
                    "risk_level": "Medium" if len(active_patents) > 5 else "Low",
                    "active_barriers": len(active_patents),
                    "recommendation": "Patent clearance search recommended" if len(active_patents) > 10 else "Relatively clear landscape"
                },
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Patent landscape analysis error: {e}")
            return {
                "drug_name": drug_name,
                "error": str(e)
            }
    
    @staticmethod
    def check_patent_expiry(patent_number: str) -> Dict[str, Any]:
        """
        Check patent expiration status
        
        Args:
            patent_number: Patent number to check
            
        Returns:
            Patent expiry information
        """
        # Mock implementation
        return {
            "patent_number": patent_number,
            "status": "Active",
            "grant_date": "2021-06-15",
            "expiry_date": "2041-06-15",
            "years_remaining": 16.5,
            "note": "This is mock data. Real implementation would query USPTO database."
        }


def search_patents_tool(drug_name: str, condition: str = "") -> str:
    """
    LangChain tool wrapper for patent search
    
    Args:
        drug_name: Drug name to search
        condition: Optional condition
        
    Returns:
        Formatted string with patent results
    """
    results = USPTOPatentAPI.search_patents(
        drug_name=drug_name,
        condition=condition if condition else None,
        max_results=10
    )
    
    if results.get("error"):
        return f"Error searching patents: {results['error']}"
    
    patents = results.get("patents", [])
    if not patents:
        return f"No patents found for {drug_name}"
    
    output = f"Found {len(patents)} patents for {drug_name}:\n\n"
    for i, patent in enumerate(patents[:5], 1):
        output += f"{i}. {patent.get('title')}\n"
        output += f"   Patent: {patent.get('patent_number')}, Status: {patent.get('status')}\n"
        output += f"   Assignee: {patent.get('assignee')}\n"
        output += f"   Grant Date: {patent.get('grant_date')}\n\n"
    
    return output


def analyze_patent_landscape_tool(drug_name: str) -> str:
    """
    LangChain tool wrapper for patent landscape analysis
    
    Args:
        drug_name: Drug name to analyze
        
    Returns:
        Formatted analysis string
    """
    analysis = USPTOPatentAPI.analyze_patent_landscape(drug_name)
    
    if analysis.get("error"):
        return f"Error analyzing patent landscape: {analysis['error']}"
    
    fto = analysis.get("freedom_to_operate", {})
    
    output = f"Patent Landscape Analysis for {drug_name}:\n\n"
    output += f"Total Patents: {analysis.get('total_patents')}\n"
    output += f"Active Patents: {analysis.get('active_patents')}\n"
    output += f"Expired Patents: {analysis.get('expired_patents')}\n\n"
    output += f"Freedom to Operate:\n"
    output += f"  Risk Level: {fto.get('risk_level')}\n"
    output += f"  Active Barriers: {fto.get('active_barriers')}\n"
    output += f"  Recommendation: {fto.get('recommendation')}\n\n"
    output += f"Top Patent Holders: {', '.join(list(analysis.get('top_assignees', {}).keys())[:3])}\n"
    
    return output
