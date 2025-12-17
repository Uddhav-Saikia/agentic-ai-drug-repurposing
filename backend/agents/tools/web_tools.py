"""
Tools for Web Intelligence Agent
"""
import requests
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from bs4 import BeautifulSoup
import re

logger = logging.getLogger(__name__)


class PubMedAPI:
    """
    Interface for PubMed/NCBI literature search
    """
    
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    
    @staticmethod
    def search_literature(
        drug_name: str,
        condition: str,
        max_results: int = 20
    ) -> Dict[str, Any]:
        """
        Search PubMed for relevant literature
        
        Args:
            drug_name: Drug name
            condition: Medical condition
            max_results: Maximum results to return
            
        Returns:
            Literature search results
        """
        try:
            # Build search query
            query = f"{drug_name} AND {condition}"
            logger.info(f"Searching PubMed for: {query}")
            
            # Search PubMed (esearch)
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmax": max_results,
                "retmode": "json",
                "sort": "relevance"
            }
            
            search_response = requests.get(
                f"{PubMedAPI.BASE_URL}/esearch.fcgi",
                params=search_params,
                timeout=30
            )
            search_response.raise_for_status()
            search_data = search_response.json()
            
            # Get list of PMIDs
            pmids = search_data.get("esearchresult", {}).get("idlist", [])
            
            if not pmids:
                return {
                    "total_count": 0,
                    "articles": [],
                    "sources": ["PubMed"],
                    "query_timestamp": datetime.utcnow().isoformat()
                }
            
            # Fetch article details (esummary)
            summary_params = {
                "db": "pubmed",
                "id": ",".join(pmids),
                "retmode": "json"
            }
            
            summary_response = requests.get(
                f"{PubMedAPI.BASE_URL}/esummary.fcgi",
                params=summary_params,
                timeout=30
            )
            summary_response.raise_for_status()
            summary_data = summary_response.json()
            
            # Extract article information
            articles = []
            result_data = summary_data.get("result", {})
            
            for pmid in pmids:
                if pmid in result_data:
                    article = result_data[pmid]
                    articles.append({
                        "pmid": pmid,
                        "title": article.get("title", ""),
                        "authors": [
                            author.get("name", "") 
                            for author in article.get("authors", [])[:3]
                        ],
                        "journal": article.get("fulljournalname", ""),
                        "pub_date": article.get("pubdate", ""),
                        "pub_type": article.get("pubtype", []),
                        "source": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                    })
            
            return {
                "total_count": len(articles),
                "articles": articles,
                "sources": ["PubMed"],
                "query_timestamp": datetime.utcnow().isoformat()
            }
            
        except requests.RequestException as e:
            logger.error(f"PubMed API error: {e}")
            return {
                "total_count": 0,
                "articles": [],
                "error": str(e),
                "sources": ["PubMed"],
                "query_timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Unexpected error in PubMed search: {e}")
            return {
                "total_count": 0,
                "articles": [],
                "error": str(e),
                "sources": ["PubMed"]
            }
    
    @staticmethod
    def analyze_literature_trends(
        drug_name: str,
        condition: str
    ) -> Dict[str, Any]:
        """
        Analyze publication trends and research focus
        
        Args:
            drug_name: Drug name
            condition: Medical condition
            
        Returns:
            Literature trend analysis
        """
        try:
            # Get literature data
            lit_data = PubMedAPI.search_literature(drug_name, condition, max_results=50)
            articles = lit_data.get("articles", [])
            
            if not articles:
                return {
                    "drug_name": drug_name,
                    "condition": condition,
                    "total_publications": 0,
                    "message": "No publications found"
                }
            
            # Analyze publication years
            year_distribution = {}
            journal_distribution = {}
            
            for article in articles:
                pub_date = article.get("pub_date", "")
                year_match = re.search(r'\d{4}', pub_date)
                if year_match:
                    year = year_match.group()
                    year_distribution[year] = year_distribution.get(year, 0) + 1
                
                journal = article.get("journal", "Unknown")
                journal_distribution[journal] = journal_distribution.get(journal, 0) + 1
            
            # Determine trend
            years = sorted(year_distribution.keys())
            trend = "Increasing" if len(years) > 2 and year_distribution.get(years[-1], 0) > year_distribution.get(years[0], 0) else "Stable"
            
            return {
                "drug_name": drug_name,
                "condition": condition,
                "total_publications": len(articles),
                "year_distribution": dict(sorted(year_distribution.items(), reverse=True)[:5]),
                "top_journals": dict(sorted(journal_distribution.items(), key=lambda x: x[1], reverse=True)[:5]),
                "publication_trend": trend,
                "recent_focus": "Clinical research" if len([a for a in articles if "Clinical" in str(a.get("pub_type", []))]) > 5 else "Basic research",
                "analysis_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Literature trend analysis error: {e}")
            return {
                "drug_name": drug_name,
                "condition": condition,
                "error": str(e)
            }


