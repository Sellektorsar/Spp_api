"""
E2E Tests: Integration with 1C
Сценарий: обмен данными с системой 1С.

Шаги:
1. Настройка интеграции с 1С
2. Отправка данных о заказах в 1С
3. Получение данных о контрагентах из 1С
4. Синхронизация данных о продукции
5. Обработка ошибок синхронизации
6. Повторная попытка синхронизации
"""
import pytest
import responses
import uuid
import datetime
from typing import Dict, Any

from src.api.application.update import update as update_aggregation_integration
from src.api.line.create import create as create_line
from src.api.work_shift.start import start as start_shift
from src.api.aggregation_session.add import add as create_agg_session
from src.api.aggregation_session.finish import finish as start_agg_session
from src.api.work_shift.integration import update_work_shift_integration
from src.models import CreateInput, WorkShiftStart, LINETYPE, ProductGroup, ProductionType


@pytest.mark.e2e
@pytest.mark.order(9)
class TestIntegrationWith1C:
    """
    E2E Сценарий: Интеграция с системой 1С.
    """

    def test_01_setup_production_line_for_integration(self, client, test_context, mock_api):
        """Шаг 1: Создание производственной линии для тестов интеграции."""
        line_id = str(uuid.uuid4())
        line_number = 601
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/create",
                json={"id": line_id, "number": line_number},
                status=200,
            )

        payload = CreateInput(
            name="1C Integration Test Line",
            line_type=LINETYPE.integer_1,
            product_group=ProductGroup.milk,
            production_type=ProductionType.integer_1,
        )
        resp = create_line(client, body=payload)
        assert resp.status_code == 200
        data = resp.json()
        test_context.add("integration_line_number", data["number"])
        print(f"[E2E-1C] Линия для интеграции создана: {data['number']}")

    def test_02_start_work_shift_for_integration(self, client, test_context, mock_api):
        """Шаг 2: Запуск рабочей смены для тестов интеграции."""
        line_number = test_context.get_last("integration_line_number")
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
            batch="BATCH-1C-001",
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
        test_context.add("integration_shift_id", data["id"])
        print(f"[E2E-1C] Смена для интеграции запущена: {data['id']}")

    def test_03_create_aggregation_session_for_integration(self, client, test_context, mock_api):
        """Шаг 3: Создание сессии агрегации для тестов интеграции."""
        session_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/dashboard/create",
                json={"id": session_id, "name": "1C Integration Session"},
                status=200,
            )

        resp = create_agg_session(client, json={"name": "1C Integration Session"})
        assert resp.status_code == 200
        data = resp.json()
        test_context.add("integration_session_id", data["id"])
        print(f"[E2E-1C] Сессия агрегации для интеграции создана: {data['id']}")

    def test_04_update_aggregation_integration_positive(self, client, test_context, mock_api):
        """Шаг 4: Позитивный сценарий обновления интеграции агрегации с 1С."""
        session_id = test_context.get_last("integration_session_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/application/integration_with_1c/aggregation/update",
                json={
                    "session_id": session_id,
                    "status": "success",
                    "synced_at": datetime.datetime.now().isoformat(),
                    "packages_count": 10,
                    "pallets_count": 2
                },
                status=200,
            )

        integration_data = {
            "session_id": session_id,
            "auto_sync": True,
            "sync_interval": 300,  # 5 минут
            "include_packages": True,
            "include_pallets": True
        }
        
        resp = update_aggregation_integration(client, json=integration_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["session_id"] == session_id
        print(f"[E2E-1C] Интеграция агрегации обновлена: {session_id}")

    def test_05_update_aggregation_integration_negative_invalid_session(self, client, test_context, mock_api):
        """Шаг 5: Негативный сценарий - обновление с невалидным ID сессии."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/application/integration_with_1c/aggregation/update",
                json={"detail": "Session not found"},
                status=404,
            )

        integration_data = {
            "session_id": "00000000-0000-0000-0000-000000000000",  # Невалидный ID
            "auto_sync": True
        }
        
        resp = update_aggregation_integration(client, json=integration_data)
        assert resp.status_code == 404
        print(f"[E2E-1C] Негативный тест обновления агрегации: статус {resp.status_code}")

    def test_06_update_aggregation_integration_negative_connection_error(self, client, test_context, mock_api):
        """Шаг 6: Негативный сценарий - ошибка подключения к 1С."""
        session_id = test_context.get_last("integration_session_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/application/integration_with_1c/aggregation/update",
                json={"detail": "Connection to 1C failed"},
                status=503,
            )

        integration_data = {
            "session_id": session_id,
            "auto_sync": True,
            "force_sync": True
        }
        
        resp = update_aggregation_integration(client, json=integration_data)
        assert resp.status_code == 503
        print(f"[E2E-1C] Тест ошибки подключения к 1С: статус {resp.status_code}")

    def test_07_update_work_shift_integration_positive(self, client, test_context, mock_api):
        """Шаг 7: Позитивный сценарий обновления интеграции рабочей смены с 1С."""
        shift_id = test_context.get_last("integration_shift_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/application/integration_with_1c/work_shift/update",
                json={
                    "shift_id": shift_id,
                    "status": "success",
                    "synced_at": datetime.datetime.now().isoformat(),
                    "codes_count": 50,
                    "batch_number": "BATCH-1C-001"
                },
                status=200,
            )

        integration_data = {
            "shift_id": shift_id,
            "auto_sync": True,
            "sync_interval": 600,  # 10 минут
            "include_codes": True,
            "include_batch_info": True
        }
        
        resp = update_work_shift_integration(client, json=integration_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "success"
        assert data["shift_id"] == shift_id
        print(f"[E2E-1C] Интеграция рабочей смены обновлена: {shift_id}")

    def test_08_update_work_shift_integration_negative_invalid_shift(self, client, test_context, mock_api):
        """Шаг 8: Негативный сценарий - обновление с невалидным ID смены."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/application/integration_with_1c/work_shift/update",
                json={"detail": "Work shift not found"},
                status=404,
            )

        integration_data = {
            "shift_id": "00000000-0000-0000-0000-000000000000",  # Невалидный ID
            "auto_sync": True
        }
        
        resp = update_work_shift_integration(client, json=integration_data)
        assert resp.status_code == 404
        print(f"[E2E-1C] Негативный тест обновления смены: статус {resp.status_code}")

    def test_09_update_work_shift_integration_negative_data_mismatch(self, client, test_context, mock_api):
        """Шаг 9: Негативный сценарий - несоответствие данных при синхронизации."""
        shift_id = test_context.get_last("integration_shift_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/application/integration_with_1c/work_shift/update",
                json={"detail": "Data mismatch between systems"},
                status=409,
            )

        integration_data = {
            "shift_id": shift_id,
            "auto_sync": True,
            "force_sync": True,
            "expected_batch": "DIFFERENT_BATCH"  # Несоответствующий номер партии
        }
        
        resp = update_work_shift_integration(client, json=integration_data)
        assert resp.status_code == 409
        print(f"[E2E-1C] Тест несоответствия данных: статус {resp.status_code}")

    def test_10_boundary_test_frequent_sync_intervals(self, client, test_context, mock_api):
        """Шаг 10: Граничный тест - слишком частые интервалы синхронизации."""
        session_id = test_context.get_last("integration_session_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/application/integration_with_1c/aggregation/update",
                json={"detail": "Sync interval too short (minimum: 60 seconds)"},
                status=400,
            )

        integration_data = {
            "session_id": session_id,
            "auto_sync": True,
            "sync_interval": 30  # Слишком частый интервал
        }
        
        resp = update_aggregation_integration(client, json=integration_data)
        assert resp.status_code == 400
        print(f"[E2E-1C] Граничный тест частой синхронизации: статус {resp.status_code}")

    def test_11_boundary_test_large_data_sync(self, client, test_context, mock_api):
        """Шаг 11: Граничный тест - синхронизация большого объема данных."""
        shift_id = test_context.get_last("integration_shift_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/application/integration_with_1c/work_shift/update",
                json={
                    "shift_id": shift_id,
                    "status": "success",
                    "synced_at": datetime.datetime.now().isoformat(),
                    "codes_count": 10000,
                    "processing_time": 45.2
                },
                status=200,
            )

        integration_data = {
            "shift_id": shift_id,
            "auto_sync": True,
            "batch_size": 1000,  # Большой размер пакета
            "max_retries": 5
        }
        
        resp = update_work_shift_integration(client, json=integration_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["codes_count"] == 10000
        print(f"[E2E-1C] Граничный тест большого объема данных: {data['codes_count']} кодов")

    def test_12_error_test_timeout_1c_connection(self, client, test_context, mock_api):
        """Шаг 12: Тест обработки ошибок - таймаут подключения к 1С."""
        session_id = test_context.get_last("integration_session_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/application/integration_with_1c/aggregation/update",
                json={"detail": "Connection timeout to 1C server"},
                status=408,
            )

        integration_data = {
            "session_id": session_id,
            "auto_sync": True,
            "timeout": 5  # Короткий таймаут
        }
        
        resp = update_aggregation_integration(client, json=integration_data)
        assert resp.status_code == 408
        print(f"[E2E-1C] Тест таймаута подключения: статус {resp.status_code}")

    def test_13_error_test_authentication_1c_failure(self, client, test_context, mock_api):
        """Шаг 13: Тест обработки ошибок - ошибка аутентификации в 1С."""
        shift_id = test_context.get_last("integration_shift_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/application/integration_with_1c/work_shift/update",
                json={"detail": "Authentication failed for 1C system"},
                status=401,
            )

        integration_data = {
            "shift_id": shift_id,
            "auto_sync": True,
            "credentials": {
                "username": "wrong_user",
                "password": "wrong_password"
            }
        }
        
        resp = update_work_shift_integration(client, json=integration_data)
        assert resp.status_code == 401
        print(f"[E2E-1C] Тест ошибки аутентификации: статус {resp.status_code}")

    def test_14_error_test_permission_denied_1c(self, client, test_context, mock_api):
        """Шаг 14: Тест обработки ошибок - отказ в доступе к 1С."""
        session_id = test_context.get_last("integration_session_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/application/integration_with_1c/aggregation/update",
                json={"detail": "Permission denied in 1C system"},
                status=403,
            )

        integration_data = {
            "session_id": session_id,
            "auto_sync": True,
            "access_level": "admin"  # Требуемый уровень доступа
        }
        
        resp = update_aggregation_integration(client, json=integration_data)
        assert resp.status_code == 403
        print(f"[E2E-1C] Тест отказа в доступе: статус {resp.status_code}")

    def test_15_retry_mechanism_after_failure(self, client, test_context, mock_api):
        """Шаг 15: Тест механизма повторных попыток после сбоя."""
        session_id = test_context.get_last("integration_session_id")
        
        # Первая попытка - ошибка
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/application/integration_with_1c/aggregation/update",
                json={"detail": "Temporary connection issue"},
                status=503,
            )

        integration_data = {
            "session_id": session_id,
            "auto_sync": True,
            "retry_count": 1
        }
        
        resp = update_aggregation_integration(client, json=integration_data)
        assert resp.status_code == 503
        
        # Вторая попытка - успех
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/application/integration_with_1c/aggregation/update",
                json={
                    "session_id": session_id,
                    "status": "success",
                    "synced_at": datetime.datetime.now().isoformat(),
                    "retry_attempt": 2
                },
                status=200,
            )

        integration_data["retry_count"] = 2
        resp = update_aggregation_integration(client, json=integration_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["retry_attempt"] == 2
        print(f"[E2E-1C] Механизм повторных попыток: успешен после 2 попыток")

    def test_16_cleanup_integration_data(self, client, test_context, mock_api):
        """Шаг 16: Очистка - отключение интеграции для тестовых данных."""
        session_id = test_context.get_last("integration_session_id")
        shift_id = test_context.get_last("integration_shift_id")
        
        # Отключение интеграции для сессии
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/application/integration_with_1c/aggregation/update",
                json={
                    "session_id": session_id,
                    "status": "disabled",
                    "disabled_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        integration_data = {
            "session_id": session_id,
            "auto_sync": False,
            "enabled": False
        }
        
        resp = update_aggregation_integration(client, json=integration_data)
        assert resp.status_code == 200
        
        # Отключение интеграции для смены
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/application/integration_with_1c/work_shift/update",
                json={
                    "shift_id": shift_id,
                    "status": "disabled",
                    "disabled_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        integration_data = {
            "shift_id": shift_id,
            "auto_sync": False,
            "enabled": False
        }
        
        resp = update_work_shift_integration(client, json=integration_data)
        assert resp.status_code == 200
        
        print(f"[E2E-1C] Интеграция отключена для очистки тестовых данных")