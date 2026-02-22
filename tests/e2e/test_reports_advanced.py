"""
E2E Сценарии: Продвинутая работа с отчетами.
Покрывает: повторная отправка, ручной статус, выгрузка CSV, статистика.
"""
import uuid
import responses


class TestReportsAdvanced:
    """
    E2E Сценарии: Управление статусами и скачивание отчетов.
    """

    def test_01_send_utilisation_report(self, client, test_context, mock_api):
        """Шаг 1: Отправка отчета о нанесении (Case 27)."""
        report_id = str(uuid.uuid4())
        test_context.add("report_id", report_id)

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/send_utilisation",
                json={
                    "id": report_id,
                    "status": "pending",
                    "type": "utilisation"
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/report/send_utilisation",
            json={"work_shift_id": str(uuid.uuid4()), "inn": "1234567890"}
        )
        assert resp.status_code == 200
        print(f"[E2E-REP-ADV] Отчет о нанесении создан: {report_id}")

    def test_02_send_aggregation_report(self, client, test_context, mock_api):
        """Шаг 2: Отправка отчета об агрегации (Case 50)."""
        report_id = str(uuid.uuid4())
        test_context.add("agg_report_id", report_id)

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/send_aggregation",
                json={
                    "id": report_id,
                    "status": "pending",
                    "type": "aggregation"
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/report/send_aggregation",
            json={"id_agg_session": str(uuid.uuid4())}
        )
        assert resp.status_code == 200
        print(f"[E2E-REP-ADV] Отчет об агрегации создан: {report_id}")

    def test_03_filter_reports(self, client, test_context, mock_api):
        """Шаг 3: Фильтрация отчетов."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/filter",
                json={
                    "total_count": 10,
                    "result": [
                        {
                            "id": test_context.get_last("report_id"),
                            "type": "utilisation",
                            "status": "pending"
                        }
                    ]
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/report/filter",
            json={"status": "pending", "limit": 20, "offset": 0}
        )
        assert resp.status_code == 200
        print(f"[E2E-REP-ADV] Отчеты отфильтрованы")

    def test_04_resend_failed_report(self, client, test_context, mock_api):
        """Шаг 4: Повторная отправка отчета с ошибкой (Case 60)."""
        report_id = test_context.get_last("report_id")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/resend",
                json={
                    "id": report_id,
                    "status": "resent",
                    "message": "Report queued for resending"
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/report/resend",
            json={"id": report_id}
        )
        assert resp.status_code == 200
        print(f"[E2E-REP-ADV] Отчет {report_id} отправлен повторно")

    def test_05_set_manual_status(self, client, test_context, mock_api):
        """Шаг 5: Установка ручного статуса (Case 61)."""
        report_id = test_context.get_last("report_id")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/set_report_status",
                json={
                    "id": report_id,
                    "status": "processed_manually",
                    "previous_status": "error"
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/report/set_report_status",
            json={"id": report_id, "status": "processed_manually"}
        )
        assert resp.status_code == 200
        print(f"[E2E-REP-ADV] Статус отчета изменен вручную")

    def test_06_download_report_csv(self, client, test_context, mock_api):
        """Шаг 6: Скачивание отчета в формате CSV (Case 62)."""
        report_id = test_context.get_last("report_id")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/download",
                body="gtin,serial,status\n04600494009044,ABC123,ok\n",
                status=200,
                content_type="text/csv",
            )

        resp = client.post(
            "/api/web/v1/report/download",
            json={"id": report_id, "type": "circulation"}
        )
        assert resp.status_code == 200
        content_type = resp.headers.get("content-type", "")
        assert "csv" in content_type or "plain" in content_type
        print(f"[E2E-REP-ADV] CSV файл отчета получен")

    def test_07_download_aggregation_csv(self, client, test_context, mock_api):
        """Шаг 7: Скачивание отчета об агрегации в CSV."""
        report_id = test_context.get_last("agg_report_id")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/aggregation/download",
                body="parent_sscc,child_sscc,level\n037123456789012341,037123456789012340,1\n",
                status=200,
                content_type="text/csv",
            )

        resp = client.post(
            "/api/web/v1/report/aggregation/download",
            json={"id": report_id}
        )
        assert resp.status_code == 200
        print(f"[E2E-REP-ADV] CSV агрегации получен")

    def test_08_report_statistics(self, client, test_context, mock_api):
        """Шаг 8: Получение статистики по отчетам (Case 63)."""
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
                    "period": "2024-01-01/2024-01-31"
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/report/statistics",
            json={
                "date_from": "2024-01-01",
                "date_to": "2024-01-31"
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        print(f"[E2E-REP-ADV] Статистика: total={data.get('total')}, error={data.get('error')}")

    def test_09_download_excel(self, client, test_context, mock_api):
        """Шаг 9: Выгрузка всех отчетов в Excel."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/download_excel",
                body=b"PK\x03\x04 fake excel content",
                status=200,
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        resp = client.post(
            "/api/web/v1/report/download_excel",
            json={
                "date_from": "2024-01-01",
                "date_to": "2024-01-31",
                "report_types": ["utilisation", "circulation", "aggregation"]
            }
        )
        assert resp.status_code == 200
        print(f"[E2E-REP-ADV] Excel файл выгружен")

    def test_10_gis_check_code(self, client, test_context, mock_api):
        """Шаг 10: Проверка статуса КМ в ГИС (Case 64)."""
        report_id = test_context.get_last("report_id")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/gis/check_code",
                json={
                    "report_id": report_id,
                    "status": "checked",
                    "gis_status": "introduced",
                    "codes_checked": 100
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/report/gis/check_code",
            json={"id": report_id}
        )
        assert resp.status_code == 200
        print(f"[E2E-REP-ADV] Проверка ГИС выполнена")
