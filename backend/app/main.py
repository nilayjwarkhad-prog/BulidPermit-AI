import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.db.session import engine, Base, SessionLocal
from app.models import *  # import all models
from app.core.security import hash_password
from app.models.user import User
from app.api.v1.router import api_router
from app.ai.llm_client import llm_client
from app.core.logging import log_info

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure database schema is created
    log_info("Ensuring database tables exist...")
    Base.metadata.create_all(bind=engine)
    
    # Seed demo user for testing and local exploration
    db = SessionLocal()
    try:
        demo_email = "demo@buildpermit.ai"
        existing = db.query(User).filter(User.email == demo_email).first()
        if not existing:
            demo_user = User(
                email=demo_email,
                hashed_password=hash_password("PermitCheck2024!"),
                full_name="Alex Builder",
                role="homeowner",
                is_active=True
            )
            db.add(demo_user)
            db.commit()
            log_info(f"Seeded demo account: {demo_email}")
    finally:
        db.close()

    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="BuildPermit AI — Pre-submission assistant for residential building permit applications.",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API v1 routes
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "connected"
    }

@app.get("/health/ai")
async def ai_health_check():
    return await llm_client.check_health()
