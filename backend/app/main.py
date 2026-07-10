import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Relative imports within the same package
from .api.certificates import router as certificates_router
from .database import Base, engine
from .models import certificates as certificate_models

app = FastAPI(title="Hacktoberfest Certificate Generator")

# Also create tables at import time (not just on the ASGI "startup" event):
# httpx.AsyncClient(transport=ASGITransport(app=app)), used by the async
# test suite, does not send lifespan events, so relying on the startup
# handler alone left the sqlite tables missing under that test client.
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def create_db_tables():
    Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(certificates_router, prefix="/certificates", tags=["certificates"])

# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to Hacktoberfest Certificate Generator API 🚀"}

# CORS middleware
_default_origins = "https://gdgbabcock.com,https://auth.gdgbabcock.com,http://localhost:3000"
allowed_origins = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", _default_origins).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
