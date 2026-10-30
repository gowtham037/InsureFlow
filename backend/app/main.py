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
