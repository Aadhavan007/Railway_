from fastapi import FastAPI

from app.database.connection import engine
from app.database.models import Base


# Create all database tables
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="RailSync AI",
    description="AI-Powered Automatic Block Planning for Indian Railways",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "message": "RailSync AI Backend is running",
        "status": "ok",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
    }