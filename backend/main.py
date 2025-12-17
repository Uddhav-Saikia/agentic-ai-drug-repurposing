"""
Main entry point for the Drug Repurposing FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from core.config import settings
from api.routes import queries, agents, reports, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    # Startup
    logger.info("Starting Drug Repurposing API...")
    logger.info(f"Environment: {settings.APP_ENV}")
    yield
    # Shutdown
    logger.info("Shutting down Drug Repurposing API...")


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Agentic AI system for drug repurposing research",
    version=settings.API_VERSION,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix=f"/{settings.API_VERSION}", tags=["Health"])
app.include_router(queries.router, prefix=f"/{settings.API_VERSION}/queries", tags=["Queries"])
app.include_router(agents.router, prefix=f"/{settings.API_VERSION}/agents", tags=["Agents"])
app.include_router(reports.router, prefix=f"/{settings.API_VERSION}/reports", tags=["Reports"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Drug Repurposing Agentic AI System",
        "version": settings.API_VERSION,
        "docs": f"/{settings.API_VERSION}/docs",
        "status": "operational"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=settings.DEBUG
    )
