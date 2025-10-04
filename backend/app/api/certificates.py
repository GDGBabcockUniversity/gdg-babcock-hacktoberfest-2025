from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from ..models.certificates import CertificateCreate, CertificateResponse, Certificate
from ..services.generator import generate_certificate
import os

router = APIRouter()

# In-memory store for certificates (for demo; use DB for production)
certificates = {}

@router.post("/", response_model=CertificateResponse)
async def create_certificate(cert: CertificateCreate):
    # Generate server-side certificate object (with unique_id, filename, created_at, etc.)
    cert_obj = Certificate(
        participant_name=cert.participant_name,
        event_name=cert.event_name,
        date_issued=cert.date_issued
    )
    output_dir = "certificates"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, cert_obj.filename)
    try:
        generate_certificate(
            cert_obj.participant_name,
            cert_obj.event_name,
            cert_obj.date_issued,
            output_path
        )
        certificates[cert_obj.unique_id] = {
            "data": cert_obj.to_dict(),
            "file": output_path
        }
        # Return a CertificateResponse model
        return CertificateResponse(
            participant_name=cert_obj.participant_name,
            event_name=cert_obj.event_name,
            date_issued=cert_obj.date_issued,
            unique_id=cert_obj.unique_id,
            filename=cert_obj.filename,
            download_url=f"/certificates/{cert_obj.unique_id}",
            created_at=cert_obj.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Certificate generation failed: {str(e)}")

@router.get("/{unique_id}")
async def get_certificate(unique_id: str):
    cert_info = certificates.get(unique_id)
    if not cert_info:
        raise HTTPException(status_code=404, detail="Certificate not found")
    file_path = cert_info["file"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Certificate file not found")
    return FileResponse(path=file_path, filename=os.path.basename(file_path), media_type="image/png")