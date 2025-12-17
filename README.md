# Agentic AI for Drug Repurposing

## Overview
An autonomous agentic system that synthesizes fragmented biomedical data to identify drug repurposing opportunities, reducing research time from months to days.

## Architecture

### Core Components
- **Master Agent**: Orchestrates query-to-report pipeline
- **Worker Agents**:
  - Market Intelligence Agent (IQVIA/Market databases)
  - Patent Landscape Agent (USPTO data analysis)
  - Clinical Intelligence Agent (ClinicalTrials.gov)
  - Web Intelligence Agent (Public web data/publications)

### Tech Stack
- **Backend**: Python with FastAPI
- **AI Framework**: LangChain + CrewAI
- **Frontend**: Next.js (React)
- **Database**: PostgreSQL + Vector DB (pgvector)
- **Infrastructure**: Docker, Docker Compose

## Project Structure
```
├── backend/                  # Python FastAPI microservices
│   ├── agents/              # AI agent implementations
│   ├── api/                 # FastAPI endpoints
│   ├── core/                # Core business logic
│   ├── models/              # Database models
│   ├── services/            # Service layer
│   └── utils/               # Utility functions
├── frontend/                # Next.js application
├── database/                # Database migrations and seeds
├── docker/                  # Docker configurations
├── tests/                   # Test suites
└── docs/                    # Documentation
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- PostgreSQL 15+

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd agentic-ai-drug-repurposing
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Start Services with Docker**
```bash
docker-compose up -d
```

5. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Development

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Environment Variables
Copy `.env.example` to `.env` and configure:
- API keys for external services
- Database credentials
- JWT secrets

## License
MIT
