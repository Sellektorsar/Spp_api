"""
Pytest configuration: фикстуры для integration и e2e тестов.
"""
import pytest
import os
import json
import logging
import warnings
from datetime import datetime
from pathlib import Path

import requests as _requests
import responses
from dotenv import load_dotenv

from src.utils.test_context import TestContext
from src.utils.http import APIClient

# ──────────────────────────────────────────────
# Нормализатор ответов реального сервера
# ──────────────────────────────────────────────
class _NormalizedResponse:
    """
    Обёртка над requests.Response.
    Реальный сервер возвращает {"data": ..., "meta": {...}}.
    Этот враппер нормализует ответ в формат, который ожидают тесты:
      - {"data": [...],"meta":{"total_count":N}} → {"result":[...],"total_count":N}
      - {"data": {…}}                            → {…}
      - {"data": "id_string"}                    → {"id": "id_string"}
      - {"data": True/False}                     → {"status": "ok"}
    """
    def __init__(self, resp: _requests.Response):
        self._resp = resp

    @property
    def status_code(self) -> int:
        return self._resp.status_code

    @property
    def text(self) -> str:
        return self._resp.text

    @property
    def request(self):
        return self._resp.request

    # Псевдонимы полей ID: реальные имена → стандартный 'id'
    _ID_ALIASES = ("id_agg_session",)

    def json(self):
        raw = self._resp.json()
        if not isinstance(raw, dict) or "data" not in raw:
            return raw
        inner = raw["data"]
        meta = raw.get("meta", {})
        if isinstance(inner, list):
            # Нормализуем псевдонимы id в каждом элементе списка
            normalized = []
            for item in inner:
                if isinstance(item, dict):
                    item = dict(item)
                    for alias in self._ID_ALIASES:
                        if alias in item and "id" not in item:
                            item["id"] = item[alias]
                normalized.append(item)
            return {
                "result": normalized,
                "total_count": meta.get("total_count", len(inner)),
            }
        if isinstance(inner, dict):
            result = dict(inner)
            # Нормализуем псевдонимы id
            for alias in self._ID_ALIASES:
                if alias in result and "id" not in result:
                    result["id"] = result[alias]
            if meta:
                result.setdefault("meta", meta)
            return result
        if isinstance(inner, str):
            return {"id": inner}
        if isinstance(inner, bool):
            return {"status": "ok", "success": inner}
        if isinstance(inner, (int, float)):
            return {"value": inner}
        return raw

    def __getattr__(self, name):
        return getattr(self._resp, name)


