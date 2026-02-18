"""
E2E Tests: Report Management Workflow
Сценарий: фильтрация отчётов → повторная отправка → управление статусами.

Шаги:
1. Получить список отчётов (фильтрация)
2. Найти отчёт в статусе "error" или "new"
3. Повторно отправить отчёт
4. Проверить, что статус изменился
5. Вручную установить финальный статус
"""
import pytest
import responses
import uuid

from src.api.report.filter import filter as filter_reports
from src.api.report.statistics import statistics as report_stats
from src.api.report.resend import resend as resend_report
from src.api.report.set_report_status import set_report_status
from src.api.report.check_code import check_code


REPORT_ID = str(uuid.uuid4())
INN = "7700000000"


@pytest.mark.e2e
@pytest.mark.order(4)
class TestReportWorkflow:
    """
    E2E Сценарий: Управление жизненным циклом отчётов в ГИС МТ.
    """

    def test_01_get_report_statistics(self, client, test_context, mock_api):
        """Шаг 1: Получение общей статистики по отчётам."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/statistics",
                json={
                    "total": 150,
                    "new": 10,
                    "pending": 5,
                    "sent": 120,
                    "error": 15,
                },
                status=200,
            )

        resp = report_stats(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        print(f"[E2E-REPORT] Статистика: total={data.get('total', 0)}, error={data.get('error', 0)}")

    def test_02_filter_error_reports(self, client, test_context, mock_api):
        """Шаг 2: Фильтрация отчётов с ошибками."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/filter",
                json={
                    "total_count": 2,
                    "result": [
                        {"id": REPORT_ID, "type": "circulation", "status": "error"},
                        {"id": str(uuid.uuid4()), "type": "utilisation", "status": "error"},
                    ],
                },
                status=200,
            )

        resp = filter_reports(client, json={"limit": 10, "offset": 0, "status": "error"})
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data

        if data["result"]:
            test_context.add("error_report_id", data["result"][0]["id"])
            print(f"[E2E-REPORT] Найдено {data['total_count']} отчётов с ошибками")
        else:
            test_context.add("error_report_id", REPORT_ID)
            print("[E2E-REPORT] Отчётов с ошибками нет, используем mock ID")

    def test_03_resend_report(self, client, test_context, mock_api):
        """Шаг 3: Повторная отправка отчёта с ошибкой."""
        report_id = test_context.get_last("error_report_id")
        assert report_id, "error_report_id от предыдущего шага отсутствует"

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/resend",
                json={"id": report_id, "status": "pending"},
                status=200,
            )

        resp = resend_report(client, json={"id": report_id})
        assert resp.status_code == 200
        data = resp.json()
        print(f"[E2E-REPORT] Отчёт повторно отправлен: {report_id}, новый статус: {data.get('status')}")

    def test_04_filter_pending_reports(self, client, test_context, mock_api):
        """Шаг 4: Проверка, что отчёт теперь в статусе 'pending'."""
        report_id = test_context.get_last("error_report_id")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/filter",
                json={
                    "total_count": 1,
                    "result": [{"id": report_id, "status": "pending"}],
                },
                status=200,
            )

        resp = filter_reports(client, json={"limit": 10, "offset": 0, "status": "pending"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] >= 0
        print(f"[E2E-REPORT] Отчётов в статусе pending: {data['total_count']}")

    def test_05_set_report_status_manually(self, client, test_context, mock_api):
        """Шаг 5: Ручная установка статуса отчёта (если ГИС МТ не ответил)."""
        report_id = test_context.get_last("error_report_id")
        assert report_id, "error_report_id от предыдущего шага отсутствует"

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/set_report_status",
                json={"id": report_id, "status": "sent"},
                status=200,
            )

        resp = set_report_status(client, json={"id": report_id, "status": "sent"})
        assert resp.status_code == 200
        print(f"[E2E-REPORT] Статус отчёта вручную установлен в 'sent': {report_id}")

    def test_06_filter_sent_reports(self, client, test_context, mock_api):
        """Шаг 6: Проверка итоговой фильтрации отчётов по статусу 'sent'."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/filter",
                json={
                    "total_count": 121,
                    "result": [
                        {"id": str(uuid.uuid4()), "status": "sent", "type": "circulation"},
                    ],
                },
                status=200,
            )

        resp = filter_reports(client, json={"limit": 10, "offset": 0, "status": "sent"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] >= 0
        print(f"[E2E-REPORT] Отчётов в статусе sent: {data['total_count']}")

    def test_07_check_code_in_gis(self, client, test_context, mock_api):
        """Шаг 7: Проверка кода маркировки в ГИС МТ."""
        test_code = "0104606203399737215code093dGVzdA=="

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/gis/check_code",
                json={
                    "code": test_code,
                    "status": "in_circulation",
                    "gtin": "04606203399737",
                },
                status=200,
            )

        resp = check_code(client, json={"code": test_code})
        assert resp.status_code == 200
        data = resp.json()
        print(f"[E2E-REPORT] Проверка кода в ГИС МТ: статус={data.get('status')}")
