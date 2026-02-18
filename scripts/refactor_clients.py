import os
import re
from pathlib import Path
from src.utils.openapi_helper import OpenAPIHelper

def refactor_file(file_path: Path, helper: OpenAPIHelper):
    content = file_path.read_text(encoding="utf-8")
    
    endpoint_match = re.search(r'endpoint\s*=\s*"([^"]+)"', content)
    if not endpoint_match:
        return False
    endpoint = endpoint_match.group(1)
    
    method_match = re.search(r'client\.request\("([A-Z]+)"', content)
    if not method_match:
        return False
    http_method = method_match.group(1)
    
    op = helper.get_operation(endpoint, http_method)
    if not op:
        return False
    
    model_name = helper.get_request_model_name(op)
    if not model_name:
        return False
        
    print(f"Refactoring {file_path} with model {model_name}...")
    
    import_stmt = f"from src.models import {model_name}"
    if import_stmt not in content:
        lines = content.splitlines()
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_idx = i + 1
        lines.insert(insert_idx, import_stmt)
        content = "\n".join(lines)
    
    content = re.sub(
        r"def (\w+)\(client: APIClient, \*\*kwargs\) -> requests.Response:",
        f"def \\1(client: APIClient, body: {model_name} | dict | None = None, **kwargs) -> requests.Response:",
        content
    )
    
    logic_block = f"""    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
"""
    
    if "if body:" in content:
        return False

    lines = content.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("return client.request"):
            indent = line[:len(line) - len(line.lstrip())]
            indented_logic = "\n".join([indent + l for l in logic_block.splitlines()])
            lines.insert(i, indented_logic)
            break
    
    file_path.write_text("\n".join(lines), encoding="utf-8")
    return True

def main():
    try:
        helper = OpenAPIHelper()
    except Exception as e:
        print(f"Failed to load OpenAPI: {e}")
        return
        
    src_dir = Path("src/api")
    count = 0
    for file_path in src_dir.rglob("*.py"):
        if file_path.name == "__init__.py":
            continue
        if refactor_file(file_path, helper):
            count += 1
            
    print(f"Refactoring complete. Updated {count} files.")

if __name__ == "__main__":
    main()
