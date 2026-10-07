import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.app.core.config import settings
from backend.app.core.database import init_db, get_db
from backend.app.models.schemas import HealthCheckResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize DB tables
    init_db()
    yield
    # Shutdown

app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered Discovery Engine analyzing Google Photos retrieval failures and opportunity spaces.",
    version="1.0.0",
    lifespan=lifespan
)

# Handle HTTP HEAD requests for uptime monitors (e.g. UptimeRobot)
@app.middleware("http")
async def handle_head_requests(request: Request, call_next):
    """Gracefully handle HTTP HEAD requests sent by monitoring services like UptimeRobot."""
    if request.method == "HEAD":
        request.scope["method"] = "GET"
        response = await call_next(request)
        return Response(
            status_code=response.status_code,
            headers=dict(response.headers)
        )
    return await call_next(request)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from backend.app.api.v1.endpoints import router as api_v1_router
app.include_router(api_v1_router)

@app.api_route("/", methods=["GET", "HEAD"], tags=["Root"])
def root():
    return {
        "app": settings.APP_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.api_route("/health", methods=["GET", "HEAD"], response_model=HealthCheckResponse, tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return HealthCheckResponse(
        status="healthy" if db_ok else "degraded",
        app_name=settings.APP_NAME,
        environment=settings.APP_ENV,
        groq_api_configured=bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY.startswith("gsk_")),
        database_connected=db_ok
    )

if __name__ == "__main__":
    import uvicorn
    raw_port = os.environ.get("PORT", "8080")
    try:
        port = int(raw_port)
    except (ValueError, TypeError):
        port = 8080
    is_dev = settings.APP_ENV == "development"
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=is_dev)
