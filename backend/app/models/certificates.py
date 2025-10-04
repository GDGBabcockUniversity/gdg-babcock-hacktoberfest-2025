"""
Certificate Models
Pydantic schemas and ORM models for certificate generation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from uuid import uuid4
import re

# ============================================================================
# PYDANTIC SCHEMAS (for API request/response validation)
# ============================================================================

class CertificateBase(BaseModel):
    """Base certificate schema with common fields"""
    participant_name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        description="Full name of the participant"
    )
    event_name: str = Field(
        ..., 
        min_length=3, 
        max_length=200,
        description="Name of the event"
    )
    date_issued: str = Field(
        ...,
        description="Date when certificate was issued (YYYY-MM-DD format)"
    )
    
    @validator('participant_name')
    def validate_participant_name(cls, v):
        """Validate participant name"""
        if not v.strip():
            raise ValueError('Participant name cannot be empty')
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r"^[a-zA-Z\s\-'\.]+$", v):
            raise ValueError('Participant name contains invalid characters')
        return v.strip()
    
    @validator('event_name')
    def validate_event_name(cls, v):
        """Validate event name"""
        if not v.strip():
            raise ValueError('Event name cannot be empty')
        return v.strip()
    
    @validator('date_issued')
    def validate_date_format(cls, v):
        """Validate date format"""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format')


class CertificateCreate(CertificateBase):
    """Schema for creating a new certificate"""
    pass


class CertificateResponse(CertificateBase):
    """Schema for certificate API response"""
    unique_id: str = Field(
        ...,
        description="Unique identifier for the certificate"
    )
    filename: str = Field(
        ...,
        description="Generated filename for the certificate"
    )
    download_url: str = Field(
        ...,
        description="URL to download the certificate"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp when certificate was generated"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "participant_name": "John Doe",
                "event_name": "GDG Babcock Hacktoberfest 2025",
                "date_issued": "2025-10-04",
                "unique_id": "cert_1a2b3c4d5e6f",
                "filename": "John_Doe_GDG_Babcock_Hacktoberfest_2025_2025-10-04.png",
                "download_url": "/download-certificate/John_Doe_GDG_Babcock_Hacktoberfest_2025_2025-10-04.png",
                "created_at": "2025-10-04T10:30:00"
            }
        }


class BulkCertificateRequest(BaseModel):
    """Schema for bulk certificate generation"""
    participants: list[CertificateCreate] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of participants (max 100 per request)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "participants": [
                    {
                        "participant_name": "Alice Johnson",
                        "event_name": "GDG Babcock Hacktoberfest 2025",
                        "date_issued": "2025-10-04"
                    },
                    {
                        "participant_name": "Bob Smith",
                        "event_name": "GDG Babcock Hacktoberfest 2025",
                        "date_issued": "2025-10-04"
                    }
                ]
            }
        }


class BulkCertificateResponse(BaseModel):
    """Schema for bulk certificate generation response"""
    message: str
    total_requested: int
    successful: int
    failed: int
    results: list[CertificateResponse]
    errors: Optional[list[dict]] = None


class CertificateListResponse(BaseModel):
    """Schema for listing certificates"""
    count: int
    certificates: list[str]


class CertificateDeleteResponse(BaseModel):
    """Schema for certificate deletion response"""
    message: str
    filename: str
    unique_id: Optional[str] = None


# ============================================================================
# CERTIFICATE DATA CLASS (for internal use)
# ============================================================================

class Certificate:
    """
    Certificate data class for internal processing
    Includes unique ID generation and filename creation
    """
    
    def __init__(
        self,
        participant_name: str,
        event_name: str,
        date_issued: str,
        unique_id: Optional[str] = None
    ):
        self.participant_name = participant_name
        self.event_name = event_name
        self.date_issued = date_issued
        self.unique_id = unique_id or self._generate_unique_id()
        self.filename = self._generate_filename()
        self.created_at = datetime.now()
    
    def _generate_unique_id(self) -> str:
        """Generate a unique certificate ID"""
        # Format: cert_<short-uuid>
        short_uuid = str(uuid4()).replace('-', '')[:12]
        return f"cert_{short_uuid}"
    
    def _generate_filename(self) -> str:
        """Generate a safe filename for the certificate"""
        # Sanitize names for filename
        safe_name = self.participant_name.replace(" ", "_").replace("/", "-").replace("\\", "-")
        safe_event = self.event_name.replace(" ", "_").replace("/", "-").replace("\\", "-")
        
        # Create filename: Name_Event_Date_UniqueID.png
        filename = f"{safe_name}_{safe_event}_{self.date_issued}_{self.unique_id}.png"
        
        # Remove any remaining special characters
        filename = re.sub(r'[^\w\-_\.]', '', filename)
        
        return filename
    
    def to_dict(self) -> dict:
        """Convert certificate to dictionary"""
        return {
            "participant_name": self.participant_name,
            "event_name": self.event_name,
            "date_issued": self.date_issued,
            "unique_id": self.unique_id,
            "filename": self.filename,
            "created_at": self.created_at.isoformat()
        }
    
    def __repr__(self) -> str:
        return f"Certificate(id={self.unique_id}, participant={self.participant_name})"


# ============================================================================
# ORM MODEL (stubbed for future database integration)
# ============================================================================


# ORM Model stub using SQLAlchemy (for future database implementation)
# Uncomment and configure when database support is added

# from sqlalchemy import Column, String, DateTime
# from sqlalchemy.ext.declarative import declarative_base

# Base = declarative_base()

# class CertificateORM(Base):
#     '''SQLAlchemy ORM model for Certificate'''
    
#     __tablename__ = 'certificates'
    
#     unique_id = Column(String(50), primary_key=True, index=True)
#     participant_name = Column(String(100), nullable=False, index=True)
#     event_name = Column(String(200), nullable=False, index=True)
#     date_issued = Column(String(10), nullable=False)
#     filename = Column(String(255), nullable=False, unique=True)
#     file_path = Column(String(500), nullable=True)
#     created_at = Column(DateTime, default=datetime.now)
#     updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
#     def __repr__(self):
#         return f"<Certificate(id={self.unique_id}, participant={self.participant_name})>"
    
#     def to_dict(self):
#         '''Convert ORM model to dictionary'''
#         return {
#             'unique_id': self.unique_id,
#             'participant_name': self.participant_name,
#             'event_name': self.event_name,
#             'date_issued': self.date_issued,
#             'filename': self.filename,
#             'file_path': self.file_path,
#             'created_at': self.created_at.isoformat() if self.created_at else None,
#             'updated_at': self.updated_at.isoformat() if self.updated_at else None
#         }

# # Database configuration (to be implemented)
# # from sqlalchemy import create_engine
# # from sqlalchemy.orm import sessionmaker

# # DATABASE_URL = "sqlite:///./certificates.db"  # or PostgreSQL, MySQL, etc.
# # engine = create_engine(DATABASE_URL)
# # SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# # Create tables
# # Base.metadata.create_all(bind=engine)
