# Phase 1: Setup Guide

## Prerequisites Installation

### 1. Install Python 3.11+
```bash
# Check Python version
python --version

# If not installed, download from python.org
```

### 2. Install Node.js 18+
```bash
# Check Node version
node --version

# If not installed, download from nodejs.org
```

### 3. Install Docker Desktop
- Download from docker.com
- Ensure Docker Compose is included

## Project Setup Steps

### Step 1: Create Virtual Environment (Windows)
```bash
cd "d:\Odin Project\repo\agentic ai drug repurposing\backend"
python -m venv venv
venv\Scripts\activate
```

### Step 2: Install Python Dependencies
```bash
# Make sure you're in backend directory with venv activated
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Set Up Environment Variables
```bash
# Copy the example env file
copy .env.example .env

# Edit .env and add your OpenAI API key:
# OPENAI_API_KEY=sk-your-actual-api-key-here
```

### Step 4: Start Database with Docker
```bash
# From project root directory
docker-compose up -d postgres redis
```

### Step 5: Verify Database Setup
```bash
# Check if containers are running
docker ps

# Should see postgres and redis containers running
```

### Step 6: Test Backend
```bash
# From backend directory with venv activated
python main.py
```

Then visit: http://localhost:8000/docs

## Directory Structure Created

```
agentic-ai-drug-repurposing/
├── backend/
│   ├── agents/              # AI agents (Phase 2)
│   ├── api/
│   │   └── routes/
│   │       ├── health.py    # Health check endpoints
│   │       ├── queries.py   # Query endpoints (Phase 3)
│   │       ├── agents.py    # Agent endpoints (Phase 3)
│   │       └── reports.py   # Report endpoints (Phase 3)
│   ├── core/
│   │   ├── config.py        # Configuration management
│   │   ├── database.py      # Database connection
│   │   └── celery_app.py    # Background tasks
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── requirements-dev.txt # Development dependencies
├── database/
│   └── init.sql            # Database initialization
├── docker/
│   ├── Dockerfile.backend  # Backend container
│   └── Dockerfile.frontend # Frontend container (Phase 4)
├── docker-compose.yml      # Multi-container orchestration
├── .env.example           # Environment template
├── .gitignore            # Git ignore rules
├── README.md             # Project overview
└── SETUP_GUIDE.md        # This file
```

## Verification Steps

### 1. Test Health Endpoints
```bash
# Basic health check
curl http://localhost:8000/v1/health

# Database health
curl http://localhost:8000/v1/health/db

# Redis health
curl http://localhost:8000/v1/health/redis

# Full health check
curl http://localhost:8000/v1/health/full
```

### 2. Check API Documentation
- Open browser: http://localhost:8000/docs
- You should see Swagger UI with available endpoints

### 3. Verify Database Tables
```bash
# Connect to postgres container
docker exec -it drug_repurposing_db psql -U postgres -d drug_repurposing

# List tables
\dt

# You should see: queries, tasks, reports, drug_candidates, embeddings
\q
```

## Common Issues & Solutions

### Issue: Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :8000

# Stop the process or change port in .env
```

### Issue: Docker Permission Denied
- Restart Docker Desktop
- Run as Administrator

### Issue: Database Connection Error
```bash
# Check if postgres is running
docker ps | findstr postgres

# Restart postgres
docker-compose restart postgres
```

## Next Steps

Once Phase 1 is complete and verified:
1. All health checks pass ✓
2. API documentation loads ✓
3. Database tables created ✓

You're ready for **Phase 2: Agentic Core (AI/ML Logic)**

---

## Tech Stack Summary

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend Framework | FastAPI | REST API server |
| AI Orchestration | LangChain + CrewAI | Agent coordination |
| Database | PostgreSQL + pgvector | Data & vector storage |
| Caching | Redis | Query caching & task queue |
| Background Tasks | Celery | Async agent execution |
| Containerization | Docker | Service isolation |
| Frontend | Next.js | User interface (Phase 4) |

## Architecture Decision: Why CrewAI + LangChain?

**CrewAI** is recommended for this project because:
1. **Role-based agents**: Perfect for specialized agents (Market, Patent, Clinical, Web)
2. **Built-in orchestration**: Handles agent coordination automatically
3. **Task delegation**: Master agent can delegate to worker agents seamlessly
4. **LangChain integration**: Uses LangChain under the hood for tool usage

**LangChain** provides:
1. **Tool abstraction**: Easy integration with APIs (ClinicalTrials.gov, USPTO)
2. **Memory management**: Maintains context across agent interactions
3. **Vector store integration**: Seamless pgvector integration
4. **Prompt templates**: Standardized agent instructions
