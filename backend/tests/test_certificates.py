import pytest
import httpx
from httpx import ASGITransport
import sys
import os

# add the full project path to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)  # backend/
parent_dir = os.path.dirname(project_root)   # gdg-babcock-hacktoberfest-2025/

# add both backend/ and parent directory
sys.path.insert(0, project_root)  # backend/
sys.path.insert(0, parent_dir)    # gdg-babcock-hacktoberfest-2025/

from app.main import app

class TestCertificateEndpoints:
    """
    Automated tests for certificate endpoints.
    Uses httpx.AsyncClient as requested in requirements.
    """
    
    @pytest.mark.asyncio
    async def test_post_certificate_success(self):
        """
        Test POST /certificates/ - successful certificate creation
        """
        async with httpx.AsyncClient(
            transport=ASGITransport(app=app), 
            base_url="http://test"
        ) as client:
            # valid data for certificate creation
            data = {
                "participant_name": "Lionel Messi",
                "event_name": "GDG Babcock Hacktoberfest 2025", 
                "date_issued": "2025-10-08"
            }
            
            response = await client.post("/certificates/", json=data)
            
            # verify successful response
            assert response.status_code == 200
            response_data = response.json()
            
            # verify response structure
            assert "participant_name" in response_data
            assert "event_name" in response_data
            assert "unique_id" in response_data
            assert "filename" in response_data
            assert "download_url" in response_data
            assert "created_at" in response_data
            
            # verify data matches
            assert response_data["participant_name"] == "Lionel Messi"
            assert response_data["event_name"] == "GDG Babcock Hacktoberfest 2025"
            
            # verify certificate file was actually created
            certificates_dir = os.path.join(project_root, "certificates")
            expected_file_path = os.path.join(certificates_dir, response_data["filename"])
            
            # check if file exists
            assert os.path.exists(expected_file_path), f"Certificate file not found: {expected_file_path}"
            
            # check if file is not empty
            assert os.path.getsize(expected_file_path) > 0, "Certificate file is empty"
            
            # verify its a PNG file by checking signature
            with open(expected_file_path, 'rb') as f:
                file_header = f.read(8)
                # PNG file signature
                assert file_header == b'\x89PNG\r\n\x1a\n', "File is not a valid PNG"
    
    @pytest.mark.asyncio
    async def test_post_certificate_validation_error(self):
        """
        Test POST /certificates/ - validation failure with invalid data
        """
        async with httpx.AsyncClient(
            transport=ASGITransport(app=app), 
            base_url="http://test"
        ) as client:
            # invalid data - name too short, event too short, wrong date format
            data = {
                "participant_name": "J",  # too short (min_length=2)
                "event_name": "AB",  # too short (min_length=3)  
                "date_issued": "2025/10/15"  # wrong format (should be YYYY-MM-DD)
            }
            
            response = await client.post("/certificates/", json=data)
            
            # should return validation error
            assert response.status_code == 422
            error_data = response.json()
            assert "detail" in error_data
    
    @pytest.mark.asyncio
    async def test_post_certificate_missing_required_fields(self):
        """
        Test POST /certificates/ - missing required fields
        """
        async with httpx.AsyncClient(
            transport=ASGITransport(app=app), 
            base_url="http://test"
        ) as client:
            # Incomplete data - missing required fields
            data = {
                "participant_name": "Lionel Messi"
                # missing event_name and date_issued (required fields)
            }
            
            response = await client.post("/certificates/", json=data)
            
            # should return validation error
            assert response.status_code == 422
            error_data = response.json()
            assert "detail" in error_data

# basic backup tests
def test_basic_setup():
    """Basic test to verify pytest is configured correctly"""
    assert 1 + 1 == 2

@pytest.mark.asyncio
async def test_async_setup():
    """Basic async test to verify pytest-asyncio works"""
    result = await simple_async_function()
    assert result == "hello"

async def simple_async_function():
    return "hello"