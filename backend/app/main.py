from fastapi import FastAPI
from app.api import certificates

app = FastAPI(title="Hacktoberfest Certificate Generator")

# Routes
app.include_router(certificates.router, prefix="/certificates", tags=["certificates"])

@app.get("/")
def root():
    return {"message": "Welcome to Hacktoberfest Certificate Generator API 🚀. Start contributing today!!!!!"}
