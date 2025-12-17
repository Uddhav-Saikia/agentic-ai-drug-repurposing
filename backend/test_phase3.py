"""
Test Phase 3 implementation
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test all Phase 3 imports"""
    print("🔧 Testing imports...")
    
    try:
        # Models
        from models.database_models import Query, Task, Report, DrugCandidate, Embedding
        from models.schemas import (
            QueryCreate, QueryResponse, QueryStatus, AnalysisResult,
            TaskResponse, ReportResponse, ReportDetail, DrugCandidateResponse,
            AgentStatusResponse, SystemStatus
        )
        print("  ✅ Models imported successfully")
        
        # Services
        from services.query_service import QueryService
        from services.report_service import ReportService
        from services.agent_service import AgentService
        from services.celery_tasks import run_analysis_task
        print("  ✅ Services imported successfully")
        
        # API Routes
        from api.routes import queries, reports, agents, health
        print("  ✅ API routes imported successfully")
        
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_schemas():
    """Test Pydantic schemas"""
    print("\n🔧 Testing schemas...")
    
    try:
        from models.schemas import QueryCreate, QueryResponse
        
        # Test QueryCreate
        query_data = QueryCreate(
            query_text="Test query for Alzheimer's disease",
            user_id="test_user"
        )
        assert query_data.query_text == "Test query for Alzheimer's disease"
        assert query_data.user_id == "test_user"
        print("  ✅ QueryCreate schema works")
        
        return True
    except Exception as e:
        print(f"  ❌ Schema test failed: {e}")
        return False


def test_database_models():
    """Test database model definitions"""
    print("\n🔧 Testing database models...")
    
    try:
        from models.database_models import Query, Task, Report, DrugCandidate, Embedding
        
        # Verify model attributes
        assert hasattr(Query, 'query_text')
        assert hasattr(Task, 'agent_type')
        assert hasattr(Report, 'content')
        assert hasattr(DrugCandidate, 'drug_name')
        assert hasattr(Embedding, 'embedding')
        print("  ✅ Database models defined correctly")
        
        return True
    except Exception as e:
        print(f"  ❌ Model test failed: {e}")
        return False


def test_api_endpoints():
    """Test API endpoint definitions"""
    print("\n🔧 Testing API endpoints...")
    
    try:
        from api.routes import queries, reports, agents
        
        # Check routers exist
        assert hasattr(queries, 'router')
        assert hasattr(reports, 'router')
        assert hasattr(agents, 'router')
        print("  ✅ API routers defined")
        
        # Check endpoint functions exist
        assert hasattr(queries, 'create_query')
        assert hasattr(queries, 'get_query')
        assert hasattr(queries, 'get_query_status')
        assert hasattr(reports, 'get_report')
        assert hasattr(agents, 'get_system_status')
        print("  ✅ API endpoints defined")
        
        return True
    except Exception as e:
        print(f"  ❌ API test failed: {e}")
        return False


def run_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 Testing Phase 3 Implementation")
    print("="*60 + "\n")
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Schemas", test_schemas()))
    results.append(("Database Models", test_database_models()))
    results.append(("API Endpoints", test_api_endpoints()))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✅ ALL TESTS PASSED - Phase 3 backend is ready!")
        print("\n📝 Next steps:")
        print("1. Run: python init_database.py  # Initialize database")
        print("2. Start Docker: docker-compose up -d postgres redis")
        print("3. Start server: uvicorn main:app --reload")
        print("4. Test API: http://localhost:8000/api/v1/docs")
        return True
    else:
        print("\n❌ Some tests failed - please fix errors above")
        return False


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
