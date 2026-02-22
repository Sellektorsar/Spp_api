"""
E2E Tests: Bulk Operations
Сценарий: работа с большими объёмами данных.

Шаги:
1. Создание заказа на большое количество кодов
2. Пакетная обработка кодов
3. Отправка больших объёмов отчётов
4. Обработка ошибок при больших объёмах
5. Проверка производительности
6. Оптимизация запросов
"""
import pytest
import responses
import uuid
import datetime
from typing import Dict, Any

from src.api.network_proxy.orders import orders as create_bulk_order
from src.api.network_proxy.approve import approve as approve_bulk_order
from src.api.report.send_circulation_bulk import send_circulation_bulk as send_bulk_circulation
from src.api.report.send_utilisation_bulk import send_utilisation_bulk as send_bulk_utilisation
from src.api.line.create import create as create_line
from src.api.work_shift.start import start as start_shift
from src.api.work_shift.add_code import add_code as add_code_to_shift
from src.api.work_shift.finish import finish as finish_shift
from src.models import CreateInput, WorkShiftStart, WorkShiftCodeWithVariableWeight, LINETYPE, ProductGroup, ProductionType


@pytest.mark.e2e
@pytest.mark.order(12)
class TestBulkOperations:
    """
    E2E Сценарий: Работа с большими объёмами данных.
    """

    def test_01_create_bulk_order_positive(self, client, test_context, mock_api):
        """Шаг 1: Позитивный сценарий создания заказа на большое количество кодов."""
        order_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/network_proxy/api/network/v1/orders",
                json={
                    "id": order_id,
                    "status": "created",
                    "gtin": "04606203399737",
                    "quantity": 10000,
                    "created_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = create_bulk_order(
            client,
            json={
                "gtin": "04606203399737",
                "quantity": 10000,
                "serviceProviderId": str(uuid.uuid4())
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["quantity"] == 10000
        
        test_context.add("bulk_order_id", data["id"])
        print(f"[E2E-BULK] Заказ на большое количество кодов создан: {data['id']}")

    def test_02_approve_bulk_order_positive(self, client, test_context, mock_api):
        """Шаг 2: Позитивный сценарий подтверждения заказа на большое количество кодов."""
        order_id = test_context.get_last("bulk_order_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/network_proxy/api/network/v1/orders/approve",
                json={
                    "id": order_id,
                    "status": "approved",
                    "approved_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = approve_bulk_order(
            client,
            json={"id": order_id}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "approved"
        print(f"[E2E-BULK] Заказ на большое количество кодов подтвержден: {order_id}")

    def test_03_create_production_line_for_bulk(self, client, test_context, mock_api):
        """Шаг 3: Создание производственной линии для обработки больших объёмов."""
        line_id = str(uuid.uuid4())
        line_number = 901
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/create",
                json={"id": line_id, "number": line_number},
                status=200,
            )

        payload = CreateInput(
            name="Bulk Operations Test Line",
            line_type=LINETYPE.integer_1,
            product_group=ProductGroup.milk,
            production_type=ProductionType.integer_1,
        )
        resp = create_line(client, body=payload)
        assert resp.status_code == 200
        data = resp.json()
        test_context.add("bulk_line_number", data["number"])
        print(f"[E2E-BULK] Линия для больших объёмов создана: {data['number']}")

    def test_04_start_shift_for_bulk(self, client, test_context, mock_api):
        """Шаг 4: Запуск рабочей смены для обработки больших объёмов."""
        line_number = test_context.get_last("bulk_line_number")
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
            batch="BATCH-BULK-001",
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
        test_context.add("bulk_shift_id", data["id"])
        print(f"[E2E-BULK] Смена для больших объёмов запущена: {data['id']}")

    def test_05_add_bulk_codes_to_shift(self, client, test_context, mock_api):
        """Шаг 5: Добавление большого количества кодов в смену."""
        line_number = test_context.get_last("bulk_line_number")
        shift_id = test_context.get_last("bulk_shift_id")
        
        # Добавляем 1000 кодов
        bulk_codes = [f"0104606203399737215bulk{i:04d}93dGVzdA==" for i in range(1000)]
        test_context.add("bulk_codes", bulk_codes)
        
        for i, code in enumerate(bulk_codes[:100]):  # Добавляем первые 100 кодов для теста
            if mock_api:
                mock_api.add(
                    responses.POST,
                    f"{client.base_url}/api/web/v1/work_shift/add_code",
                    json={"status": "added"},
                    status=200,
                )

            code_data = WorkShiftCodeWithVariableWeight(
                line_number=line_number,
                code=code
            )
            resp = add_code_to_shift(client, body=code_data)
            assert resp.status_code == 200
        
        print(f"[E2E-BULK] Добавлено {min(100, len(bulk_codes))} кодов в смену")

    def test_06_add_bulk_codes_negative_invalid_format(self, client, test_context, mock_api):
        """Шаг 6: Негативный сценарий - добавление кодов с невалидным форматом."""
        line_number = test_context.get_last("bulk_line_number")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/add_code",
                json={"detail": "Invalid code format"},
                status=400,
            )

        # Код с невалидным форматом
        invalid_code = "INVALID_BULK_CODE_FORMAT"
        code_data = WorkShiftCodeWithVariableWeight(
                line_number=line_number,
                code=invalid_code
            )
        resp = add_code_to_shift(client, body=code_data)
        assert resp.status_code == 400
        print(f"[E2E-BULK] Негативный тест добавления кода: статус {resp.status_code}")

    def test_07_send_bulk_circulation_report(self, client, test_context, mock_api):
        """Шаг 7: Отправка отчёта о вводе в оборот с большим количеством кодов."""
        shift_id = test_context.get_last("bulk_shift_id")
        report_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/send_circulation_bulk",
                json={
                    "id": report_id,
                    "status": "new",
                    "type": "circulation",
                    "sent_at": datetime.datetime.now().isoformat(),
                    "codes_count": 1000
                },
                status=200,
            )

        resp = send_bulk_circulation(
            client,
            json={
                "work_shift_id": shift_id,
                "inn": "7700000000"
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["codes_count"] == 1000
        
        test_context.add("bulk_circulation_report_id", data["id"])
        print(f"[E2E-BULK] Отчёт о вводе в оборот отправлен: {data['id']}")

    def test_08_send_bulk_utilisation_report(self, client, test_context, mock_api):
        """Шаг 8: Отправка отчёта о нанесении с большим количеством кодов."""
        shift_id = test_context.get_last("bulk_shift_id")
        report_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/send_utilisation_bulk",
                json={
                    "id": report_id,
                    "status": "new",
                    "type": "utilisation",
                    "sent_at": datetime.datetime.now().isoformat(),
                    "codes_count": 1000
                },
                status=200,
            )

        resp = send_bulk_utilisation(
            client,
            json={
                "work_shift_id": shift_id,
                "inn": "7700000000"
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["codes_count"] == 1000
        
        test_context.add("bulk_utilisation_report_id", data["id"])
        print(f"[E2E-BULK] Отчёт о нанесении отправлен: {data['id']}")

    def test_09_boundary_test_large_bulk_order(self, client, test_context, mock_api):
        """Шаг 9: Граничный тест - очень большой заказ."""
        order_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/network_proxy/api/network/v1/orders",
                json={
                    "id": order_id,
                    "status": "created",
                    "gtin": "04606203399737",
                    "quantity": 100000,  # Очень большое количество
                    "created_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = create_bulk_order(
            client,
            json={
                "gtin": "04606203399737",
                "quantity": 100000,
                "serviceProviderId": str(uuid.uuid4())
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["quantity"] == 100000
        print(f"[E2E-BULK] Граничный тест: создан заказ на {data['quantity']} кодов")

    def test_10_boundary_test_large_bulk_codes(self, client, test_context, mock_api):
        """Шаг 10: Граничный тест - добавление очень большого количества кодов."""
        line_number = test_context.get_last("bulk_line_number")
        shift_id = test_context.get_last("bulk_shift_id")
        
        # Добавляем 10000 кодов
        large_bulk_codes = [f"0104606203399737215large{i:05d}93dGVzdA==" for i in range(10000)]
        
        # Добавляем только первые 100 кодов для теста производительности
        for i, code in enumerate(large_bulk_codes[:100]):
            if mock_api:
                mock_api.add(
                    responses.POST,
                    f"{client.base_url}/api/web/v1/work_shift/add_code",
                    json={"status": "added"},
                    status=200,
                )

            code_data = WorkShiftCodeWithVariableWeight(
                line_number=line_number,
                code=code
            )
            resp = add_code_to_shift(client, body=code_data)
            assert resp.status_code == 200
        
        print(f"[E2E-BULK] Граничный тест: добавлено {min(100, len(large_bulk_codes))} кодов")

    def test_11_boundary_test_timeout_bulk_operation(self, client, test_context, mock_api):
        """Шаг 11: Граничный тест - таймаут при больших объёмах."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/send_circulation_bulk",
                json={"detail": "Request timeout due to large data size"},
                status=408,
            )

        resp = send_bulk_circulation(
            client,
            json={
                "work_shift_id": test_context.get_last("bulk_shift_id"),
                "inn": "7700000000",
                "timeout": 1  # Короткий таймаут
            }
        )
        assert resp.status_code == 408
        print(f"[E2E-BULK] Граничный тест: таймаут при больших объёмах: статус {resp.status_code}")

    def test_12_error_test_memory_limit_bulk_operation(self, client, test_context, mock_api):
        """Шаг 12: Тест обработки ошибок - превышение лимита памяти."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/send_utilisation_bulk",
                json={"detail": "Memory limit exceeded"},
                status=507,
            )

        resp = send_bulk_utilisation(
            client,
            json={
                "work_shift_id": test_context.get_last("bulk_shift_id"),
                "inn": "7700000000",
                "batch_size": 100000  # Очень большой размер пакета
            }
        )
        assert resp.status_code == 507
        print(f"[E2E-BULK] Тест превышения лимита памяти: статус {resp.status_code}")

    def test_13_error_test_rate_limit_bulk_operation(self, client, test_context, mock_api):
        """Шаг 13: Тест обработки ошибок - превышение лимита запросов."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/send_circulation_bulk",
                json={"detail": "Rate limit exceeded for bulk operations"},
                status=429,
            )

        resp = send_bulk_circulation(
            client,
            json={
                "work_shift_id": test_context.get_last("bulk_shift_id"),
                "inn": "7700000000"
            }
        )
        assert resp.status_code == 429
        print(f"[E2E-BULK] Тест превышения лимита запросов: статус {resp.status_code}")

    def test_14_performance_test_bulk_codes_addition(self, client, test_context, mock_api):
        """Шаг 14: Тест производительности - добавление большого количества кодов."""
        line_number = test_context.get_last("bulk_line_number")
        shift_id = test_context.get_last("bulk_shift_id")
        
        # Измеряем время добавления 1000 кодов
        import time
        start_time = time.time()
        
        for i in range(1000):
            code = f"0104606203399737215perf{i:05d}93dGVzdA=="
            code_data = WorkShiftCodeWithVariableWeight(
                line_number=line_number,
                code=code
            )
            resp = add_code_to_shift(client, body=code_data)
            assert resp.status_code == 200
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Проверяем, что операция не занимает слишком много времени
        assert duration < 60, f"Добавление 1000 кодов заняло слишком много времени: {duration}с"
        
        print(f"[E2E-BULK] Тест производительности: добавлено 1000 кодов за {duration:.2f}с")

    def test_15_optimization_test_batch_processing(self, client, test_context, mock_api):
        """Шаг 15: Тест оптимизации - пакетная обработка кодов."""
        line_number = test_context.get_last("bulk_line_number")
        shift_id = test_context.get_last("bulk_shift_id")
        
        # Создаем 1000 кодов для пакетной обработки
        batch_codes = [f"0104606203399737215batch{i:03d}93dGVzdA==" for i in range(1000)]
        
        # Разделяем на пакеты по 100 кодов
        batch_size = 100
        for batch_start in range(0, len(batch_codes), batch_size):
            batch = batch_codes[batch_start:batch_start + batch_size]
            
            for code in batch:
                if mock_api:
                    mock_api.add(
                        responses.POST,
                        f"{client.base_url}/api/web/v1/work_shift/add_code",
                        json={"status": "added"},
                        status=200,
                    )

                code_data = WorkShiftCodeWithVariableWeight(
                    line_number=line_number,
                    code=code
                )
                resp = add_code_to_shift(client, body=code_data)
                assert resp.status_code == 200
        
        print(f"[E2E-BULK] Тест оптимизации: обработано {len(batch_codes)} кодов пакетами по {batch_size}")

    def test_16_cleanup_bulk_test_data(self, client, test_context, mock_api):
        """Шаг 16: Очистка - завершение смены с большим количеством кодов."""
        line_number = test_context.get_last("bulk_line_number")
        shift_id = test_context.get_last("bulk_shift_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/finish",
                json={
                    "id": shift_id,
                    "status": "finished",
                    "finished_at": datetime.datetime.now().isoformat(),
                    "total_codes": 1100  # 1000 нормальных + 100 тестовых
                },
                status=200,
            )

        resp = finish_shift(client, json={"id": shift_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "finished"
        
        print(f"[E2E-BULK] Тестовые данные больших объёмов очищены")