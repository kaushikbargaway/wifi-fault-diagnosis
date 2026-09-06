"""WiFi Fault Diagnosis System — FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, telemetry, diagnosis, digital_twin, recovery, explanation
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Intelligent Wi-Fi Network Fault Diagnosis and Digital Twin-Driven Recovery Recommendation System",
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS — allow the React dev server during development
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
API_PREFIX = "/api/v1"

app.include_router(health.router,       prefix=API_PREFIX, tags=["Health"])
app.include_router(telemetry.router,    prefix=API_PREFIX, tags=["Telemetry"])
app.include_router(diagnosis.router,    prefix=API_PREFIX, tags=["Diagnosis"])
app.include_router(digital_twin.router, prefix=API_PREFIX, tags=["Digital Twin"])
app.include_router(recovery.router,     prefix=API_PREFIX, tags=["Recovery"])
app.include_router(explanation.router,  prefix=API_PREFIX, tags=["Explanation"])


@app.get("/", tags=["Root"])
async def root() -> dict:
    """Root endpoint — confirms the API is running."""
    return {"message": "WiFi Fault Diagnosis API is running", "version": settings.VERSION}
