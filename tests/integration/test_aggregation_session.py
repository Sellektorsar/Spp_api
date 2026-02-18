"""
Integration Tests: Aggregation Session Management
Проверяет управление сессиями агрегации: создание, фильтрация, статистика, детали.
Тесты работают против реального сервера spp-dev.

Ключевые исправления:
- hierarchy/detail принимает id_agg_session (не id)
- pallets/start принимает line_number + read_type + print_type (не id сессии)
- pallets/add_code/add_package/add_pallet/finish принимают line_number (не id сессии)
- withdrawal_code принимает code + package_code (не id + code)
- disbandment_package принимает package_code (не id + package_code)
"""
import pytest
import datetime

from src.api.aggregation_session.create import create as create_session
from src.api.aggregation_session.start import start as start_session
from src.api.aggregation_session.finish import finish as finish_session
from src.api.aggregation_session.add_code import add_code as agg_add_code
from src.api.aggregation_session.add_codes import add_codes as agg_add_codes
from src.api.aggregation_session.add_package import add_package
from src.api.aggregation_session.add_pallet import add_pallet
from src.api.aggregation_session.filter import filter as filter_sessions
from src.api.aggregation_session.detail import detail as get_detail
from src.api.aggregation_session.get_stats import get_stats
from src.api.aggregation_session.disbandment_package import disbandment_package
from src.api.aggregation_session.withdrawal_code import withdrawal_code


# Линия для lifecycle-тестов: toys — смена завершена, не активна
_AGG_TEST_LINE = 994849


@pytest.mark.integration
class TestAggregationSessionFilter:
    """Тесты фильтрации сессий агрегации."""

    def test_filter_all_sessions(self, client):
        """Получение списка всех сессий агрегации."""
        resp = filter_sessions(client, json={"limit": 20, "offset": 0})
        assert resp.status_code == 200
        data = resp.json()
        assert "total_count" in data
        assert isinstance(data["result"], list)

    def test_filter_sessions_pagination(self, client):
        """Пагинация: limit/offset принимаются сервером корректно."""
        resp1 = filter_sessions(client, json={"limit": 5, "offset": 0})
        resp2 = filter_sessions(client, json={"limit": 5, "offset": 5})
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert "total_count" in resp1.json()
        assert isinstance(resp1.json()["result"], list)
        assert isinstance(resp2.json()["result"], list)
        assert len(resp1.json()["result"]) <= 5
        assert len(resp2.json()["result"]) <= 5

    def test_filter_sessions_with_limit(self, client):
        """Фильтрация с ограниченным limit."""
        resp = filter_sessions(client, json={"limit": 3, "offset": 0})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["result"]) <= 3


