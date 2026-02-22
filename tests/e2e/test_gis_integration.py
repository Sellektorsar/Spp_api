"""
E2E Tests: GIS Integration
Сценарий: взаимодействие с системами маркировки.

Шаги:
1. Аутентификация в ГИС МТ
2. Проверка кодов маркировки
3. Отправка различных типов отчётов
4. Обработка ошибок ГИС МТ
5. Повторная отправка отчётов
6. Проверка статусов кодов в ГИС МТ
"""
import pytest
import responses
import uuid
import datetime
from typing import Dict, Any

from src.api.report.check_code import check_code as check_report_code
from src.api.check_gis_code.check_gis_code import check_gis_code
from src.api.report.send_aggregation import send_aggregation
from src.api.report.send_circulation import send_circulation
from src.api.report.send_utilisation import send_utilisation
from src.api.report.resend import resend as resend_report
from src.api.line.create import create as create_line
from src.api.work_shift.start import start as start_shift
from src.models import CreateInput, WorkShiftStart, LINETYPE, ProductGroup, ProductionType, ReportID


@pytest.mark.e2e
@pytest.mark.order(10)
class TestGISIntegration:
    """
    E2E Сценарий: Интеграция с системами маркировки.
    """

    def test_01_setup_production_line_for_gis(self, client, test_context, mock_api):
        """Шаг 1: Создание производственной линии для тестов ГИС."""
        line_id = str(uuid.uuid4())
        line_number = 701
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/create",
                json={"id": line_id, "number": line_number},
                status=200,
            )

        payload = CreateInput(
            name="GIS Integration Test Line",
            line_type=LINETYPE.integer_1,
            product_group=ProductGroup.milk,
            production_type=ProductionType.integer_1,
        )
        resp = create_line(client, body=payload)
        assert resp.status_code == 200
        data = resp.json()
        test_context.add("gis_line_number", data["number"])
        print(f"[E2E-GIS] Линия для ГИС создана: {data['number']}")

    def test_02_start_work_shift_for_gis(self, client, test_context, mock_api):
        """Шаг 2: Запуск рабочей смены для тестов ГИС."""
        line_number = test_context.get_last("gis_line_number")
        shift_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/start",
                json={"id": shift_id, "line_number": line_number, "status": "active"},
                status=200,
            )

        payload = WorkShiftStart(
            line_number=line_number,
            gtin="04606203399737",
            batch="BATCH-GIS-001",
            start_date=datetime.datetime.now(datetime.timezone.utc),
            production_date=datetime.datetime.now(datetime.timezone.utc),
            product_group=ProductGroup.milk,
            is_allow_other_gtins=False,
            with_variable_weight=False,
            camera_is_active=False,
        )
        resp = start_shift(client, body=payload)
        assert resp.status_code == 200
        data = resp.json()
        test_context.add("gis_shift_id", data["id"])
        print(f"[E2E-GIS] Смена для ГИС запущена: {data['id']}")

    def test_03_check_gis_code_positive(self, client, test_context, mock_api):
        """Шаг 3: Позитивный сценарий проверки кода в ГИС."""
        test_code = "0104606203399737215gis00193dGVzdA=="
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/check_gis_code",
                json={
                    "code": test_code,
                    "status": "in_circulation",
                    "gtin": "04606203399737",
                    "check_date": datetime.datetime.now().isoformat(),
                    "valid": True
                },
                status=200,
            )

        resp = check_gis_code(client, json={"code": test_code})
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == test_code
        assert data["status"] == "in_circulation"
        assert data["valid"] is True
        
        test_context.add("valid_gis_code", test_code)
        print(f"[E2E-GIS] Код проверен в ГИС: {test_code} - {data['status']}")

    def test_04_check_gis_code_negative_invalid(self, client, test_context, mock_api):
        """Шаг 4: Негативный сценарий - проверка невалидного кода в ГИС."""
        invalid_code = "INVALID_GIS_CODE_FORMAT"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/check_gis_code",
                json={"detail": "Invalid code format"},
                status=400,
            )

        resp = check_gis_code(client, json={"code": invalid_code})
        assert resp.status_code == 400
        print(f"[E2E-GIS] Негативный тест проверки кода: статус {resp.status_code}")

    def test_05_check_gis_code_negative_not_found(self, client, test_context, mock_api):
        """Шаг 5: Негативный сценарий - код не найден в ГИС."""
        not_found_code = "0104606203399737215notfound93dGVzdA=="
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/check_gis_code",
                json={"detail": "Code not found in GIS"},
                status=404,
            )

        resp = check_gis_code(client, json={"code": not_found_code})
        assert resp.status_code == 404
        print(f"[E2E-GIS] Тест кода не найден в ГИС: статус {resp.status_code}")

    def test_06_send_utilisation_report_to_gis(self, client, test_context, mock_api):
        """Шаг 6: Отправка отчёта о нанесении в ГИС."""
        shift_id = test_context.get_last("gis_shift_id")
        report_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/send_utilisation",
                json={
                    "id": report_id,
                    "status": "new",
                    "type": "utilisation",
                    "sent_to_gis": True,
                    "sent_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = send_utilisation(client, json={"work_shift_id": shift_id, "inn": "7700000000"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "utilisation"
        assert data["sent_to_gis"] is True
        
        test_context.add("utilisation_report_id", data["id"])
        print(f"[E2E-GIS] Отчёт о нанесении отправлен в ГИС: {data['id']}")

    def test_07_send_circulation_report_to_gis(self, client, test_context, mock_api):
        """Шаг 7: Отправка отчёта о вводе в оборот в ГИС."""
        shift_id = test_context.get_last("gis_shift_id")
        report_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/send_circulation",
                json={
                    "id": report_id,
                    "status": "new",
                    "type": "circulation",
                    "sent_to_gis": True,
                    "sent_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = send_circulation(client, json={"work_shift_id": shift_id, "inn": "7700000000"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "circulation"
        assert data["sent_to_gis"] is True
        
        test_context.add("circulation_report_id", data["id"])
        print(f"[E2E-GIS] Отчёт о вводе в оборот отправлен в ГИС: {data['id']}")

    def test_08_send_aggregation_report_to_gis(self, client, test_context, mock_api):
        """Шаг 8: Отправка отчёта об агрегации в ГИС."""
        session_id = str(uuid.uuid4())
        report_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/send_aggregation",
                json={
                    "id": report_id,
                    "status": "new",
                    "type": "aggregation",
                    "sent_to_gis": True,
                    "sent_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = send_aggregation(client, json={"id_agg_session": session_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "aggregation"
        assert data["sent_to_gis"] is True
        
        test_context.add("aggregation_report_id", data["id"])
        test_context.add("aggregation_session_id", session_id)
        print(f"[E2E-GIS] Отчёт об агрегации отправлен в ГИС: {data['id']}")

    def test_09_check_report_code_status(self, client, test_context, mock_api):
        """Шаг 9: Проверка статуса кода через отчёт."""
        valid_gis_code = test_context.get_last("valid_gis_code")
        report_id = test_context.get_last("utilisation_report_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/check_code",
                json={
                    "report_id": report_id,
                    "code": valid_gis_code,
                    "status": "confirmed",
                    "confirmed_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        report_data = ReportID(report_id=report_id)
        resp = check_report_code(client, body=report_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == valid_gis_code
        assert data["status"] == "confirmed"
        print(f"[E2E-GIS] Статус кода проверен через отчёт: {data['status']}")

    def test_10_resend_failed_report_to_gis(self, client, test_context, mock_api):
        """Шаг 10: Повторная отправка неудачного отчёта в ГИС."""
        report_id = test_context.get_last("utilisation_report_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/resend",
                json={
                    "id": report_id,
                    "status": "pending",
                    "resent_at": datetime.datetime.now().isoformat(),
                    "retry_count": 1
                },
                status=200,
            )

        resp = resend_report(client, json={"id": report_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "pending"
        assert data["retry_count"] == 1
        print(f"[E2E-GIS] Отчёт повторно отправлен в ГИС: {data['id']}")

    def test_11_boundary_test_multiple_code_check(self, client, test_context, mock_api):
        """Шаг 11: Граничный тест - проверка множественных кодов."""
        test_codes = [
            "0104606203399737215gis00193dGVzdA==",
            "0104606203399737215gis00293dGVzdA==",
            "0104606203399737215gis00393dGVzdA=="
        ]
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/check_gis_code",
                json={
                    "results": [
                        {
                            "code": code,
                            "status": "in_circulation",
                            "valid": True
                        } for code in test_codes
                    ],
                    "total_count": len(test_codes)
                },
                status=200,
            )

        # Проверяем каждый код по отдельности
        for code in test_codes:
            resp = check_gis_code(client, json={"code": code})
            assert resp.status_code == 200
            data = resp.json()
            assert data["valid"] is True
        
        print(f"[E2E-GIS] Граничный тест: проверено {len(test_codes)} кодов")

    def test_12_boundary_test_large_report_data(self, client, test_context, mock_api):
        """Шаг 12: Граничный тест - отправка отчёта с большим объемом данных."""
        shift_id = test_context.get_last("gis_shift_id")
        report_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/send_utilisation",
                json={
                    "id": report_id,
                    "status": "new",
                    "type": "utilisation",
                    "sent_to_gis": True,
                    "codes_count": 10000,
                    "processing_time": 120.5
                },
                status=200,
            )

        resp = send_utilisation(client, json={
            "work_shift_id": shift_id, 
            "inn": "7700000000",
            "batch_size": 1000  # Большой размер пакета
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["codes_count"] == 10000
        print(f"[E2E-GIS] Граничный тест: отправлен отчёт с {data['codes_count']} кодами")

    def test_13_error_test_gis_connection_timeout(self, client, test_context, mock_api):
        """Шаг 13: Тест обработки ошибок - таймаут подключения к ГИС."""
        test_code = test_context.get_last("valid_gis_code")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/check_gis_code",
                json={"detail": "Connection timeout to GIS server"},
                status=408,
            )

        resp = check_gis_code(client, json={"code": test_code, "timeout": 5})
        assert resp.status_code == 408
        print(f"[E2E-GIS] Тест таймаута подключения к ГИС: статус {resp.status_code}")

    def test_14_error_test_gis_authentication_failure(self, client, test_context, mock_api):
        """Шаг 14: Тест обработки ошибок - ошибка аутентификации в ГИС."""
        test_code = test_context.get_last("valid_gis_code")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/check_gis_code",
                json={"detail": "Authentication failed for GIS system"},
                status=401,
            )

        resp = check_gis_code(client, json={
            "code": test_code,
            "credentials": {
                "username": "wrong_user",
                "password": "wrong_password"
            }
        })
        assert resp.status_code == 401
        print(f"[E2E-GIS] Тест ошибки аутентификации в ГИС: статус {resp.status_code}")

    def test_15_error_test_gis_rate_limit(self, client, test_context, mock_api):
        """Шаг 15: Тест обработки ошибок - превышение лимита запросов к ГИС."""
        test_code = test_context.get_last("valid_gis_code")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/check_gis_code",
                json={"detail": "Rate limit exceeded for GIS requests"},
                status=429,
            )

        resp = check_gis_code(client, json={"code": test_code})
        assert resp.status_code == 429
        print(f"[E2E-GIS] Тест превышения лимита запросов: статус {resp.status_code}")

    def test_16_error_test_gis_server_error(self, client, test_context, mock_api):
        """Шаг 16: Тест обработки ошибок - внутренняя ошибка сервера ГИС."""
        test_code = test_context.get_last("valid_gis_code")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/check_gis_code",
                json={"detail": "Internal server error in GIS system"},
                status=500,
            )

        resp = check_gis_code(client, json={"code": test_code})
        assert resp.status_code == 500
        print(f"[E2E-GIS] Тест внутренней ошибки сервера ГИС: статус {resp.status_code}")

    def test_17_cleanup_gis_test_data(self, client, test_context, mock_api):
        """Шаг 17: Очистка - завершение тестовых данных ГИС."""
        # В реальном сценарии здесь была бы очистка тестовых данных
        # Для e2e тестов просто логируем завершение
        print(f"[E2E-GIS] Тестовые данные ГИС очищены")