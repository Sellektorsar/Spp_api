import os
import pytest
from src.utils.http import APIClient

@pytest.mark.integration
class TestAuth:
    """
    Integration tests for Authentication.
    Endpoint: /api/web/v1/auth
    """

    def test_login_success(self):
        """Test successful login with valid credentials."""
        base_url = os.getenv("SPP_API_URL", "https://spp-dev.smartpack.world")
        username = os.getenv("SPP_API_USERNAME")
        password = os.getenv("SPP_API_PASSWORD")
        
        if not username or not password:
            pytest.skip("SPP_API_USERNAME or SPP_API_PASSWORD not set")

        # Create a fresh client without token to avoid using existing session token
        client = APIClient(base_url=base_url, verify_ssl=False)
        
        # Auth endpoint expects form-data, not JSON
        resp = client.request(
            "POST", 
            "/api/web/v1/auth", 
            data={"username": username, "password": password}
        )
        
        assert resp.status_code == 200, f"Login failed: {resp.text}"
        
        data = resp.json()
        # Structure check: {"data": {"access_token": "...", "token_type": "bearer"}}
        # Or sometimes just {"access_token": "..."} depending on normalization, but here we use raw response
        
        token = None
        if "data" in data and isinstance(data["data"], dict):
            token = data["data"].get("access_token")
        elif "access_token" in data:
            token = data["access_token"]
            
        assert token, f"Token not found in response: {data}"
        assert len(token) > 20, "Token seems too short"

    def test_login_invalid_credentials(self):
        """Test login with incorrect password."""
        base_url = os.getenv("SPP_API_URL", "https://spp-dev.smartpack.world")
        client = APIClient(base_url=base_url, verify_ssl=False)
        
        resp = client.request(
            "POST", 
            "/api/web/v1/auth", 
            data={"username": "invalid_user_12345", "password": "wrong_password_12345"}
        )
        
        # Expect 400 Bad Request or 401 Unauthorized
        assert resp.status_code in [400, 401, 403], f"Unexpected status code: {resp.status_code}"

    def test_login_missing_fields(self):
        """Test login with missing fields."""
        base_url = os.getenv("SPP_API_URL", "https://spp-dev.smartpack.world")
        client = APIClient(base_url=base_url, verify_ssl=False)
        
        # Missing password
        resp = client.request(
            "POST", 
            "/api/web/v1/auth", 
            data={"username": "some_user"}
        )
        
        assert resp.status_code in [400, 422], f"Unexpected status code: {resp.status_code}"
