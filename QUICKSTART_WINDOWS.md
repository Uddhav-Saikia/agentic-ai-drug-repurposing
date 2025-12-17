# Quick Start Guide - Windows

## Step-by-Step Commands

### 1. Navigate to Project
```cmd
cd "d:\Odin Project\repo\agentic ai drug repurposing"
```

### 2. Set Up Backend Environment
```cmd
cd backend
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment
```cmd
cd ..
copy .env.example .env
notepad .env
```
**Required:** Add your OpenAI API key in the .env file:
```
OPENAI_API_KEY=sk-your-actual-key-here
```

### 4. Start Database Services
```cmd
docker-compose up -d postgres redis
```

### 5. Verify Containers Running
```cmd
docker ps
```
You should see:
- `drug_repurposing_db` (PostgreSQL)
- `drug_repurposing_redis` (Redis)

### 6. Check Database Tables
```cmd
docker exec -it drug_repurposing_db psql -U postgres -d drug_repurposing -c "\dt"
```
Expected tables:
- queries
- tasks
- reports
- drug_candidates
- embeddings

### 7. Start Backend Server
```cmd
cd backend
venv\Scripts\activate
python main.py
```

### 8. Test the API
Open your browser:
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/v1/health
- Root: http://localhost:8000

### 9. Test with curl (PowerShell)
```powershell
# Basic health
Invoke-WebRequest -Uri http://localhost:8000/v1/health | Select-Object -Expand Content

# Database health
Invoke-WebRequest -Uri http://localhost:8000/v1/health/db | Select-Object -Expand Content

# Full health check
Invoke-WebRequest -Uri http://localhost:8000/v1/health/full | Select-Object -Expand Content
```

## Common Commands

### Stop Services
```cmd
docker-compose down
```

### Stop Services + Delete Data
```cmd
docker-compose down -v
```

### View Logs
```cmd
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Restart Services
```cmd
docker-compose restart postgres
docker-compose restart redis
```

### Access PostgreSQL Shell
```cmd
docker exec -it drug_repurposing_db psql -U postgres -d drug_repurposing
```

### Access Redis CLI
```cmd
docker exec -it drug_repurposing_redis redis-cli
```

## Troubleshooting

### Port Already in Use (8000)
```cmd
# Find process using port
netstat -ano | findstr :8000

# Kill process (replace PID with actual process ID)
taskkill /PID <PID> /F
```

### Docker Issues
```cmd
# Restart Docker Desktop
# Then rebuild containers
docker-compose up -d --build
```

### Virtual Environment Issues
```cmd
# Delete and recreate
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Database Connection Issues
```cmd
# Check if database is accepting connections
docker exec -it drug_repurposing_db pg_isready -U postgres

# Restart database
docker-compose restart postgres
```

## File Locations

| Item | Path |
|------|------|
| Backend code | `backend\` |
| API routes | `backend\api\routes\` |
| Configuration | `backend\core\config.py` |
| Environment vars | `.env` |
| Database init | `database\init.sql` |
| Docker configs | `docker-compose.yml` |
| Logs | `backend\logs\app.log` |

## Next Steps

Once everything is running:
1. ✅ Verify health checks pass
2. ✅ Check API documentation loads
3. ✅ Confirm database tables exist
4. 🚀 Ready for Phase 2!

## Need Help?

Check these files:
- [README.md](README.md) - Project overview
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup
- [PHASE1_COMPLETE.md](PHASE1_COMPLETE.md) - Phase 1 summary