class _NormalizingAPIClient(APIClient):
    """APIClient с авто-нормализацией ответов реального сервера.
    Буферизует все вызовы в self._pending_logs для записи в лог после теста.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._pending_logs: list = []  # список raw requests.Response за текущий тест

    def request(self, method, endpoint, **kwargs):
        raw_resp = super().request(method, endpoint, **kwargs)
        self._pending_logs.append(raw_resp)
        return _NormalizedResponse(raw_resp)

# Загружаем .env из корня проекта (если есть)
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env", override=False)

# ──────────────────────────────────────────────
# Настройка логгера
# ──────────────────────────────────────────────
_log_dir = Path("logs")
_log_dir.mkdir(exist_ok=True)
_log_file = _log_dir / f"api_responses_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

_logger = logging.getLogger("api_test")
_logger.setLevel(logging.DEBUG)
if not _logger.handlers:
    _fh = logging.FileHandler(_log_file, encoding="utf-8")
    _fh.setLevel(logging.DEBUG)
    _fh.setFormatter(logging.Formatter("%(message)s"))
    _logger.addHandler(_fh)


def _log_calls(test_name: str, calls) -> None:
    """Записывает все HTTP-вызовы теста в лог-файл."""
    test_calls = [c for c in calls if "/api/web/v1/auth" not in c.request.url]
    if not test_calls:
        return

    _logger.info("=" * 72)
    _logger.info(f"TEST: {test_name}")
    _logger.info("=" * 72)

    for call in test_calls:
        req = call.request
        resp = call.response

        _logger.info(f"\n  ► {req.method}  {req.url}")

        try:
            if req.body:
                body_obj = json.loads(req.body)
                _logger.info(
                    "    REQUEST BODY:\n"
                    + "\n".join(
                        "      " + line
                        for line in json.dumps(body_obj, ensure_ascii=False, indent=2).splitlines()
                    )
                )
        except Exception:
            if req.body:
                _logger.info(f"    REQUEST BODY: {req.body}")

        _logger.info(f"    RESPONSE STATUS: {resp.status_code}")
        try:
            resp_obj = json.loads(resp.text)
            _logger.info(
                "    RESPONSE BODY:\n"
                + "\n".join(
                    "      " + line
                    for line in json.dumps(resp_obj, ensure_ascii=False, indent=2).splitlines()
                )
            )
        except Exception:
            _logger.info(f"    RESPONSE BODY: {getattr(resp, 'text', '')}")

    _logger.info("")


def _log_real_calls(test_name: str, raw_responses: list) -> None:
    """Записывает все реальные HTTP-вызовы теста одним блоком в лог-файл."""
    # Фильтруем авторизацию
    calls = [
        r for r in raw_responses
        if not (r.request and "/api/web/v1/auth" in r.request.url)
    ]
    if not calls:
        return

    _logger.info("=" * 72)
    _logger.info(f"TEST: {test_name}")
    _logger.info("=" * 72)

    for resp in calls:
        req = resp.request
        if req:
            _logger.info(f"\n  ► {req.method}  {req.url}")
            try:
                if req.body:
                    body_obj = json.loads(req.body)
                    _logger.info(
                        "    REQUEST BODY:\n"
                        + "\n".join(
                            "      " + line
                            for line in json.dumps(body_obj, ensure_ascii=False, indent=2).splitlines()
                        )
                    )
            except Exception:
                if req.body:
                    _logger.info(f"    REQUEST BODY: {req.body}")

        _logger.info(f"    RESPONSE STATUS: {resp.status_code}")
        try:
            resp_obj = resp.json()
            _logger.info(
                "    RESPONSE BODY:\n"
                + "\n".join(
                    "      " + line
                    for line in json.dumps(resp_obj, ensure_ascii=False, indent=2).splitlines()
                )
            )
        except Exception:
            _logger.info(f"    RESPONSE BODY: {resp.text[:500]}")

    _logger.info("")


def _get_real_token(base_url: str, username: str, password: str, verify_ssl: bool) -> str:
    """Получить Bearer-токен через POST /api/web/v1/auth (form-data)."""
    auth_url = f"{base_url.rstrip('/')}/api/web/v1/auth"
    resp = _requests.post(
        auth_url,
        data={"username": username, "password": password},
        verify=verify_ssl,
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    # Ответ: {"data": {"access_token": "...", "token_type": "bearer"}}
    token = (
        data.get("data", {}).get("access_token")
        or data.get("access_token")
        or data.get("token")
    )
    if not token:
        raise RuntimeError(f"Токен не найден в ответе авторизации: {data}")
    return token


# ──────────────────────────────────────────────
# Фикстуры
# ──────────────────────────────────────────────

@pytest.fixture(scope="session")
def test_context():
    """
    Session-scoped контекст для передачи состояния между тестами в E2E сценариях.
    """
    return TestContext()


@pytest.fixture(scope="session")
def client():
    """
    API Client.
    - В режиме моков: http://test-api.com с фиктивным токеном.
    - В режиме реального сервера (SPP_TEST_REAL_ENV=1): авторизуется через логин/пароль,
      получает Bearer-токен и подключается к реальному серверу.
    """
    real_env = os.getenv("SPP_TEST_REAL_ENV", "")
    if real_env:
        base_url = os.getenv("SPP_API_URL", "http://localhost:8080")
        username = os.getenv("SPP_API_USERNAME", "")
        password = os.getenv("SPP_API_PASSWORD", "")
        timeout = int(os.getenv("SPP_API_TIMEOUT", "30"))
        verify_ssl = os.getenv("SPP_API_VERIFY_SSL", "true").lower() not in ("false", "0", "no")

        if not verify_ssl:
            warnings.filterwarnings("ignore", message="Unverified HTTPS request")

        if username and password:
            print(f"\n[AUTH] Авторизация на {base_url} как '{username}'...")
            token = _get_real_token(base_url, username, password, verify_ssl)
            print(f"[AUTH] Токен получен: {token[:40]}...")
        else:
            token = os.getenv("SPP_API_TOKEN", "")

        return _NormalizingAPIClient(base_url=base_url, token=token, timeout=timeout, verify_ssl=verify_ssl)

    # Режим моков
    base_url = os.getenv("SPP_API_URL", "http://test-api.com")
    token = os.getenv("SPP_API_TOKEN", "fake-test-token")
    return APIClient(base_url=base_url, token=token)


@pytest.fixture(autouse=True)
def mock_api(client, request):
    """
    - SPP_TEST_REAL_ENV не установлен → все запросы перехватываются моками.
    - SPP_TEST_REAL_ENV=1 → запросы идут на реальный сервер, mock_api=None.
    После каждого теста записывает request/response в лог-файл.
    """
    if os.getenv("SPP_TEST_REAL_ENV"):
        # Сбрасываем буфер перед тестом
        if hasattr(client, "_pending_logs"):
            client._pending_logs.clear()

        yield None

        # Логируем реальные вызовы ПОСЛЕ теста
        if hasattr(client, "_pending_logs"):
            _log_real_calls(request.node.nodeid, client._pending_logs)
            client._pending_logs.clear()
        return

    with responses.RequestsMock(assert_all_requests_are_fired=False) as rsps:
        rsps.add_passthru("http://localhost")

        rsps.add(
            responses.POST,
            f"{client.base_url}/api/web/v1/auth",
            json={"status": "ok", "token": "test-token-from-mock"},
            status=200,
        )

        yield rsps

        # Логируем все вызовы ВНУТРИ with-блока (до сброса calls)
        _log_calls(request.node.nodeid, rsps.calls)
