from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Relative imports within the same package
from .api.certificates import router as certificates_router
from .database import Base, engine
from .models import certificates as certificate_models

app = FastAPI(title="Hacktoberfest Certificate Generator")

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
