"""
Initialize database tables and verify setup
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import create_engine, text
from core.config import settings
from core.database import Base
from models.database_models import Query, Task, Report, DrugCandidate, Embedding

def init_database():
    """Initialize database with all tables"""
    print("🔧 Initializing database...")
    print(f"Database URL: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else 'local'}")
    
    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully")
        
        # Verify tables exist
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result]
            
            expected_tables = ['queries', 'tasks', 'reports', 'drug_candidates', 'embeddings']
            for table in expected_tables:
                if table in tables:
                    print(f"  ✅ {table}")
                else:
                    print(f"  ⚠️  {table} not found")
        
        # Check for pgvector extension
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS(
                    SELECT 1 FROM pg_extension WHERE extname = 'vector'
                )
            """))
            has_vector = result.scalar()
            
            if has_vector:
                print("✅ pgvector extension is installed")
            else:
                print("⚠️  pgvector extension not found - run database/init.sql")
        
        print("\n✅ Database initialization complete!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def verify_setup():
    """Verify complete backend setup"""
    print("\n" + "="*60)
    print("🔍 Verifying Phase 3 Setup")
    print("="*60 + "\n")
    
    # Check database
    db_ok = init_database()
    
    # Check imports
    print("\n🔧 Checking imports...")
    try:
        from models.database_models import Query, Task, Report, DrugCandidate
        from models.schemas import QueryCreate, QueryResponse, AnalysisResult
        from services.query_service import QueryService
        from services.report_service import ReportService
        from services.agent_service import AgentService
        from services.celery_tasks import run_analysis_task
        from api.routes import queries, reports, agents
        print("✅ All imports successful")
        imports_ok = True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        imports_ok = False
    
    # Check Redis connection
    print("\n🔧 Checking Redis connection...")
    try:
        import redis
        r = redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        r.ping()
        print("✅ Redis connection successful")
        redis_ok = True
    except Exception as e:
        print(f"⚠️  Redis not available: {e}")
        print("   (Optional for development, required for production)")
        redis_ok = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 Setup Summary")
    print("="*60)
    print(f"Database:  {'✅' if db_ok else '❌'}")
    print(f"Imports:   {'✅' if imports_ok else '❌'}")
    print(f"Redis:     {'✅' if redis_ok else '⚠️  (optional)'}")
    
    if db_ok and imports_ok:
        print("\n✅ Phase 3 setup complete!")
        print("\n📝 Next steps:")
        print("1. Start the server: uvicorn main:app --reload")
        print("2. View API docs: http://localhost:8000/api/v1/docs")
        print("3. Submit a query via API")
        print("4. Proceed to Phase 4 (Frontend)")
        return True
    else:
        print("\n❌ Setup incomplete - please fix errors above")
        return False


if __name__ == "__main__":
    verify_setup()
