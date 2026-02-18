import json
import re
from pathlib import Path
from tests.utils.roadmap_parser import parse_roadmap

def normalize_key(method, url):
    return f"{method.upper()} {url}"

def main():
    roadmap_path = "TEST_ROADMAP.md"
    roadmap_methods = parse_roadmap(roadmap_path)
    
    with open("openapi.json", "r", encoding="utf-8") as f:
        openapi = json.load(f)
        
    openapi_map = {}
    for path, methods in openapi["paths"].items():
        for method, details in methods.items():
            if method in ["get", "post", "put", "delete", "patch"]:
                openapi_map[normalize_key(method, path)] = {
                    "details": details,
                    "path": path,
                    "method": method
                }

    updated_methods = []
    processed_openapi_keys = set()
    
    # 1. Process existing roadmap methods
    for m in roadmap_methods:
        raw_path = f"{m['base_path']}/{m['endpoint']}".replace("//", "/")
        clean_path = raw_path
        if "/user=" in clean_path: 
            clean_path = clean_path.split("/user=")[0]
        if clean_path.endswith("."):
            clean_path = clean_path[:-1]
            
        key = normalize_key(m['http_method'], clean_path)
        
        if key in openapi_map:
            m['url'] = openapi_map[key]['path']
            updated_methods.append(m)
            processed_openapi_keys.add(key)
            continue
            
        new_key = None
        if "password/change" in key: new_key = key.replace("password/change", "user/password/change")
        elif "permissions/get" in key: new_key = key.replace("permissions/get", "user/permissions/get")
        elif "permissions/update" in key: new_key = key.replace("permissions/update", "user/permissions/update")
        elif "download_csv" in key: new_key = key.replace("download_csv", "download")
        
        if new_key and new_key in openapi_map:
            m['url'] = openapi_map[new_key]['path']
            m['http_method'] = openapi_map[new_key]['method'].upper()
            m['title'] = f"{m['title']} (Renamed)"
            updated_methods.append(m)
            processed_openapi_keys.add(new_key)
            continue
            
        m['title'] = f"[DEPRECATED] {m['title']}"
        updated_methods.append(m)

    # 2. Add new methods
    for key, data in openapi_map.items():
        if key not in processed_openapi_keys:
            details = data['details']
            new_method = {
                "title": details.get("summary", "New Method"),
                "http_method": data['method'].upper(),
                "url": data['path'],
                "description": details.get("description", "Автоматически добавлено из OpenAPI"),
                "privacy": "приватный" if "security" in details else "публичный",
                "request_type": "application/json",
                "response_type": "application/json",
                "status_codes": ["200"],
                "priority": "средний",
                "query_required": [],
                "query_optional": [],
                "body_required": [],
                "body_optional": [],
                "valid_data": ["Параметры по умолчанию"],
                "invalid_data": ["Некорректный формат"],
                "scenarios": [
                    "(высокий) Позитивный запрос",
                    "(средний) Невалидные данные",
                    "(высокий) Ошибка авторизации"
                ]
            }
            updated_methods.append(new_method)

    # 3. Generate Markdown
    lines = []
    lines.append("# Дорожная карта тестирования API SPP 5.3 (Updated)")
    lines.append("")
    lines.append("## Обновление")
    lines.append("Документ обновлен на основе `openapi.json` и `SPP Руководство пользователя_5.3.pdf`.")
    lines.append("")
    lines.append("## Общие требования")
    lines.append("- 100% покрытие методов с аутентификацией")
    lines.append("- Минимум 80% покрытие критических методов")
    lines.append("")
    
    for idx, method in enumerate(updated_methods, start=1):
        lines.append(f"### {idx}. {method['title']}")
        lines.append(f"- HTTP-метод: {method['http_method']}")
        lines.append(f"- Endpoint URL: <server>{method['url']}")
        lines.append(f"- Описание: {method.get('description', 'Описание отсутствует')}")
        lines.append(f"- Тип приватности: {method['privacy']}")
        lines.append(f"- Приоритет метода: {method['priority']}")
        
        lines.append("- Тестовые сценарии:")
        for s_idx, scenario in enumerate(method['scenarios'], start=1):
             # Handle scenario format
             if isinstance(scenario, str):
                 sc_text = scenario
             else:
                 sc_text = str(scenario)
             
             lines.append(f"  {s_idx}. [TC-{idx:03d}-{s_idx:02d}] {sc_text}")
             lines.append(f"     - Ожидаемый результат: HTTP 200/400/etc")
        
        lines.append("")

    Path("UPDATED_ROADMAP.md").write_text("\n".join(lines), encoding="utf-8")
    print("Updated Roadmap generated.")

if __name__ == "__main__":
    main()
