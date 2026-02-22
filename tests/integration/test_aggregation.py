"""
Integration tests for Aggregation operations.
Покрывает: Сессии, иерархия, буферы KITY/KIGU/KIN.
"""
import pytest
import os


class TestAggregationIntegration:
    """
    Интеграционные тесты для операций агрегации.
    Endpoints: /api/web/v1/aggregation_session/*
    """

    def test_filter_aggregation_sessions(self, client):
        """Фильтрация агрегационных сессий."""
        resp = client.post(
            "/api/web/v1/aggregation_session/filter",
            json={
                "limit": 20,
                "offset": 0,
                "status": "finished"
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        print(f"[INT-AGG] Найдено сессий: {data.get('total_count', 0)}")

    def test_get_active_session(self, client):
        """Получение активной сессии на линии."""
        line_id = os.getenv("SPP_TEST_AGG_LINE_ID", 1)
        
        resp = client.post(
            "/api/web/v1/aggregation_session/active",
            json={"line_id": line_id}
        )
        # 200 - есть активная, 404 - нет активной
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.json()
            assert "id" in data
            print(f"[INT-AGG] Активная сессия найдена")
        else:
            print(f"[INT-AGG] Нет активной сессии")

    def test_get_session_detail_info(self, client, real_agg_session_id):
        """Получение детальной информации о сессии."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")

        resp = client.post(
            "/api/web/v1/aggregation_session/get_detail_info",
            json={"id": real_agg_session_id}
        )
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.json()
            assert "id" in data
            print(f"[INT-AGG] Детальная информация получена")

    def test_get_session_hierarchy(self, client, real_agg_session_id):
        """Получение иерархии сессии."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")

        resp = client.post(
            "/api/web/v1/aggregation_session/hierarchy",
            json={"id": real_agg_session_id}
        )
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.json()
            assert "hierarchy" in data or "packages" in data
            print(f"[INT-AGG] Иерархия получена")

    def test_get_hierarchy_detail(self, client, real_agg_session_id):
        """Получение детальной иерархии вложенности."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")

        resp = client.post(
            "/api/web/v1/aggregation_session/hierarchy/detail",
            json={"id": real_agg_session_id}
        )
        assert resp.status_code in [200, 404]
        print(f"[INT-AGG] Детальная иерархия получена")

    def test_check_code_in_session(self, client, real_agg_session_id):
        """Проверка кода в сессии."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")

        test_code = "0104600494009044215TestCheck93dGVzdA=="
        
        resp = client.post(
            "/api/web/v1/aggregation_session/check_code",
            json={
                "id": real_agg_session_id,
                "code": test_code
            }
        )
        assert resp.status_code in [200, 404]
        print(f"[INT-AGG] Проверка кода выполнена")

    def test_buffer_kity_statistics(self, client):
        """Статистика буфера KITY."""
        resp = client.post(
            "/api/web/v1/aggregation_session/buffer/kity/statistics",
            json={}
        )
        assert resp.status_code in [200, 404]
        print(f"[INT-AGG] Статистика KITY получена")

    def test_buffer_kigu_statistics(self, client, real_agg_session_id):
        """Статистика буфера KIGU."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")

        resp = client.post(
            "/api/web/v1/aggregation_session/buffer/kigu/statistics",
            json={"id_agg_session": real_agg_session_id}
        )
        assert resp.status_code in [200, 404]
        print(f"[INT-AGG] Статистика KIGU получена")

    def test_buffer_kin_statistics(self, client, real_agg_session_id):
        """Статистика буфера KIN."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")

        resp = client.post(
            "/api/web/v1/aggregation_session/buffer/kin/statistics",
            json={"id_agg_session": real_agg_session_id}
        )
        assert resp.status_code in [200, 404]
        print(f"[INT-AGG] Статистика KIN получена")

    def test_preset_filter(self, client):
        """Фильтрация пресетов агрегации."""
        resp = client.post(
            "/api/web/v1/aggregation_session/preset/filter",
            json={"limit": 10, "offset": 0}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        print(f"[INT-AGG] Найдено пресетов: {data.get('total_count', 0)}")

    def test_dashboard_filter(self, client):
        """Фильтрация дашбордов агрегации."""
        resp = client.post(
            "/api/web/v1/aggregation_session/dashboard/filter",
            json={"limit": 10, "offset": 0}
        )
        assert resp.status_code == 200
        print(f"[INT-AGG] Дашборды получены")

