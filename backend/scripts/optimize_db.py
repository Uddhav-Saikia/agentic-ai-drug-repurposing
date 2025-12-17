"""
Database optimization utilities
"""
from sqlalchemy import text
from core.database import engine


def create_indexes():
    """Create database indexes for performance"""
    with engine.connect() as conn:
        # Query indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_queries_status 
            ON queries(status);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_queries_created_at 
            ON queries(created_at DESC);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_queries_updated_at 
            ON queries(updated_at DESC);
        """))
        
        # Report indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_reports_query_id 
            ON reports(query_id);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_reports_created_at 
            ON reports(created_at DESC);
        """))
        
        # Drug candidate indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_drug_candidates_report_id 
            ON drug_candidates(report_id);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_drug_candidates_confidence 
            ON drug_candidates(confidence_score DESC);
        """))
        
        # Task indexes
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_tasks_query_id 
            ON tasks(query_id);
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_tasks_status 
            ON tasks(status);
        """))
        
        # Embedding indexes for vector search
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_embeddings_vector 
            ON embeddings USING ivfflat (vector vector_cosine_ops)
            WITH (lists = 100);
        """))
        
        conn.commit()
        print("✓ Database indexes created successfully")


def analyze_query_performance():
    """Analyze slow queries"""
    with engine.connect() as conn:
        # Enable query statistics
        conn.execute(text("""
            CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
        """))
        
        # Get slow queries
        result = conn.execute(text("""
            SELECT 
                query,
                calls,
                total_time,
                mean_time,
                max_time
            FROM pg_stat_statements
            WHERE mean_time > 100
            ORDER BY mean_time DESC
            LIMIT 10;
        """))
        
        print("\n=== Slow Queries ===")
        for row in result:
            print(f"Query: {row.query[:100]}")
            print(f"Calls: {row.calls}, Mean: {row.mean_time:.2f}ms, Max: {row.max_time:.2f}ms\n")


def vacuum_database():
    """Vacuum and analyze database"""
    with engine.connect() as conn:
        conn.execute(text("VACUUM ANALYZE;"))
        print("✓ Database vacuumed and analyzed")


def get_table_sizes():
    """Get size of each table"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
                pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY size_bytes DESC;
        """))
        
        print("\n=== Table Sizes ===")
        for row in result:
            print(f"{row.tablename}: {row.size}")


if __name__ == "__main__":
    print("Running database optimizations...")
    create_indexes()
    vacuum_database()
    get_table_sizes()
    print("\n✓ Database optimization complete")
