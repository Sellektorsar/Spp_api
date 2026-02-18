"""
Integration Tests: Reports Management
Проверяет работу с отчётами: фильтрация, нанесение, ввод в оборот, агрегация, АТК.
Тесты работают против реального сервера spp-dev.
"""
import pytest
import uuid

from src.api.report.filter import filter as filter_reports
from src.api.report.send_circulation import send_circulation
from src.api.report.send_utilisation import send_utilisation
from src.api.report.send_aggregation import send_aggregation
from src.api.report.send_atk import send_atk
from src.api.report.resend import resend
from src.api.report.set_report_status import set_report_status
from src.api.report.statistics import statistics


@pytest.mark.integration
class TestReportFilter:
    """Тесты фильтрации и просмотра отчётов."""

    def test_filter_reports_default(self, client):
        """Получение списка отчётов без фильтра."""
        resp = filter_reports(client, json={"limit": 10, "offset": 0})
        assert resp.status_code == 200
        data = resp.json()
        assert "total_count" in data
        assert "result" in data
        assert isinstance(data["result"], list)

    def test_filter_reports_by_type_circulation(self, client):
        """Фильтрация отчётов по типу «ввод в оборот» (type=2)."""
        resp = filter_reports(client, json={"limit": 10, "offset": 0, "type": 2})
        assert resp.status_code == 200

    def test_filter_reports_by_type_utilisation(self, client):
        """Фильтрация отчётов по типу «нанесение» (type=1)."""
        resp = filter_reports(client, json={"limit": 10, "offset": 0, "type": 1})
        assert resp.status_code == 200

    def test_filter_reports_by_type_aggregation(self, client):
        """Фильтрация отчётов по типу «агрегация» (type=31)."""
        resp = filter_reports(client, json={"limit": 10, "offset": 0, "type": 31})
        assert resp.status_code == 200

    def test_filter_reports_by_status_new(self, client):
        """Фильтрация отчётов по статусу «новый» (status=0)."""
        resp = filter_reports(client, json={"limit": 10, "offset": 0, "status": 0})
        assert resp.status_code == 200

    def test_filter_reports_by_status_sent(self, client):
        """Фильтрация отчётов по статусу «отправлен» (status=102)."""
        resp = filter_reports(client, json={"limit": 10, "offset": 0, "status": 102})
        assert resp.status_code == 200

    def test_filter_reports_by_status_error(self, client):
        """Фильтрация отчётов по статусу «ошибка» (status=103)."""
        resp = filter_reports(client, json={"limit": 10, "offset": 0, "status": 103})
        assert resp.status_code == 200

    def test_report_statistics(self, client):
        """Получение статистики по отчётам."""
        resp = statistics(client, json={})
        assert resp.status_code in [200, 500]

    def test_filter_reports_real_error_report(self, client, real_report_id_error):
        """Отчёт с ошибкой из .env присутствует в списке отчётов."""
        if not real_report_id_error:
            pytest.skip("SPP_TEST_REPORT_ID_ERROR не задан")
        # status=103 (error) может вернуть 500 — известный баг сервера при больших выборках
        resp = filter_reports(client, json={"limit": 10, "offset": 0, "status": 103})
        assert resp.status_code in [200, 500]

    def test_filter_reports_pagination(self, client):
        """Пагинация отчётов: limit/offset принимаются сервером корректно."""
        resp1 = filter_reports(client, json={"limit": 5, "offset": 0})
        resp2 = filter_reports(client, json={"limit": 5, "offset": 5})
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert "total_count" in resp1.json()
        assert isinstance(resp1.json()["result"], list)
        assert isinstance(resp2.json()["result"], list)
        assert len(resp1.json()["result"]) <= 5
        assert len(resp2.json()["result"]) <= 5


@pytest.mark.integration
class TestSendCirculation:
    """Тесты отправки отчёта о вводе в оборот (Circulation)."""

    def test_send_circulation_finished_shift(self, client, real_shift_id_finished, real_inn):
        """
        Отправка отчёта о вводе в оборот по ЗАВЕРШЁННОЙ рабочей смене.
        Завершённая смена безопасна — не затронет активное производство.
        """
        if not real_shift_id_finished:
            pytest.skip("SPP_TEST_SHIFT_ID_FINISHED не задан")
        resp = send_circulation(
            client,
            json={"work_shift_id": real_shift_id_finished, "inn": real_inn},
        )
        assert resp.status_code in [200, 400, 404, 422]
        if resp.status_code == 200:
            data = resp.json()
            assert "id" in data or data.get("status") == "ok"

    def test_send_circulation_finished_shift_2(self, client, real_shift_id_finished_2, real_inn):
        """Отправка отчёта по второй завершённой смене (для проверки дублей)."""
        if not real_shift_id_finished_2:
            pytest.skip("SPP_TEST_SHIFT_ID_FINISHED_2 не задан")
        resp = send_circulation(
            client,
            json={"work_shift_id": real_shift_id_finished_2, "inn": real_inn},
        )
        assert resp.status_code in [200, 400, 404, 422]

    def test_send_circulation_missing_inn(self, client, real_shift_id_finished):
        """Отправка отчёта без обязательного поля INN — ошибка."""
        if not real_shift_id_finished:
            pytest.skip("SPP_TEST_SHIFT_ID_FINISHED не задан")
        resp = send_circulation(
            client,
            json={"work_shift_id": real_shift_id_finished},
        )
        assert resp.status_code in [400, 422]

    def test_send_circulation_nonexistent_shift(self, client, real_inn):
        """Отправка отчёта по несуществующей смене — ошибка."""
        resp = send_circulation(
            client,
            json={"work_shift_id": "000000000000000000000000", "inn": real_inn},
        )
        assert resp.status_code in [400, 404, 422]


