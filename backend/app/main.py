from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import engine
from app.database.models import Base

from app.api import (
    approvals,
    conflicts,
    dashboard,
    data,
    emergency,
    optimization,
    priorities,
    schedules,
    tasks,
)


# ============================================================
# DATABASE
# ============================================================

Base.metadata.create_all(
    bind=engine
)


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="RailSync AI",
    description=(
        "AI-Powered Automatic Block Planning "
        "for Indian Railways"
    ),
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ROUTERS
# ============================================================

app.include_router(
    dashboard.router
)

app.include_router(
    optimization.router
)

app.include_router(
    schedules.router
)

app.include_router(
    priorities.router
)

app.include_router(
    tasks.router
)

app.include_router(
    conflicts.router
)

app.include_router(
    data.router
)

app.include_router(
    approvals.router
)

app.include_router(
    emergency.router
)


# ============================================================
# ROOT
# ============================================================

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