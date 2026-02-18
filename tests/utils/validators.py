from typing import Any, Dict, List
import jsonschema
from jsonschema import validate

def validate_response(response, schema=None, expected_status=200):
    assert response.status_code == expected_status, \
        f"Expected status {expected_status}, got {response.status_code}. Response: {response.text}"
    
    if schema:
        try:
            validate(instance=response.json(), schema=schema)
        except jsonschema.exceptions.ValidationError as e:
            raise AssertionError(f"Schema validation failed: {e}")

def assert_error_response(response, expected_status, expected_error_code=None):
    assert response.status_code == expected_status, \
        f"Expected error status {expected_status}, got {response.status_code}"
    
    # Check error structure if needed
    # Example: {"code": "ERR_001", "message": "..."}
    if expected_error_code:
        json_data = response.json()
        assert json_data.get("code") == expected_error_code, \
            f"Expected error code {expected_error_code}, got {json_data.get('code')}"