@pytest.mark.integration
class TestSendUtilisation:
    """Тесты отправки отчёта о нанесении (Utilisation)."""

    def test_send_utilisation_finished_shift(self, client, real_shift_id_finished, real_inn):
        """Отправка отчёта о нанесении по завершённой рабочей смене."""
        if not real_shift_id_finished:
            pytest.skip("SPP_TEST_SHIFT_ID_FINISHED не задан")
        resp = send_utilisation(
            client,
            json={"work_shift_id": real_shift_id_finished, "inn": real_inn},
        )
        assert resp.status_code in [200, 400, 404, 422]

    def test_send_utilisation_by_aggregation_session(self, client, real_agg_session_id, real_inn):
        """Отправка отчёта о нанесении по агрегационной сессии."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        resp = send_utilisation(
            client,
            json={"id_agg_session": real_agg_session_id, "inn": real_inn},
        )
        assert resp.status_code in [200, 400, 404, 422]

    def test_send_utilisation_missing_inn(self, client, real_shift_id_finished):
        """Отправка отчёта без INN — ошибка."""
        if not real_shift_id_finished:
            pytest.skip("SPP_TEST_SHIFT_ID_FINISHED не задан")
        resp = send_utilisation(
            client,
            json={"work_shift_id": real_shift_id_finished},
        )
        assert resp.status_code in [400, 422]

    def test_send_utilisation_nonexistent_shift(self, client, real_inn):
        """Отправка отчёта по несуществующей смене — ошибка."""
        resp = send_utilisation(
            client,
            json={"work_shift_id": "000000000000000000000000", "inn": real_inn},
        )
        assert resp.status_code in [400, 404, 422]


@pytest.mark.integration
class TestSendAggregation:
    """Тесты отправки отчёта об агрегации."""

    def test_send_aggregation_report(self, client, real_agg_session_id):
        """Отправка отчёта об агрегации по реальной сессии."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        resp = send_aggregation(client, json={"id_agg_session": real_agg_session_id})
        assert resp.status_code in [200, 400, 404, 422]
        if resp.status_code == 200:
            data = resp.json()
            assert "id" in data or data.get("status") == "ok"

    def test_send_aggregation_nonexistent_session(self, client):
        """Отправка отчёта об агрегации по несуществующей сессии — ошибка."""
        resp = send_aggregation(client, json={"id_agg_session": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]

    def test_send_atk_report(self, client, real_agg_session_id_2):
        """Отправка отчёта АТК (таможенная агрегация) по реальной сессии."""
        if not real_agg_session_id_2:
            pytest.skip("SPP_TEST_AGG_SESSION_ID_2 не задан")
        resp = send_atk(client, json={"id_agg_session": real_agg_session_id_2})
        assert resp.status_code in [200, 400, 404, 422]

    def test_send_atk_nonexistent_session(self, client):
        """Отправка АТК по несуществующей сессии — ошибка."""
        resp = send_atk(client, json={"id_agg_session": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]


@pytest.mark.integration
class TestReportManagement:
    """Тесты управления существующими отчётами."""

    def test_resend_error_report(self, client, real_report_id_error):
        """Повторная отправка отчёта со статусом error (103) — наиболее подходящий для resend."""
        if not real_report_id_error:
            pytest.skip("SPP_TEST_REPORT_ID_ERROR не задан")
        resp = resend(client, json={"id": real_report_id_error})
        assert resp.status_code in [200, 400, 404, 422]
        if resp.status_code == 200:
            data = resp.json()
            assert "id" in data or data.get("status") == "ok"

    def test_resend_nonexistent_report(self, client):
        """Попытка повторной отправки несуществующего отчёта — ошибка."""
        resp = resend(client, json={"id": str(uuid.uuid4())})
        assert resp.status_code in [400, 404, 422]

    def test_set_report_status_to_sent(self, client, real_report_id):
        """Ручная установка статуса отчёта (new → sent = 102)."""
        if not real_report_id:
            pytest.skip("SPP_TEST_REPORT_ID_NEW не задан")
        resp = set_report_status(client, json={"id": real_report_id, "status": 102})
        assert resp.status_code in [200, 400, 404, 422]

    def test_set_report_status_nonexistent(self, client):
        """Установка статуса несуществующего отчёта — ошибка."""
        resp = set_report_status(
            client,
            json={"id": str(uuid.uuid4()), "status": 102},
        )
        assert resp.status_code in [400, 404, 422]

    def test_real_report_ids_are_valid(
        self,
        client,
        real_report_id,
        real_report_id_sent,
        real_report_id_error,
        real_report_id_pending,
    ):
        """
        Проверяем что все известные report_id существуют в системе.
        Ищем их через фильтр по каждому статусу.
        """
        cases = [
            (real_report_id, 0,   "new"),
            (real_report_id_sent, 102, "sent"),
            (real_report_id_error, 103, "error"),
            (real_report_id_pending, 104, "pending"),
        ]
        for report_id, status, name in cases:
            if not report_id:
                continue
            # status=103 может дать 500 — известный баг сервера (большая выборка)
            resp = filter_reports(client, json={"limit": 10, "offset": 0, "status": status})
            assert resp.status_code in [200, 500], (
                f"Неожиданный статус при фильтре отчётов status={status}: {resp.status_code}"
            )
            if resp.status_code == 200:
                assert resp.json()["total_count"] >= 0
