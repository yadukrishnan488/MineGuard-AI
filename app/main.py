import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.db.session import init_db
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure upload directory exists and database tables are initialized
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    init_db()
    yield
    # Shutdown logic if needed


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "AI-Based Smart Governance and Compliance Monitoring System for Coal Mines.\n\n"
        "Features:\n"
        "- Role-Based Access Control (RBAC) across 6 hierarchical roles.\n"
        "- 22 normalized database entities with PostGIS geospatial mapping.\n"
        "- Resilient offline field inspection synchronization with idempotency keys.\n"
        "- Worker grievance redressal with confidential reporting.\n"
        "- Explainable multi-factor AI risk assessment engine.\n"
        "- Tesseract OCR document text extraction pipeline.\n"
        "- Cryptographic SHA-256 immutable audit trail verification."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Secure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static folder for interactive KhanRakshak web UI
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", tags=["System Information"])
def root():
    """System welcome and operational metadata."""
    return {
        "system": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
        "documentation": "/docs",
        "web_portal": "/portal",
        "api_v1": settings.API_V1_STR,
    }


@app.get("/portal", response_class=HTMLResponse, tags=["Web Portal"])
def web_portal():
    """Interactive KhanRakshak Web Portal connected to live backend."""
    portal_file = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(portal_file):
        with open(portal_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Portal not found</h1>", status_code=404)



@app.get("/health", tags=["Health & Status"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health & Status"])
def health_check():
    """System health check and database connectivity verification."""
    from app.db.session import SessionLocal
    from sqlalchemy import text

    db_status = "healthy"
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return {
        "status": "healthy" if "unhealthy" not in db_status else "degraded",
        "database": db_status,
        "environment": settings.ENVIRONMENT,
    }


# Mount versioned API routes
app.include_router(api_router, prefix=settings.API_V1_STR)
