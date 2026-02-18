import json
import re
from pathlib import Path
from tests.utils.roadmap_parser import parse_roadmap

def normalize_roadmap_path(path):
    # Remove query-like parts embedded in path (common in text docs)
    # e.g. /api/auth/user={id} -> /api/auth
    # Check for pattern /param=...
    if "=" in path:
        path = path.split("user=")[0].split("password=")[0]
    # Remove trailing & or /
    path = path.rstrip("&").rstrip("/")
    return path

def main():
    print("Loading Roadmap...")
    roadmap_methods = parse_roadmap("TEST_ROADMAP.md")
    roadmap_map = {}
    for m in roadmap_methods:
        raw_path = f"{m['base_path']}/{m['endpoint']}".replace("//", "/")
        # Heuristic to clean up paths that included query params in the URL string
        # e.g. /api/web/v1/auth/user={user_name}&password={password} -> /api/web/v1/auth
        # Real query params usually start with ? but sometimes docs are messy.
        clean_path = raw_path
        if "/user=" in clean_path:
             clean_path = clean_path.split("/user=")[0]
        
        key = f"{m['http_method'].upper()} {clean_path}"
        roadmap_map[key] = m

    print("Loading OpenAPI...")
    with open("openapi.json", "r", encoding="utf-8") as f:
        openapi = json.load(f)
    
    openapi_map = {}
    for path, methods in openapi["paths"].items():
        for method, details in methods.items():
            if method not in ["get", "post", "put", "delete", "patch"]:
                continue
            key = f"{method.upper()} {path}"
            openapi_map[key] = details

    new_endpoints = []
    removed_endpoints = []
    matched_endpoints = []

    # Check for New
    for key in openapi_map:
        if key not in roadmap_map:
            # Try to handle path params: {id} vs {order_id}
            # Regex match?
            found = False
            for r_key in roadmap_map:
                # Convert OpenAPI {param} to regex capture and Roadmap {param} to regex capture
                # Simplified: just check if they are same length of parts
                pass
            
            # For now, strict check, but handle specific known divergences
            new_endpoints.append(key)
        else:
            matched_endpoints.append(key)

    # Check for Removed
    for key in roadmap_map:
        if key not in openapi_map:
            removed_endpoints.append(key)

    # Generate Report
    report = []
    report.append("# Отчет об изменениях API (v5.0 -> v5.3)")
    report.append("Сравнение основано на `TEST_ROADMAP.md` (текущая реализация) и `openapi.json` (актуальная схема).")
    
    report.append(f"\n## Статистика")
    report.append(f"- Всего методов в Roadmap: {len(roadmap_map)}")
    report.append(f"- Всего методов в OpenAPI: {len(openapi_map)}")
    report.append(f"- Совпадений: {len(matched_endpoints)}")
    report.append(f"- Новых методов: {len(new_endpoints)}")
    report.append(f"- Удаленных/Измененных методов: {len(removed_endpoints)}")

    report.append(f"\n## 1. Новые эндпоинты (Присутствуют в OpenAPI, нет в Roadmap)")
    for key in sorted(new_endpoints):
        summary = openapi_map[key].get("summary", "Нет описания")
        report.append(f"- **{key}** - {summary}")

    report.append(f"\n## 2. Deprecated / Удаленные методы (Есть в Roadmap, нет в OpenAPI)")
    for key in sorted(removed_endpoints):
        report.append(f"- **{key}**")
        # Try to find if it was just renamed
        parts = key.split(" ")
        method = parts[0]
        url = parts[1]
        # Suggest potential matches
        # ...

    report.append(f"\n## 3. План миграции")
    report.append("### Этап 1: Актуализация существующих тестов")
    report.append("- Проверить методы из списка 'Удаленные' на предмет изменения URL (например, добавление path-параметров).")
    report.append("- Обновить `TEST_ROADMAP.md` и код тестов для совпадения с OpenAPI.")
    
    report.append("### Этап 2: Покрытие новых методов")
    report.append("- Создать заглушки тестов для новых эндпоинтов.")
    report.append("- Написать сценарии тестирования для критических новых функций (см. список выше).")

    Path("API_CHANGES_REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print("Report generated: API_CHANGES_REPORT.md")

if __name__ == "__main__":
    main()
