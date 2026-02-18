import re
from pathlib import Path
from tests.utils.roadmap_parser import split_url

def get_file_paths(url):
    # Convert URL to file path using the same logic as generate_unit_tests/populate_logic
    base_path, endpoint = split_url(url)
    
    if base_path == "/api/web/v1":
        parts = endpoint.split("/")
        group = parts[0] if parts[0] else "root"
    elif base_path == "/api/network_proxy/api/network/v1":
        group = "network_proxy"
    else:
        group = "root"
        
    method_name = endpoint.split("/")[-1] or "root"
    # Typo fix from roadmap
    method_name = method_name.rstrip(".")
    
    safe_name = re.sub(r"[^a-zA-Z0-9_]+", "_", method_name)
    
    src_path = Path(f"src/api/{group}/{safe_name}.py")
    test_path = Path(f"tests/unit/api/{group}/test_{safe_name}.py")
    return src_path, test_path

def main():
    report_path = "API_CHANGES_REPORT.md"
    if not Path(report_path).exists():
        print("Report not found.")
        return

    content = Path(report_path).read_text(encoding="utf-8")
    
    # Extract Deprecated section
    lines = content.splitlines()
    in_deprecated = False
    urls_to_remove = []
    
    for line in lines:
        if line.startswith("## 2. Deprecated"):
            in_deprecated = True
            continue
        if line.startswith("## 3."):
            in_deprecated = False
            break
            
        if in_deprecated and line.strip().startswith("- **"):
            # Format: - **METHOD URL**
            # e.g. - **GET /api/web/v1/auth**
            match = re.search(r"\*\*([A-Z]+) (\S+)\*\*", line)
            if match:
                urls_to_remove.append(match.group(2))

    print(f"Found {len(urls_to_remove)} endpoints to remove.")
    
    removed_count = 0
    for url in urls_to_remove:
        src, test = get_file_paths(url)
        
        if src.exists():
            try:
                src.unlink()
                print(f"Deleted: {src}")
                removed_count += 1
            except Exception as e:
                print(f"Error deleting {src}: {e}")
                
        if test.exists():
            try:
                test.unlink()
                print(f"Deleted: {test}")
                removed_count += 1
            except Exception as e:
                print(f"Error deleting {test}: {e}")

    print(f"Cleanup complete. Removed {removed_count} files.")

if __name__ == "__main__":
    main()
