"""
Bulk Certificate Generation Service
Handles CSV processing and bulk certificate creation
"""

import csv
import io
import os
import zipfile
from typing import List, Dict, Any
from ..models.certificates import BulkCertificateItem, BulkCertificateRequest
from .generator import generate_certificate
import logging

logger = logging.getLogger(__name__)


def process_csv_content(csv_content: str) -> List[BulkCertificateItem]:
    """
    Process CSV content and return list of certificate items
    Expected CSV format: participant_name,email (optional)
    """
    participants = []
    csv_reader = csv.DictReader(io.StringIO(csv_content))
    
    for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
        try:
            # Handle different possible column names
            name_fields = ['participant_name', 'name', 'full_name', 'participant']
            email_fields = ['email', 'email_address', 'participant_email']
            
            participant_name = None
            email = None
            
            # Find participant name
            for field in name_fields:
                if field in row and row[field].strip():
                    participant_name = row[field].strip()
                    break
            
            # Find email (optional)
            for field in email_fields:
                if field in row and row[field].strip():
                    email = row[field].strip()
                    break
            
            if not participant_name:
                logger.warning(f"Row {row_num}: Missing participant name, skipping")
                continue
                
            participants.append(BulkCertificateItem(
                participant_name=participant_name,
                email=email
            ))
            
        except Exception as e:
            logger.error(f"Error processing row {row_num}: {e}")
            continue
    
    return participants


def generate_bulk_certificates(
    event_name: str,
    date_issued: str,
    participants: List[BulkCertificateItem],
    output_dir: str = "certificates/bulk",
    certificate_type: str = "participation"
) -> Dict[str, Any]:
    """
    Generate certificates for multiple participants
    Returns summary of successful and failed generations
    
    Args:
        event_name: Name of the event
        date_issued: Date in YYYY-MM-DD format
        participants: List of participant items
        output_dir: Directory to save certificates
        certificate_type: "participation" or "completion" for template selection
    """
    os.makedirs(output_dir, exist_ok=True)
    
    successful = []
    failed = []
    
    for participant in participants:
        try:
            # Generate unique filename
            safe_name = "".join(c for c in participant.participant_name if c.isalnum() or c in (' ', '-', '_')).replace(' ', '_')
            filename = f"{safe_name}_{date_issued}_cert.png"
            output_path = os.path.join(output_dir, filename)
            
            # Generate certificate with specified type
            generate_certificate(
                participant.participant_name,
                event_name,
                date_issued,
                output_path,
                certificate_type=certificate_type
            )
            
            successful.append({
                "participant_name": participant.participant_name,
                "email": participant.email,
                "filename": filename,
                "file_path": output_path
            })
            
        except Exception as e:
            logger.error(f"Failed to generate certificate for {participant.participant_name}: {e}")
            failed.append({
                "participant_name": participant.participant_name,
                "email": participant.email,
                "error": str(e)
            })
    
    return {
        "successful_certificates": successful,
        "failed_certificates": failed,
        "success_count": len(successful),
        "failed_count": len(failed),
        "total_count": len(participants)
    }


def create_certificates_zip(certificates: List[Dict], output_dir: str) -> str:
    """
    Create a ZIP file containing all generated certificates
    Returns the path to the ZIP file
    """
    zip_filename = f"certificates_bulk_{len(certificates)}_files.zip"
    zip_path = os.path.join(output_dir, zip_filename)
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for cert in certificates:
            if os.path.exists(cert["file_path"]):
                # Add file to zip with just the filename (not full path)
                zipf.write(cert["file_path"], cert["filename"])
    
    return zip_path
