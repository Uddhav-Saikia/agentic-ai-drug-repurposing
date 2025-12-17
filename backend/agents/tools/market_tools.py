"""
Tools for Market Intelligence Agent
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import random

logger = logging.getLogger(__name__)


class MarketIntelligenceAPI:
    """
    Interface for market intelligence data (IQVIA, market reports, etc.)
    Note: Real IQVIA API requires subscription and authentication
    """
    
    @staticmethod
    def get_market_size(condition: str, region: str = "Global") -> Dict[str, Any]:
        """
        Get market size estimates for a condition
        
        Args:
            condition: Medical condition
            region: Geographic region (Global, US, EU, etc.)
            
        Returns:
            Market size data
        """
        try:
            logger.info(f"Fetching market size for {condition} in {region}")
            
            # Mock data (replace with real API in production)
            # Realistic estimates based on common conditions
            market_data = {
                "condition": condition,
                "region": region,
                "market_size_usd": random.randint(5, 50) * 1e9,  # $5B-$50B
                "market_size_year": 2024,
                "projected_cagr": round(random.uniform(3.5, 12.5), 2),  # 3.5%-12.5%
                "projected_2030": None,
                "patient_population": random.randint(10, 500) * 1e6,  # 10M-500M
                "treatment_rate": round(random.uniform(0.3, 0.8), 2),  # 30%-80%
                "sources": ["IQVIA Market Report", "Industry Analysis"],
                "timestamp": datetime.utcnow().isoformat(),
                "note": "This is mock data. Real implementation requires IQVIA subscription."
            }
            
            # Calculate projection
            current_size = market_data["market_size_usd"]
            cagr = market_data["projected_cagr"] / 100
            years = 6  # 2024 to 2030
            market_data["projected_2030"] = round(current_size * ((1 + cagr) ** years), 2)
            
            return market_data
            
        except Exception as e:
            logger.error(f"Market size query error: {e}")
            return {
                "condition": condition,
                "region": region,
                "error": str(e)
            }
    
    @staticmethod
    def analyze_competitive_landscape(
        condition: str,
        drug_class: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze competitive landscape for a condition
        
        Args:
            condition: Medical condition
            drug_class: Drug class (optional)
            
        Returns:
            Competitive landscape data
        """
        try:
            logger.info(f"Analyzing competitive landscape for {condition}")
            
            # Mock competitive data
            competitors = [
                {
                    "drug_name": f"DrugA-{random.randint(100, 999)}",
                    "manufacturer": ["Pfizer", "Novartis", "Roche", "AstraZeneca"][random.randint(0, 3)],
                    "market_share": round(random.uniform(5, 30), 2),
                    "approval_year": random.randint(2015, 2023),
                    "status": "Approved"
                },
                {
                    "drug_name": f"DrugB-{random.randint(100, 999)}",
                    "manufacturer": ["J&J", "Merck", "GSK", "Eli Lilly"][random.randint(0, 3)],
                    "market_share": round(random.uniform(5, 25), 2),
                    "approval_year": random.randint(2016, 2024),
                    "status": "Approved"
                },
                {
                    "drug_name": f"DrugC-{random.randint(100, 999)}",
                    "manufacturer": ["Amgen", "BMS", "Sanofi"][random.randint(0, 2)],
                    "market_share": round(random.uniform(3, 20), 2),
                    "approval_year": random.randint(2018, 2024),
                    "status": "Approved"
                }
            ]
            
            # Pipeline drugs
            pipeline = [
                {
                    "drug_name": f"Pipeline-{random.randint(100, 999)}",
                    "company": "Emerging Biotech",
                    "phase": ["Phase II", "Phase III"][random.randint(0, 1)],
                    "estimated_launch": random.randint(2025, 2028)
                }
                for _ in range(3)
            ]
            
            return {
                "condition": condition,
                "drug_class": drug_class,
                "approved_drugs": competitors,
                "pipeline_drugs": pipeline,
                "market_concentration": "Moderate",
                "top_3_market_share": sum([c["market_share"] for c in competitors[:3]]),
                "generic_competition": random.choice([True, False]),
                "analysis_timestamp": datetime.utcnow().isoformat(),
                "note": "This is mock data. Real implementation requires market database access."
            }
            
        except Exception as e:
            logger.error(f"Competitive analysis error: {e}")
            return {
                "condition": condition,
                "error": str(e)
            }
    
    @staticmethod
    def get_pricing_data(drug_name: str, region: str = "US") -> Dict[str, Any]:
        """
        Get pricing and reimbursement data
        
        Args:
            drug_name: Drug name
            region: Geographic region
            
        Returns:
            Pricing data
        """
        try:
            logger.info(f"Fetching pricing data for {drug_name} in {region}")
            
            return {
                "drug_name": drug_name,
                "region": region,
                "average_wholesale_price": round(random.uniform(100, 5000), 2),
                "currency": "USD",
                "pricing_model": random.choice(["Per dose", "Per month", "Per treatment cycle"]),
                "reimbursement_status": random.choice(["Covered", "Partial coverage", "Prior authorization required"]),
                "patient_out_of_pocket": round(random.uniform(20, 500), 2),
                "price_trend": random.choice(["Stable", "Increasing", "Decreasing"]),
                "sources": ["Drug Pricing Database"],
                "timestamp": datetime.utcnow().isoformat(),
                "note": "This is mock data."
            }
            
        except Exception as e:
            logger.error(f"Pricing data error: {e}")
            return {
                "drug_name": drug_name,
                "error": str(e)
            }


def get_market_size_tool(condition: str, region: str = "Global") -> str:
    """
    LangChain tool wrapper for market size data
    
    Args:
        condition: Medical condition
        region: Geographic region
        
    Returns:
        Formatted market size string
    """
    data = MarketIntelligenceAPI.get_market_size(condition, region)
    
    if data.get("error"):
        return f"Error fetching market data: {data['error']}"
    
    output = f"Market Intelligence for {condition} ({region}):\n\n"
    output += f"Current Market Size (2024): ${data.get('market_size_usd', 0) / 1e9:.2f}B USD\n"
    output += f"Projected CAGR: {data.get('projected_cagr')}%\n"
    output += f"Projected Market Size (2030): ${data.get('projected_2030', 0) / 1e9:.2f}B USD\n"
    output += f"Patient Population: {data.get('patient_population', 0) / 1e6:.1f}M\n"
    output += f"Treatment Rate: {data.get('treatment_rate', 0) * 100:.0f}%\n"
    
    return output


def analyze_competition_tool(condition: str) -> str:
    """
    LangChain tool wrapper for competitive analysis
    
    Args:
        condition: Medical condition
        
    Returns:
        Formatted competitive analysis
    """
    data = MarketIntelligenceAPI.analyze_competitive_landscape(condition)
    
    if data.get("error"):
        return f"Error analyzing competition: {data['error']}"
    
    approved = data.get("approved_drugs", [])
    pipeline = data.get("pipeline_drugs", [])
    
    output = f"Competitive Landscape for {condition}:\n\n"
    output += f"Approved Drugs: {len(approved)}\n"
    
    for drug in approved[:3]:
        output += f"  - {drug['drug_name']} ({drug['manufacturer']}): {drug['market_share']}% market share\n"
    
    output += f"\nPipeline Drugs: {len(pipeline)}\n"
    for drug in pipeline[:3]:
        output += f"  - {drug['drug_name']} ({drug['company']}): {drug['phase']}\n"
    
    output += f"\nTop 3 Market Share: {data.get('top_3_market_share', 0):.1f}%\n"
    output += f"Market Concentration: {data.get('market_concentration')}\n"
    
    return output
