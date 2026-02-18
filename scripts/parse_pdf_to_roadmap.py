import re
from pathlib import Path

# Config
input_text_path = "pdf_api_5.3_content.txt"
output_roadmap_path = "ROADMAP_FROM_PDF_5.3.md"

def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()

def build_title(section_lines, url):
    collected = []
    for line in section_lines:
        line_stripped = line.strip()
        if not line_stripped: continue
        if line_stripped.startswith("--- Page"): continue
        if line_stripped.startswith("Тип приватности:"): break
        if line_stripped.startswith("URL:"): break
        if line_stripped.startswith("Метод:"): continue
        if line_stripped.startswith("Данный метод"): break
        if line_stripped.startswith("Пример") or line_stripped.startswith("Параметры"): break
        if line_stripped.startswith("Примечание"): continue
        collected.append(line_stripped)
    raw_title = normalize_whitespace(" ".join(collected))
    raw_title = re.sub(r"\.{5,}", "", raw_title).strip()
    # Cleanup known prefixes
    for prefix in ["Данный метод", "Метод используется", "Метод предназначен"]:
        if prefix in raw_title:
            raw_title = raw_title.split(prefix)[0].strip()
    if not raw_title:
        raw_title = f"Метод {url}"
    return raw_title

def extract_sections(lines):
    url_indices = [i for i, line in enumerate(lines) if line.strip().startswith("URL:")]
    sections = []
    for idx, url_idx in enumerate(url_indices):
        start_search = max(0, url_idx - 40)
        title_idx = None
        # Look backwards for "Метод" or "METHOD"
        for j in range(url_idx, start_search, -1):
            line = lines[j].strip()
            if line.startswith("Метод:"): continue
            # Heuristic: Title usually contains "МЕТОД" in uppercase or Mixed
            if "МЕТОД" in line.upper() and not line.startswith("Данный"):
                title_idx = j
                break
        if title_idx is None:
            title_idx = start_search
        end = url_indices[idx + 1] if idx + 1 < len(url_indices) else len(lines)
        sections.append((title_idx, lines[title_idx:end], url_idx))
    return sections

def detect_description(section_lines):
    for line in section_lines:
        if line.strip().startswith("Данный метод") or line.strip().startswith("Метод используется"):
            return normalize_whitespace(line)
    return "Описание не указано в тексте."

def generate_roadmap():
    if not Path(input_text_path).exists():
        print(f"File {input_text_path} not found.")
        return

    text = Path(input_text_path).read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    sections = extract_sections(lines)
    methods = []
    
    for start, section_lines, url_idx in sections:
        try:
            url_line = lines[url_idx]
            if "URL:" not in url_line: continue
            url = url_line.split("URL:", 1)[1].strip()
            
            title = build_title(section_lines, url)
            
            http_method = None
            # Search for Method: GET/POST near URL
            for j in range(max(0, url_idx - 10), min(url_idx + 10, len(lines))):
                line = lines[j].strip()
                if line.startswith("Метод:") or line.startswith("HTTP метод:"):
                    http_method = line.split(":", 1)[1].strip()
                    break
            
            # Fallback if method line is missing but title has (METHOD/URL)
            if not http_method:
                 match = re.search(r"\((GET|POST|PUT|DELETE)", title)
                 if match:
                     http_method = match.group(1)
            
            if not url or not http_method:
                continue

            description = detect_description(section_lines)
            
            methods.append({
                "title": title,
                "http_method": http_method,
                "url": url,
                "description": description
            })
        except Exception as e:
            # print(f"Error parsing section around line {url_idx}: {e}")
            continue

    lines_out = []
    lines_out.append("# Дорожная карта из PDF 5.3")
    
    for idx, method in enumerate(methods, start=1):
        lines_out.append(f"### {idx}. {method['title']}")
        lines_out.append(f"- HTTP-метод: {method['http_method']}")
        lines_out.append(f"- Endpoint URL: {method['url']}")
        lines_out.append(f"- Описание: {method['description']}")
        lines_out.append("")
        
    Path(output_roadmap_path).write_text("\n".join(lines_out), encoding="utf-8")
    print(f"Generated {output_roadmap_path} with {len(methods)} methods.")

if __name__ == "__main__":
    generate_roadmap()
