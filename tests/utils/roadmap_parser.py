import re
from urllib.parse import urlparse


def split_url(url):
    value = url.replace("<server>", "").replace("< server>", "").strip()
    value = value.replace(" ", "")
    if value.startswith("http://") or value.startswith("https://"):
        value = urlparse(value).path
    if not value.startswith("/"):
        value = "/" + value
    parts = value.split("/")
    version_index = None
    for i, part in enumerate(parts):
        if re.fullmatch(r"v\d+", part):
            version_index = i
    if version_index is not None:
        base = "/".join(parts[:version_index + 1])
        endpoint = "/".join(parts[version_index + 1:])
    else:
        base = "/".join(parts[:2])
        endpoint = "/".join(parts[2:])
    if not base.startswith("/"):
        base = "/" + base
    return base.rstrip("/"), endpoint


def parse_roadmap(path):
    lines = [line.rstrip() for line in open(path, encoding="utf-8").read().splitlines()]
    blocks = []
    current = None
    for line in lines:
        if line.startswith("### "):
            if current:
                blocks.append(current)
            current = {"title": line[4:].strip(), "lines": []}
            continue
        if current is not None:
            current["lines"].append(line)
    if current:
        blocks.append(current)

    methods = []
    for block in blocks:
        title = block["title"]
        http_method = None
        url = None
        description = "Описание отсутствует"
        privacy = None
        priority = None
        query_required = []
        query_optional = []
        body_required = []
        body_optional = []
        scenarios = []
        mode = None
        for line in block["lines"]:
            if line.startswith("- HTTP-метод:"):
                http_method = line.split(":", 1)[1].strip()
            if line.startswith("- Endpoint URL:"):
                url = line.split(":", 1)[1].strip()
            if line.startswith("- Описание:"):
                description = line.split(":", 1)[1].strip()
            if line.startswith("- Тип приватности:"):
                privacy = line.split(":", 1)[1].strip()
            if line.startswith("- Приоритет метода:"):
                priority = line.split(":", 1)[1].strip()
            if line.startswith("- Параметры query:"):
                mode = "query"
                continue
            if line.startswith("- Параметры body:"):
                mode = "body"
                continue
            if line.startswith("- Тестовые сценарии:"):
                mode = "scenarios"
                continue
            if mode == "query" and line.strip().startswith("- Обязательные:"):
                payload = line.split(":", 1)[1].strip()
                if payload and payload != "не указаны в тексте":
                    query_required = [p.strip() for p in payload.split(";") if p.strip()]
            if mode == "query" and line.strip().startswith("- Опциональные:"):
                payload = line.split(":", 1)[1].strip()
                if payload and payload != "не указаны в тексте":
                    query_optional = [p.strip() for p in payload.split(";") if p.strip()]
            if mode == "body" and line.strip().startswith("- Обязательные:"):
                payload = line.split(":", 1)[1].strip()
                if payload and payload != "не указаны в тексте":
                    body_required = [p.strip() for p in payload.split(";") if p.strip()]
            if mode == "body" and line.strip().startswith("- Опциональные:"):
                payload = line.split(":", 1)[1].strip()
                if payload and payload != "не указаны в тексте":
                    body_optional = [p.strip() for p in payload.split(";") if p.strip()]
            if mode == "scenarios" and re.match(r"^\s*\d+\.\s+\[TC-", line):
                scenario = line.split("]", 1)[1].strip()
                scenarios.append(scenario)

        if not http_method or not url:
            continue
        base_path, endpoint = split_url(url)
        methods.append({
            "title": title,
            "http_method": http_method,
            "url": url,
            "base_path": base_path,
            "endpoint": endpoint,
            "description": description,
            "privacy": privacy or "приватный",
            "priority": priority or "средний",
            "query_required": query_required,
            "query_optional": query_optional,
            "body_required": body_required,
            "body_optional": body_optional,
            "scenarios": scenarios
        })
    return methods


def build_param_value(param):
    name = param.split(" (", 1)[0].strip()
    if "integer" in param:
        return name, 1
    if "boolean" in param:
        return name, True
    if "array" in param:
        return name, ["test"]
    return name, "test"


def render_endpoint(endpoint, scenario):
    if "{" in endpoint:
        value = "non-existent-id" if "Несуществующий" in scenario else "test-id"
        endpoint = re.sub(r"\{[^}]+\}", value, endpoint)
        endpoint = re.sub(r"\$\{[^}]+\}", value, endpoint)
    return endpoint


def build_request_data(method, scenario):
    params = {}
    body = {}
    if "Отсутствует обязательный" in scenario:
        return params, body
    for item in method["query_required"]:
        key, value = build_param_value(item)
        params[key] = value
    for item in method["query_optional"]:
        key, value = build_param_value(item)
        params[key] = value
    for item in method["body_required"]:
        key, value = build_param_value(item)
        body[key] = value
    for item in method["body_optional"]:
        key, value = build_param_value(item)
        body[key] = value
    if "Неверный формат" in scenario and params:
        key = list(params.keys())[0]
        params[key] = "!!!"
    if "Неверный формат" in scenario and body:
        key = list(body.keys())[0]
        body[key] = "!!!"
    return params, body


def expected_statuses(scenario):
    if "Позитивный" in scenario:
        return {200, 201, 204}
    if "Отсутствует обязательный" in scenario:
        return {400}
    if "Неверный формат" in scenario:
        return {400}
    if "Запрос без токена" in scenario:
        return {401}
    if "Недостаточно прав" in scenario:
        return {403}
    if "Несуществующий идентификатор" in scenario:
        return {404}
    if "Серверная ошибка" in scenario:
        return {500}
    if "Производительность" in scenario:
        return {200, 201, 204}
    return {200, 201, 204}
