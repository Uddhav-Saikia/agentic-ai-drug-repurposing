-- Initialize Database for Drug Repurposing System

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create queries table
CREATE TABLE IF NOT EXISTS queries (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255),
    query_text TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create tasks table (for agent sub-tasks)
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    query_id INTEGER REFERENCES queries(id) ON DELETE CASCADE,
    agent_type VARCHAR(100) NOT NULL,
    task_description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    result JSONB,
    error TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create reports table
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    query_id INTEGER REFERENCES queries(id) ON DELETE CASCADE,
    title VARCHAR(500),
    content TEXT,
    summary TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create drug_candidates table
CREATE TABLE IF NOT EXISTS drug_candidates (
    id SERIAL PRIMARY KEY,
    report_id INTEGER REFERENCES reports(id) ON DELETE CASCADE,
    drug_name VARCHAR(255) NOT NULL,
    indication VARCHAR(500),
    confidence_score FLOAT,
    market_data JSONB,
    patent_data JSONB,
    clinical_data JSONB,
    web_intelligence JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create vector embeddings table
CREATE TABLE IF NOT EXISTS embeddings (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB,
    source VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index on vector embeddings for similarity search
CREATE INDEX IF NOT EXISTS embeddings_vector_idx ON embeddings 
USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_queries_status ON queries(status);
CREATE INDEX IF NOT EXISTS idx_queries_created_at ON queries(created_at);
CREATE INDEX IF NOT EXISTS idx_tasks_query_id ON tasks(query_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_reports_query_id ON reports(query_id);
CREATE INDEX IF NOT EXISTS idx_drug_candidates_report_id ON drug_candidates(report_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for queries table
CREATE TRIGGER update_queries_updated_at BEFORE UPDATE ON queries
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data for testing
INSERT INTO queries (user_id, query_text, status) VALUES 
    ('test_user', 'Find drug repurposing opportunities for Alzheimer''s disease', 'completed'),
    ('test_user', 'Identify candidates for COVID-19 treatment', 'pending');

COMMENT ON TABLE queries IS 'Stores user queries for drug repurposing research';
COMMENT ON TABLE tasks IS 'Tracks individual agent tasks for each query';
COMMENT ON TABLE reports IS 'Stores generated reports from agent analysis';
COMMENT ON TABLE drug_candidates IS 'Stores identified drug repurposing candidates';
COMMENT ON TABLE embeddings IS 'Stores vector embeddings for semantic search';
