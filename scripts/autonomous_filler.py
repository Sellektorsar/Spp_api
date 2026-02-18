import os
import re
import json
from pathlib import Path
from tests.utils.roadmap_parser import parse_roadmap
from src.utils.openapi_helper import OpenAPIHelper

def get_group_and_name(method):
    base_path = method["base_path"]
    endpoint = method["endpoint"]
    
    if "{path}" in endpoint:
        endpoint = endpoint.replace("{path}", "wildcard")
    
    if "network_proxy" in base_path:
        group = "network_proxy"
    elif base_path.startswith("/api/web/v1"):
        parts = endpoint.split("/")
        group = parts[0] if parts[0] else "root"
    else:
        group = "root"
        
    method_name = endpoint.split("/")[-1] or "root"
    if not method_name or method_name == "wildcard":
        method_name = f"{method['http_method'].lower()}_root"
    
    safe_name = re.sub(r"[^a-zA-Z0-9_]+", "_", method_name)
    safe_name = safe_name.strip("_")
    
    return group, safe_name

def fill_source(method, group, safe_name, helper: OpenAPIHelper):
    src_path = Path(f"src/api/{group}/{safe_name}.py")
    
    # Skip if manual content detected (get_roll)
    if src_path.exists():
        content = src_path.read_text(encoding="utf-8")
        # Stricter check for get_roll manual override
        if "def get_roll(" in content and str(src_path).endswith(os.sep + "get_roll.py"):
             return "skipped_manual"
        # Also skip get_roll_by_code/documents if they are manual (they were manually fixed by me)
        if safe_name in ["get_roll_by_code", "get_roll_from_documents"] and "warehouse" in str(src_path):
             return "skipped_manual"
        # change_app_conf was also manual
        if safe_name == "change_app_conf":
             return "skipped_manual"

    full_path = f"{method['base_path']}/{method['endpoint']}".replace("<server>", "")
    
    op = helper.get_operation(full_path, method['http_method'])
    if not op:
        return "skipped_no_openapi"

    docstring = helper.generate_docstring(op, full_path, method['http_method'])
    docstring_indented = "\n".join([f"    {line}" if line else "" for line in docstring.splitlines()])
    
    code = f"""from src.utils.http import APIClient
import requests

def {safe_name}(client: APIClient, **kwargs) -> requests.Response:
{docstring_indented}
    endpoint = "{full_path}"
    return client.request("{method['http_method'].upper()}", endpoint, **kwargs)
"""
    
    src_path.parent.mkdir(parents=True, exist_ok=True)
    src_path.write_text(code, encoding="utf-8")
    return "updated"

def fill_test(method, group, safe_name, helper: OpenAPIHelper):
    test_path = Path(f"tests/unit/api/{group}/test_{safe_name}.py")
    
    if test_path.exists():
        content = test_path.read_text(encoding="utf-8")
        # Stricter check for manual overrides
        if "class TestGetRoll:" in content or "class TestGetRoll(" in content:
             return "skipped_manual"
        if safe_name in ["get_roll_by_code", "get_roll_from_documents"] and "warehouse" in str(test_path):
             return "skipped_manual"
        if safe_name == "change_app_conf":
             return "skipped_manual"

    full_path = f"{method['base_path']}/{method['endpoint']}".replace("<server>", "")
    op = helper.get_operation(full_path, method['http_method'])
    
    if not op:
        return "skipped_no_openapi"

    class_name = "".join(x.title() for x in safe_name.split("_"))
    payload = helper.generate_payload_template(op)
    
    is_get = method['http_method'].upper() == "GET"
    
    if is_get:
        call_arg = ""
    else:
        payload_str = json.dumps(payload, indent=8).replace("true", "True").replace("false", "False").replace("null", "None")
        payload_str = payload_str.replace("}", "        }")
        call_arg = f", json={payload_str}"

    code = f"""import pytest
import responses
import allure
from src.api.{group}.{safe_name} import {safe_name}
from src.utils.http import APIClient

@pytest.fixture
def client():
    return APIClient(base_url="http://test-api.com", token="fake-token")

@allure.feature("{group.capitalize()}")
@allure.story("{method['title']}")
class Test{class_name}:

    @allure.title("Positive: Success")
    @responses.activate
    def test_success(self, client):
        responses.add(
            responses.{method['http_method'].upper()},
            "http://test-api.com{full_path}",
            json={{"status": "ok"}},
            status=200
        )
        response = {safe_name}(client{call_arg})
        assert response.status_code == 200

    @allure.title("Negative: Bad Request")
    @responses.activate
    def test_bad_request(self, client):
        responses.add(
            responses.{method['http_method'].upper()},
            "http://test-api.com{full_path}",
            json={{"error": "Bad Request"}},
            status=400
        )
        response = {safe_name}(client{call_arg})
        assert response.status_code == 400
"""
    test_path.parent.mkdir(parents=True, exist_ok=True)
    test_path.write_text(code, encoding="utf-8")
    return "updated"

def main():
    print("Starting Autonomous Content Filler...")
    try:
        helper = OpenAPIHelper()
    except Exception as e:
        print(f"Failed to load OpenAPI: {e}")
        return

    methods = parse_roadmap("UPDATED_ROADMAP.md")
    stats = {"updated": 0, "skipped_manual": 0, "skipped_no_openapi": 0}
    
    for method in methods:
        group, safe_name = get_group_and_name(method)
        
        res_src = fill_source(method, group, safe_name, helper)
        res_test = fill_test(method, group, safe_name, helper)
        
        if res_src == "updated":
            stats["updated"] += 1
        elif res_src == "skipped_manual":
            stats["skipped_manual"] += 1
        else:
            stats["skipped_no_openapi"] += 1
            
    print(f"Filling complete.")
    print(f"Updated: {stats['updated']}")
    print(f"Skipped (Manual): {stats['skipped_manual']}")
    print(f"Skipped (No OpenAPI match): {stats['skipped_no_openapi']}")
    
    Path("FILLING_REPORT.md").write_text(f"""# Autonomous Filling Report
    
- Total Methods Processed: {len(methods)}
- Successfully Updated: {stats['updated']}
- Preserved Manual Implementations: {stats['skipped_manual']}
- Failed to Match in OpenAPI: {stats['skipped_no_openapi']}

The system has automatically enriched the source code with Docstrings, Type Hints, and Parameter descriptions from OpenAPI.
Unit tests have been updated with valid payload templates.
""", encoding="utf-8")

if __name__ == "__main__":
    main()