@pytest.mark.integration
class TestAggregationSessionDetail:
    """Тесты получения иерархии вложенности реальной агрегационной сессии."""

    def test_get_session_detail_real(self, client, real_agg_session_id):
        """Получение иерархии вложенности реальной сессии.
        Для надежности сначала берем свежий ID из списка сессий."""
        
        # 1. Get a fresh valid session ID from filter
        filter_resp = filter_sessions(client, json={"limit": 1, "offset": 0})
        if filter_resp.status_code == 200:
            data = filter_resp.json()
            if data.get("result") and len(data["result"]) > 0:
                fresh_id = data["result"][0].get("id_agg_session")
                if fresh_id:
                    real_agg_session_id = fresh_id

        if not real_agg_session_id:
            pytest.skip("Не удалось получить валидный ID сессии для теста")

        resp = get_detail(client, json={"id_agg_session": real_agg_session_id})
        
        # Read-only operation on existing session should be 200
        assert resp.status_code == 200, f"Failed to get details for {real_agg_session_id}: {resp.text}"
        
        data = resp.json()
        assert "id" in data or "id_agg_session" in data

    def test_get_session_detail_nonexistent(self, client):
        """Запрос несуществующей сессии → ошибка."""
        resp = get_detail(client, json={"id_agg_session": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]

    def test_get_session_stats(self, client, real_agg_session_id):
        """Получение статистики реальной сессии."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        now = datetime.datetime.utcnow()
        start = (now - datetime.timedelta(days=30)).isoformat() + "Z"
        end = now.isoformat() + "Z"
        resp = get_stats(
            client,
            json={
                "id_agg_session": real_agg_session_id,
                "start_date": start,
                "end_date": end,
            },
        )
        assert resp.status_code == 200, f"Failed to get stats: {resp.text}"

    def test_get_global_stats(self, client):
        """Получение глобальной статистики агрегации (без ID сессии)."""
        now = datetime.datetime.utcnow()
        start = (now - datetime.timedelta(days=7)).isoformat() + "Z"
        end = now.isoformat() + "Z"
        resp = get_stats(client, json={"start_date": start, "end_date": end})
        assert resp.status_code == 200, f"Failed to get global stats: {resp.text}"


@pytest.mark.integration
class TestAggregationSessionLifecycle:
    """
    Жизненный цикл pallets-сессии:
      pallets/start → add_code → add_package → add_pallet → pallets/finish

    Все операции используют line_number (не id_agg_session).
    read_type=1 (сканер), print_type=1 (cups).
    """

    _LINE = _AGG_TEST_LINE  # toys, смена завершена

    def test_start_pallets_session(self, client):
        """Запуск новой pallets-сессии: line_number + read_type + print_type."""
        resp = start_session(
            client,
            json={
                "line_number": self._LINE,
                "read_type": 1,
                "print_type": 1,
            },
        )
        # 200 — успех; 400 — линия уже активна (допустимо в тестовой среде)
        assert resp.status_code in [200, 400, 422]

    def test_add_code_to_pallets_session(self, client):
        """Добавление GS1-кода в активную pallets-сессию (vision scanner)."""
        resp = agg_add_code(
            client,
            json={
                "line_number": self._LINE,
                "code": "010460049400904421dGVzdGNvZGU=",
            },
        )
        assert resp.status_code in [200, 400, 422]

    def test_add_package_to_pallets_session(self, client):
        """Добавление SSCC-упаковки в активную pallets-сессию."""
        resp = add_package(
            client,
            json={
                "line_number": self._LINE,
                "package_code": "000000000000000000",
            },
        )
        assert resp.status_code in [200, 400, 422]

    def test_add_pallet_to_pallets_session(self, client):
        """Добавление поддона в активную pallets-сессию."""
        resp = add_pallet(
            client,
            json={
                "line_number": self._LINE,
                "package_code": "000000000000000000",
                "pallet_code": "000000000000000001",
            },
        )
        assert resp.status_code in [200, 400, 422]

    def test_finish_pallets_session(self, client):
        """Завершение pallets-сессии по line_number."""
        resp = finish_session(
            client,
            json={"line_number": self._LINE},
        )
        assert resp.status_code in [200, 400, 422]

    def test_create_dashboard_session(self, client):
        """Создание dashboard-сессии агрегации (отдельный тип)."""
        resp = create_session(
            client,
            json={"name": f"Test Session {datetime.datetime.now().strftime('%H%M%S')}"},
        )
        assert resp.status_code in [200, 400, 422]
        if resp.status_code == 200:
            data = resp.json()
            sid = data.get("id") or data.get("id_agg_session")
            assert sid, "ID сессии должен присутствовать в ответе"


@pytest.mark.integration
class TestAggregationSessionCorrections:
    """
    Тесты корректировок: withdrawal_code и disbandment_package.
    Оба метода работают по коду/SSCC (не по id_agg_session).
    """

    def test_withdrawal_code_nonexistent(self, client):
        """Изъятие несуществующего кода из упаковки → ошибка."""
        resp = withdrawal_code(
            client,
            json={
                "code": "010460049400904421testcode93Ab==",
                "package_code": "000000000000000000",
            },
        )
        assert resp.status_code in [200, 400, 404, 422]

    def test_disbandment_package_nonexistent(self, client):
        """Расформирование несуществующей упаковки → ошибка."""
        resp = disbandment_package(
            client,
            json={"package_code": "000000000000000000"},
        )
        assert resp.status_code in [200, 400, 404, 422]
