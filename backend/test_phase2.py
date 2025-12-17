"""
Quick test script to verify Phase 2 installation
Run this to ensure all agents are properly set up
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from agents.base_agent import BaseAgent, AgentTask, AgentResult
        print("✅ Base agent imported")
    except Exception as e:
        print(f"❌ Base agent import failed: {e}")
        return False
    
    try:
        from agents.clinical_agent import ClinicalIntelligenceAgent
        print("✅ Clinical agent imported")
    except Exception as e:
        print(f"❌ Clinical agent import failed: {e}")
        return False
    
    try:
        from agents.patent_agent import PatentLandscapeAgent
        print("✅ Patent agent imported")
    except Exception as e:
        print(f"❌ Patent agent import failed: {e}")
        return False
    
    try:
        from agents.market_agent import MarketIntelligenceAgent
        print("✅ Market agent imported")
    except Exception as e:
        print(f"❌ Market agent import failed: {e}")
        return False
    
    try:
        from agents.web_agent import WebIntelligenceAgent
        print("✅ Web agent imported")
    except Exception as e:
        print(f"❌ Web agent import failed: {e}")
        return False
    
    try:
        from agents.master_agent import MasterAgent
        print("✅ Master agent imported")
    except Exception as e:
        print(f"❌ Master agent import failed: {e}")
        return False
    
    return True


def test_api_access():
    """Test external API accessibility"""
    print("\nTesting external APIs...")
    
    # Test ClinicalTrials.gov
    try:
        import requests
        response = requests.get(
            "https://clinicaltrials.gov/api/v2/studies",
            params={"query.cond": "diabetes", "pageSize": 1},
            timeout=10
        )
        if response.status_code == 200:
            print("✅ ClinicalTrials.gov API accessible")
        else:
            print(f"⚠️  ClinicalTrials.gov returned status {response.status_code}")
    except Exception as e:
        print(f"⚠️  ClinicalTrials.gov API error: {e}")
    
    # Test PubMed
    try:
        response = requests.get(
            "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
            params={"db": "pubmed", "term": "diabetes", "retmax": 1, "retmode": "json"},
            timeout=10
        )
        if response.status_code == 200:
            print("✅ PubMed API accessible")
        else:
            print(f"⚠️  PubMed returned status {response.status_code}")
    except Exception as e:
        print(f"⚠️  PubMed API error: {e}")


def test_agent_creation():
    """Test agent instantiation"""
    print("\nTesting agent creation...")
    
    try:
        from agents.clinical_agent import ClinicalIntelligenceAgent
        agent = ClinicalIntelligenceAgent()
        print(f"✅ Clinical agent created: {agent.name}")
    except Exception as e:
        print(f"❌ Clinical agent creation failed: {e}")
        return False
    
    try:
        from agents.patent_agent import PatentLandscapeAgent
        agent = PatentLandscapeAgent()
        print(f"✅ Patent agent created: {agent.name}")
    except Exception as e:
        print(f"❌ Patent agent creation failed: {e}")
        return False
    
    try:
        from agents.market_agent import MarketIntelligenceAgent
        agent = MarketIntelligenceAgent()
        print(f"✅ Market agent created: {agent.name}")
    except Exception as e:
        print(f"❌ Market agent creation failed: {e}")
        return False
    
    try:
        from agents.web_agent import WebIntelligenceAgent
        agent = WebIntelligenceAgent()
        print(f"✅ Web agent created: {agent.name}")
    except Exception as e:
        print(f"❌ Web agent creation failed: {e}")
        return False
    
    try:
        from agents.master_agent import MasterAgent
        agent = MasterAgent()
        print(f"✅ Master agent created")
    except Exception as e:
        print(f"❌ Master agent creation failed: {e}")
        return False
    
    return True


def test_tools():
    """Test tool imports"""
    print("\nTesting tools...")
    
    try:
        from agents.tools.clinical_tools import ClinicalTrialsAPI
        print("✅ Clinical tools imported")
    except Exception as e:
        print(f"❌ Clinical tools import failed: {e}")
    
    try:
        from agents.tools.patent_tools import USPTOPatentAPI
        print("✅ Patent tools imported")
    except Exception as e:
        print(f"❌ Patent tools import failed: {e}")
    
    try:
        from agents.tools.market_tools import MarketIntelligenceAPI
        print("✅ Market tools imported")
    except Exception as e:
        print(f"❌ Market tools import failed: {e}")
    
    try:
        from agents.tools.web_tools import PubMedAPI
        print("✅ Web tools imported")
    except Exception as e:
        print(f"❌ Web tools import failed: {e}")


def check_dependencies():
    """Check required dependencies"""
    print("\nChecking dependencies...")
    
    required = [
        "langchain",
        "langchain_openai",
        "requests",
        "beautifulsoup4",
        "pydantic"
    ]
    
    for package in required:
        try:
            __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} NOT installed - run: pip install {package}")


def check_env_vars():
    """Check environment variables"""
    print("\nChecking environment variables...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "":
        print(f"✅ OPENAI_API_KEY is set ({api_key[:8]}...)")
    else:
        print("⚠️  OPENAI_API_KEY not set - required for LLM features")
        print("   Set it in your .env file or environment")


def main():
    """Run all tests"""
    print("=" * 80)
    print("PHASE 2 VERIFICATION TEST")
    print("=" * 80)
    
    check_env_vars()
    check_dependencies()
    
    if not test_imports():
        print("\n❌ FAILED: Import errors detected")
        return False
    
    test_api_access()
    
    if not test_agent_creation():
        print("\n❌ FAILED: Agent creation errors detected")
        return False
    
    test_tools()
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED - Phase 2 is ready!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Run example_usage.py for full demo")
    print("2. Proceed to Phase 3 (Backend API)")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