class WebIntelligence:
    """
    General web intelligence gathering
    """
    
    @staticmethod
    def search_news_articles(drug_name: str, condition: str) -> Dict[str, Any]:
        """
        Search for recent news articles (mock implementation)
        
        Args:
            drug_name: Drug name
            condition: Medical condition
            
        Returns:
            News articles data
        """
        # Mock news data
        return {
            "total_count": 5,
            "articles": [
                {
                    "title": f"New study shows promise for {drug_name} in {condition}",
                    "source": "Medical News Today",
                    "date": "2024-11-15",
                    "url": "https://example.com/news1",
                    "sentiment": "Positive"
                },
                {
                    "title": f"Researchers investigate {drug_name} for {condition} treatment",
                    "source": "ScienceDaily",
                    "date": "2024-10-20",
                    "url": "https://example.com/news2",
                    "sentiment": "Neutral"
                }
            ],
            "overall_sentiment": "Positive",
            "sources": ["News aggregators"],
            "note": "This is mock data. Real implementation would use news APIs."
        }


def search_pubmed_tool(drug_name: str, condition: str) -> str:
    """
    LangChain tool wrapper for PubMed search
    
    Args:
        drug_name: Drug name
        condition: Medical condition
        
    Returns:
        Formatted literature results
    """
    results = PubMedAPI.search_literature(drug_name, condition, max_results=10)
    
    if results.get("error"):
        return f"Error searching PubMed: {results['error']}"
    
    articles = results.get("articles", [])
    if not articles:
        return f"No publications found for {drug_name} and {condition}"
    
    output = f"Found {len(articles)} publications on PubMed:\n\n"
    for i, article in enumerate(articles[:5], 1):
        output += f"{i}. {article.get('title')}\n"
        output += f"   Authors: {', '.join(article.get('authors', [])[:2])}\n"
        output += f"   Journal: {article.get('journal')}, {article.get('pub_date')}\n"
        output += f"   PMID: {article.get('pmid')}\n\n"
    
    return output


def analyze_literature_trends_tool(drug_name: str, condition: str) -> str:
    """
    LangChain tool wrapper for literature trend analysis
    
    Args:
        drug_name: Drug name
        condition: Medical condition
        
    Returns:
        Formatted trend analysis
    """
    analysis = PubMedAPI.analyze_literature_trends(drug_name, condition)
    
    if analysis.get("error"):
        return f"Error analyzing literature: {analysis['error']}"
    
    output = f"Literature Trend Analysis for {drug_name} and {condition}:\n\n"
    output += f"Total Publications: {analysis.get('total_publications', 0)}\n"
    output += f"Publication Trend: {analysis.get('publication_trend')}\n"
    output += f"Recent Focus: {analysis.get('recent_focus')}\n\n"
    
    year_dist = analysis.get('year_distribution', {})
    if year_dist:
        output += "Recent Publications by Year:\n"
        for year, count in list(year_dist.items())[:5]:
            output += f"  {year}: {count} publications\n"
    
    return output
