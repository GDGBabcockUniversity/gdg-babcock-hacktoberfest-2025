# backend/main.py
import time
from typing import Any, Dict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

# Relative imports within the same package
from .api.certificates import router as certificates_router
from .database import Base, engine
from .models import certificates as certificate_models

APP_NAME = "Hacktoberfest Certificate Generator"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "API to generate and manage event certificates."

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
)

# Store startup time and create DB tables on startup
@app.on_event("startup")
def startup_event():
    app.state.start_time = time.time()
    Base.metadata.create_all(bind=engine)


# Custom 404 handler
@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(
            status_code=404, content={"error": "not_found","message": "The requested resource was not found.","status": 404, "path": request.url.path}
        )
    return JSONResponse(status_code=exc.status_code,content={"detail": exc.detail, "status": exc.status_code})


# Include routers
app.include_router(certificates_router, prefix="/certificates", tags=["certificates"])


# Root endpoint — returns service info & uptime
@app.get("/", summary="Service info")
def root() -> Dict[str, Any]:
    start = getattr(app.state, "start_time", None)
    uptime = int(time.time() - start) if start else None
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "description": APP_DESCRIPTION,
        "uptime_seconds": uptime,
        "docs": "/docs",
        "openapi": "/openapi.json",
    }


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change this to your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
