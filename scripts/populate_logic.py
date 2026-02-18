import os
import re
from pathlib import Path
from tests.utils.roadmap_parser import parse_roadmap

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)
    # Ensure __init__.py exists in every parent directory up to src/api or tests/unit/api
    parent = Path(path).parent
    while parent.name not in ["src", "tests", "unit", "api"]:
        init_file = parent / "__init__.py"
        if not init_file.exists():
            init_file.touch()
        parent = parent.parent

def get_group_and_name(method):
    base_path = method["base_path"]
    endpoint = method["endpoint"]
    
    # Handle wildcard paths
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
        # Try to make a better name from HTTP method if endpoint is generic
        method_name = f"{method['http_method'].lower()}_root"
    
    safe_name = re.sub(r"[^a-zA-Z0-9_]+", "_", method_name)
    # Remove leading/trailing underscores
    safe_name = safe_name.strip("_")
    
    return group, safe_name

def generate_source(method, group, safe_name):
    src_path = Path(f"src/api/{group}/{safe_name}.py")
    
    # Skip if file exists and has content (manual edit check), except empty stub
    if src_path.exists():
        content = src_path.read_text(encoding="utf-8")
        if "def get_roll" in content: # specific skip for our manual example
            print(f"Skipping {src_path} (manual content detected)")
            return

    ensure_dir(src_path.parent)
    
    full_endpoint = f"{method['base_path'].strip('/')}/{method['endpoint'].strip('/')}"
    http_method = method['http_method'].upper()
    
    code = f"""from src.utils.http import APIClient
import requests

def {safe_name}(client: APIClient, **kwargs) -> requests.Response:
    \"\"\"
    {method['title']}
    
    Endpoint: {full_endpoint}
    Method: {http_method}
    \"\"\"
    endpoint = "{full_endpoint}"
    return client.request("{http_method}", endpoint, **kwargs)
"""
    src_path.write_text(code, encoding="utf-8")
    print(f"Generated source: {src_path}")

def generate_test(method, group, safe_name):
    test_path = Path(f"tests/unit/api/{group}/test_{safe_name}.py")
    
    # Skip if file exists and has manual content (check for our manual example)
    if test_path.exists():
        content = test_path.read_text(encoding="utf-8")
        if "class TestGetRoll" in content:
            print(f"Skipping {test_path} (manual content detected)")
            return

    ensure_dir(test_path.parent)
    
    full_endpoint = f"{method['base_path'].strip('/')}/{method['endpoint'].strip('/')}"
    http_method = method['http_method'].upper()
    class_name = "".join(x.title() for x in safe_name.split("_"))
    
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
            responses.{http_method},
            "http://test-api.com/{full_endpoint}",
            json={{"status": "ok"}},
            status=200
        )
        response = {safe_name}(client, json={{}})
        assert response.status_code == 200

    @allure.title("Negative: Bad Request")
    @responses.activate
    def test_bad_request(self, client):
        responses.add(
            responses.{http_method},
            "http://test-api.com/{full_endpoint}",
            json={{"error": "Bad Request"}},
            status=400
        )
        response = {safe_name}(client, json={{}})
        assert response.status_code == 400
"""
    test_path.write_text(code, encoding="utf-8")
    print(f"Generated test: {test_path}")

def main():
    roadmap_path = "UPDATED_ROADMAP.md"
    if not os.path.exists(roadmap_path):
        print("Roadmap not found")
        return

    methods = parse_roadmap(roadmap_path)
    
    for method in methods:
        group, safe_name = get_group_and_name(method)
        generate_source(method, group, safe_name)
        generate_test(method, group, safe_name)

if __name__ == "__main__":
    main()
