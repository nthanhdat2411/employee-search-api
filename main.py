import uvicorn
from fastapi import FastAPI
from app.api import app
from app.database import create_tables
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting Employee Search Directory API...")
    try:
        # Create database tables
        create_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    logger.info("Shutting down Employee Search Directory API...")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 