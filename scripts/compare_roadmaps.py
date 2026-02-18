from tests.utils.roadmap_parser import parse_roadmap
from pathlib import Path

def normalize_url(url):
    # Remove <server> prefix
    url = url.replace("<server>", "").strip()
    # Remove query params for comparison
    if "?" in url:
        url = url.split("?")[0]
    # Remove trailing slash
    url = url.rstrip("/")
    # Handle {id} vs {order_id} differences by simple regex or ignoring content in {}
    # But usually precise match is better first
    return url

def main():
    print("Loading OpenAPI Roadmap...")
    openapi_methods = parse_roadmap("UPDATED_ROADMAP.md")
    openapi_map = {}
    for m in openapi_methods:
        key = f"{m['http_method'].upper()} {normalize_url(m['url'])}"
        openapi_map[key] = m

    print("Loading PDF Roadmap...")
    pdf_methods = parse_roadmap("ROADMAP_FROM_PDF_5.3.md")
    pdf_map = {}
    for m in pdf_methods:
        # PDF parser extracts method from text line, e.g. "GET" or "POST"
        # URL might be full path
        key = f"{m['http_method'].upper()} {normalize_url(m['url'])}"
        pdf_map[key] = m

    only_in_pdf = []
    only_in_openapi = []
    
    for key in pdf_map:
        if key not in openapi_map:
            only_in_pdf.append(pdf_map[key])
            
    for key in openapi_map:
        if key not in pdf_map:
            only_in_openapi.append(openapi_map[key])

    print(f"Methods in PDF: {len(pdf_map)}")
    print(f"Methods in OpenAPI: {len(openapi_map)}")
    print(f"Only in PDF: {len(only_in_pdf)}")
    print(f"Only in OpenAPI: {len(only_in_openapi)}")

    report = []
    report.append("# API 5.3 Analysis Report")
    report.append(f"Comparison between `SPP Описание API_5.3.pdf` (Documentation) and `openapi.json` (Implementation).")
    
    report.append(f"\n## Summary")
    report.append(f"- Documentation Methods: {len(pdf_map)}")
    report.append(f"- Implementation Methods: {len(openapi_map)}")
    
    if only_in_pdf:
        report.append(f"\n## Methods in Documentation but Missing in Implementation ({len(only_in_pdf)})")
        report.append("These methods might be planned but not implemented, or removed but docs not updated.")
        for m in only_in_pdf:
            report.append(f"- **{m['http_method']} {m['url']}**")
            report.append(f"  - Title: {m['title']}")

    if only_in_openapi:
        report.append(f"\n## Methods in Implementation but Missing in Documentation ({len(only_in_openapi)})")
        report.append("These methods are available in API but not documented in PDF.")
        for m in only_in_openapi:
            report.append(f"- **{m['http_method']} {m['url']}**")
            report.append(f"  - Title: {m['title']}")

    Path("API_5.3_ANALYSIS_REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print("Report generated: API_5.3_ANALYSIS_REPORT.md")

if __name__ == "__main__":
    main()
