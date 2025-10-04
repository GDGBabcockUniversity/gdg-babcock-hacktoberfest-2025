from fastapi import FastAPI

# Relative imports within the same package
from .api.certificates import router as certificates_router

app = FastAPI(title="Hacktoberfest Certificate Generator")

# Include routers
app.include_router(certificates_router, prefix="/certificates", tags=["certificates"])

# Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to Hacktoberfest Certificate Generator API 🚀"}
