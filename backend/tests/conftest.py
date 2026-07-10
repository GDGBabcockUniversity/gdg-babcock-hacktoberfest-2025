"""
Shared pytest fixtures. Sets a fixed CERT_SERVICE_TOKEN for the whole test
session so tests can authenticate against the now-secured POST /certificates/
endpoint without depending on the real production secret.
"""

import os

os.environ.setdefault("CERT_SERVICE_TOKEN", "test-service-token")

TEST_SERVICE_TOKEN = os.environ["CERT_SERVICE_TOKEN"]
AUTH_HEADERS = {"Authorization": f"Bearer {TEST_SERVICE_TOKEN}"}
