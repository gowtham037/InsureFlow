from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings
from backend.app.database import init_db
from backend.app.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Enterprise Insurance Underwriting, Policy Evaluation & Anomaly Detection Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()
    # Auto-seed full dataset on fresh database startup if enabled
    import os
    if os.getenv("AUTO_SEED_ON_STARTUP", "true").lower() in ("true", "1", "yes"):
        from backend.app.database import SessionLocal
        from backend.app.models.applicant import Applicant
        from backend.app.data_generator.generator import generate_dataset
        db = SessionLocal()
        try:
            if db.query(Applicant).count() == 0:
                import logging
                logger = logging.getLogger(__name__)
                logger.info("Fresh database detected (0 applicants). Auto-generating full production dataset...")
                generate_dataset(mode="full", seed=settings.DATA_GEN_SEED, db=db)
                logger.info("Auto-seeding full production dataset completed successfully.")
        except Exception as e:
            import logging
            db.rollback()
            logging.getLogger(__name__).error(f"Auto-seed failed on startup: {e}", exc_info=True)
        finally:
            db.close()


@app.get("/", tags=["Health"])
def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "OPERATIONAL",
        "version": "1.0.0",
        "documentation": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "HEALTHY"}


# Include all modular routers under /api
app.include_router(api_router, prefix=settings.API_V1_STR)
