"""
Shared FastAPI dependencies for the certificates API.
"""

import os
import secrets

from fastapi import Header, HTTPException


async def require_service_token(authorization: str = Header(default=None)):
    """
    Requires a `Authorization: Bearer <token>` header matching CERT_SERVICE_TOKEN.

    Fails closed: if CERT_SERVICE_TOKEN itself is not configured, every call
    is rejected (503) rather than silently accepting all requests.
    """
    expected_token = os.environ.get("CERT_SERVICE_TOKEN")
    if not expected_token:
        raise HTTPException(
            status_code=503,
            detail="Certificate service is not configured with a service token.",
        )

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or malformed Authorization header.")

    provided_token = authorization[len("Bearer "):]
    if not secrets.compare_digest(provided_token, expected_token):
        raise HTTPException(status_code=401, detail="Invalid service token.")
