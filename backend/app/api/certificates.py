from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import FileResponse
from ..models.certificates import (
    CertificateCreate, 
    CertificateResponse, 
    Certificate,
    BulkCertificateRequest,
    BulkCertificateResponse,
    CertificateORM
)
from ..services.generator import generate_certificate
from ..services.bulk_generator import (
    process_csv_content, 
    generate_bulk_certificates, 
    create_certificates_zip
)
import os
import logging
from sqlalchemy.orm import Session
from ..database import get_db

# Logger setup
logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory store for demo; use DB in production
# certificates = {}


@router.post(
    "/",
    response_model=CertificateResponse,
    responses={
        200: {"description": "Certificate created successfully"},
        400: {"description": "Invalid input (empty participant or event name)"},
        422: {"description": "Request validation error"},
        500: {"description": "Internal server error during certificate generation"},
    },
)
async def create_certificate(
    cert: CertificateCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new digital certificate for a participant.

    This endpoint generates a certificate image file based on the participant’s details
    and stores its record temporarily in memory (use a persistent DB in production).

    ---
    **Request Body Example**
    ```json
    {
        "participant_name": "Jane Doe",
        "event_name": "AI Hackathon 2025",
        "date_issued": "2025-10-21"
    }
    ```

    **Successful Response (200)**
    ```json
    {
        "participant_name": "Jane Doe",
        "event_name": "AI Hackathon 2025",
        "date_issued": "2025-10-21",
        "unique_id": "c8b5a120-6d48-4d13-9af5-2c7ad70fef14",
        "filename": "Jane_Doe_AI_Hackathon_2025.png",
        "download_url": "/certificates/c8b5a120-6d48-4d13-9af5-2c7ad70fef14",
        "created_at": "2025-10-21T15:30:12.004Z"
    }
    ```

    **Error Codes**
    - `400`: Invalid input (empty participant or event name)
    - `422`: Request validation error (invalid format)
    - `500`: Internal server error (template missing, permission denied, etc.)

    **Notes**
    - Certificate images are saved in the `certificates/` directory.
    - The returned `unique_id` can be used to download the generated certificate later.
    """
    try:
        # Input validation
        if not cert.participant_name.strip() or not cert.event_name.strip():
            raise HTTPException(
                status_code=400,
                detail="Participant name and event name cannot be empty."
            )

        # Create certificate object
        cert_obj = Certificate(
            participant_name=cert.participant_name,
            event_name=cert.event_name,
            date_issued=cert.date_issued
        )

        output_dir = "certificates"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, cert_obj.filename)

        # Attempt generation
        try:
            generate_certificate(
                cert_obj.participant_name,
                cert_obj.event_name,
                cert_obj.date_issued,
                output_path
            )
        except FileNotFoundError as e:
            logger.error(f"Template file missing: {e}")
            raise HTTPException(status_code=500, detail="Certificate template not found on server.")
        except PermissionError as e:
            logger.error(f"Permission error writing file: {e}")
            raise HTTPException(status_code=500, detail="Server permission error while saving certificate.")
        except Exception as e:
            logger.error(f"Unexpected error during certificate generation: {e}")
            raise HTTPException(status_code=500, detail="Unexpected error during certificate generation.")

        # Save to database
        db_cert = CertificateORM(
            unique_id=cert_obj.unique_id,
            participant_name=cert_obj.participant_name,
            event_name=cert_obj.event_name,
            date_issued=cert_obj.date_issued,
            filename=cert_obj.filename,
            created_at=cert_obj.created_at
        )

        db.add(db_cert)
        db.commit()
        db.refresh(db_cert)

        # Successful response
        return CertificateResponse(
            participant_name=cert_obj.participant_name,
            event_name=cert_obj.event_name,
            date_issued=cert_obj.date_issued,
            unique_id=cert_obj.unique_id,
            filename=cert_obj.filename,
            download_url=f"/certificates/{cert_obj.unique_id}",
            created_at=cert_obj.created_at
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled error in POST /certificates: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while creating certificate.")


@router.get(
    "/{unique_id}",
    responses={
        200: {"description": "Returns the certificate image file"},
        404: {"description": "Certificate record or file not found"},
        500: {"description": "Internal server error while fetching certificate"},
    },
)
async def get_certificate(
    unique_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a generated certificate by its unique ID.

    This endpoint returns the generated certificate image file if it exists on the server.
    The certificate must first be created using the `POST /certificates` endpoint.

    ---
    **Path Parameter**
    - `unique_id` (string): Unique identifier of the certificate.

    **Example Request**
    ```
    GET /certificates/c8b5a120-6d48-4d13-9af5-2c7ad70fef14
    ```

    **Example Response (File Download)**
    - Content-Type: `image/png`
    - File: `Jane_Doe_AI_Hackathon_2025.png`

    **Error Codes**
    - `404`: Certificate record not found or file missing.
    - `500`: Internal server error while retrieving certificate.

    **Notes**
    - This endpoint returns a `FileResponse` (image), not JSON.
    """
    try:
        db_cert = db.query(CertificateORM).filter(CertificateORM.unique_id == unique_id).first()
        if not db_cert:
            raise HTTPException(status_code=404, detail="Certificate record not found.")

        file_path = os.path.join("certificates", db_cert.filename)
        if not os.path.exists(file_path):
            logger.warning(f"File not found for certificate {unique_id}: {file_path}")
            raise HTTPException(status_code=404, detail="Certificate file missing on server.")

        return FileResponse(
            path=file_path,
            filename=db_cert.filename,
            media_type="image/png"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unhandled error in GET /certificates/{unique_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while fetching certificate.")


@router.post("/bulk", response_model=BulkCertificateResponse)
async def create_bulk_certificates(request: BulkCertificateRequest):
    """
    Generate certificates for multiple participants
    """
    try:
        output_dir = "certificates/bulk"
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate bulk certificates
        result = generate_bulk_certificates(
            event_name=request.event_name,
            date_issued=request.date_issued,
            participants=request.participants,
            output_dir=output_dir
        )
        
        download_url = None
        if result["successful_certificates"]:
            # Create ZIP file for download
            zip_path = create_certificates_zip(
                result["successful_certificates"], 
                output_dir
            )
            download_url = f"/certificates/bulk/download/{os.path.basename(zip_path)}"
        
        return BulkCertificateResponse(
            success_count=result["success_count"],
            failed_count=result["failed_count"],
            total_count=result["total_count"],
            successful_certificates=result["successful_certificates"],
            failed_certificates=result["failed_certificates"],
            download_url=download_url
        )
        
    except Exception as e:
        logger.error(f"Error in bulk certificate generation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate bulk certificates: {str(e)}")


@router.post("/bulk/csv", response_model=BulkCertificateResponse)
async def create_bulk_certificates_from_csv(
    event_name: str,
    date_issued: str,
    csv_file: UploadFile = File(...)
):
    """
    Generate certificates from CSV file upload
    CSV should have columns: participant_name, email (optional)
    """
    try:
        # Validate file type
        if not csv_file.filename.endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV file")
        
        # Read CSV content
        csv_content = await csv_file.read()
        csv_text = csv_content.decode('utf-8')
        
        # Process CSV and extract participants
        participants = process_csv_content(csv_text)
        
        if not participants:
            raise HTTPException(
                status_code=400, 
                detail="No valid participants found in CSV file"
            )
        
        # Create bulk request
        bulk_request = BulkCertificateRequest(
            event_name=event_name,
            date_issued=date_issued,
            participants=participants
        )
        
        # Generate certificates
        return await create_bulk_certificates(bulk_request)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing CSV file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process CSV file: {str(e)}")


@router.get("/bulk/download/{filename}")
async def download_bulk_certificates(filename: str):
    """
    Download ZIP file containing bulk certificates
    """
    try:
        file_path = os.path.join("certificates/bulk", filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Bulk certificate file not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/zip"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading bulk certificates: {e}")
        raise HTTPException(status_code=500, detail="Failed to download bulk certificates")