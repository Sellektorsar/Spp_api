"""
E2E Tests: Shipment Process
Сценарий: процесс отгрузки продукции.

Шаги:
1. Создание отгрузки
2. Добавление SSCC кодов
3. Формирование транспортной упаковки
4. Завершение отгрузки
5. Отправка отчёта об отгрузке
6. Отмена отгрузки (если необходимо)
"""
import pytest
import responses
import uuid
import datetime
from typing import Dict, Any

from src.api.shipment.start import start as start_shipment
from src.api.shipment.add_sscc import add_sscc
from src.api.shipment.filter import filter as filter_shipments
from src.api.shipment.get_detail_info import get_detail_info
from src.api.shipment.finish import finish as finish_shipment
from src.api.shipment.resume import resume as resume_shipment
from src.api.shipment.active import active as get_active_shipment
from src.api.shipment.delete import delete as delete_shipment
from src.api.shipment.download import download as download_shipment
from src.api.line.create import create as create_line
from src.models import ShipmentStartInput, ShipmentAddPackage, ShipmentFinish, CreateInput, LINETYPE, ProductGroup, ProductionType


@pytest.mark.e2e
@pytest.mark.order(7)
class TestShipmentProcess:
    """
    E2E Сценарий: Полный цикл процесса отгрузки продукции.
    """

    def test_01_create_production_line_for_shipment(self, client, test_context, mock_api):
        """Шаг 1: Создание производственной линии для отгрузки."""
        line_id = str(uuid.uuid4())
        line_number = 401
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/create",
                json={"id": line_id, "number": line_number},
                status=200,
            )

        payload = CreateInput(
            name="Shipment Test Line",
            line_type=LINETYPE.integer_1,
            product_group=ProductGroup.milk,
            production_type=ProductionType.integer_1,
        )
        resp = create_line(client, body=payload)
        assert resp.status_code == 200
        data = resp.json()
        test_context.add("shipment_line_number", data["number"])
        print(f"[E2E-SHIPMENT] Линия для отгрузки создана: {data['number']}")

    def test_02_start_shipment_positive(self, client, test_context, mock_api):
        """Шаг 2: Позитивный сценарий начала отгрузки."""
        line_number = test_context.get_last("shipment_line_number")
        shipment_id = str(uuid.uuid4())
        shipment_name = f"SHIPMENT_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/start",
                json={
                    "id": shipment_id,
                    "line_number": line_number,
                    "name": shipment_name,
                    "status": "active",
                    "start_date": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        shipment_data = ShipmentStartInput(
            line_number=line_number,
            name=shipment_name,
            start_date=datetime.datetime.now().isoformat(),
            read_type="manual",  # Предполагаемое значение
            product_group=ProductGroup.milk
        )
        
        resp = start_shipment(client, body=shipment_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["line_number"] == line_number
        assert data["status"] == "active"
        
        test_context.add("shipment_id", data["id"])
        test_context.add("shipment_name", shipment_name)
        print(f"[E2E-SHIPMENT] Отгрузка начата: {shipment_name} (ID: {data['id']})")

    def test_03_start_shipment_negative_invalid_line(self, client, test_context, mock_api):
        """Шаг 3: Негативный сценарий - начало отгрузки с невалидной линией."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/start",
                json={"detail": "Line not found or inactive"},
                status=400,
            )

        shipment_data = ShipmentStartInput(
            line_number=99999,  # Несуществующая линия
            name="Invalid Shipment",
            start_date=datetime.datetime.now().isoformat(),
            read_type="manual",
            product_group=ProductGroup.milk
        )
        
        resp = start_shipment(client, body=shipment_data)
        assert resp.status_code == 400
        print(f"[E2E-SHIPMENT] Негативный тест начала отгрузки: статус {resp.status_code}")

    def test_04_get_active_shipment(self, client, test_context, mock_api):
        """Шаг 4: Получение активной отгрузки."""
        line_number = test_context.get_last("shipment_line_number")
        shipment_id = test_context.get_last("shipment_id")
        
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/shipment/active",
                json={
                    "id": shipment_id,
                    "line_number": line_number,
                    "name": test_context.get_last("shipment_name"),
                    "status": "active",
                    "sscc_count": 0
                },
                status=200,
            )

        resp = get_active_shipment(client, params={"line_number": line_number})
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == shipment_id
        assert data["status"] == "active"
        print(f"[E2E-SHIPMENT] Активная отгрузка получена: {data['name']}")

    def test_05_add_first_sscc_positive(self, client, test_context, mock_api):
        """Шаг 5: Позитивный сценарий добавления первого SSCC."""
        line_number = test_context.get_last("shipment_line_number")
        shipment_id = test_context.get_last("shipment_id")
        sscc_code = f"00380060191111150000000001"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/add_sscc",
                json={
                    "shipment_id": shipment_id,
                    "sscc_code": sscc_code,
                    "status": "added",
                    "packages_count": 1
                },
                status=200,
            )

        sscc_data = ShipmentAddPackage(
            line_number=line_number,
            sscc_code=sscc_code,
            is_forced=False
        )
        
        resp = add_sscc(client, body=sscc_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["sscc_code"] == sscc_code
        assert data["status"] == "added"
        
        test_context.add("sscc_1_code", sscc_code)
        print(f"[E2E-SHIPMENT] Первый SSCC добавлен: {sscc_code}")

    def test_06_add_second_sscc_positive(self, client, test_context, mock_api):
        """Шаг 6: Позитивный сценарий добавления второго SSCC."""
        line_number = test_context.get_last("shipment_line_number")
        shipment_id = test_context.get_last("shipment_id")
        sscc_code = f"00380060191111150000000002"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/add_sscc",
                json={
                    "shipment_id": shipment_id,
                    "sscc_code": sscc_code,
                    "status": "added",
                    "packages_count": 2
                },
                status=200,
            )

        sscc_data = ShipmentAddPackage(
            line_number=line_number,
            sscc_code=sscc_code,
            is_forced=False
        )
        
        resp = add_sscc(client, body=sscc_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["sscc_code"] == sscc_code
        assert data["status"] == "added"
        
        test_context.add("sscc_2_code", sscc_code)
        print(f"[E2E-SHIPMENT] Второй SSCC добавлен: {sscc_code}")

    def test_07_add_sscc_negative_duplicate(self, client, test_context, mock_api):
        """Шаг 7: Негативный сценарий - добавление дублирующего SSCC."""
        line_number = test_context.get_last("shipment_line_number")
        sscc_1_code = test_context.get_last("sscc_1_code")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/add_sscc",
                json={"detail": "SSCC already exists in this shipment"},
                status=409,
            )

        sscc_data = ShipmentAddPackage(
            line_number=line_number,
            sscc_code=sscc_1_code,  # Дублирующий SSCC
            is_forced=False
        )
        
        resp = add_sscc(client, body=sscc_data)
        assert resp.status_code == 409
        print(f"[E2E-SHIPMENT] Тест дублирования SSCC: статус {resp.status_code}")

    def test_08_add_sscc_negative_invalid_format(self, client, test_context, mock_api):
        """Шаг 8: Негативный сценарий - добавление SSCC с невалидным форматом."""
        line_number = test_context.get_last("shipment_line_number")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/add_sscc",
                json={"detail": "Invalid SSCC format"},
                status=400,
            )

        sscc_data = ShipmentAddPackage(
            line_number=line_number,
            sscc_code="INVALID_SSCC_FORMAT",  # Невалидный формат
            is_forced=False
        )
        
        resp = add_sscc(client, body=sscc_data)
        assert resp.status_code == 400
        print(f"[E2E-SHIPMENT] Тест невалидного формата SSCC: статус {resp.status_code}")

    def test_09_filter_shipments(self, client, test_context, mock_api):
        """Шаг 9: Фильтрация отгрузок."""
        shipment_id = test_context.get_last("shipment_id")
        shipment_name = test_context.get_last("shipment_name")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/filter",
                json={
                    "total_count": 1,
                    "result": [
                        {
                            "id": shipment_id,
                            "name": shipment_name,
                            "status": "active",
                            "line_number": test_context.get_last("shipment_line_number"),
                            "sscc_count": 2,
                            "created_at": datetime.datetime.now().isoformat()
                        }
                    ]
                },
                status=200,
            )

        resp = filter_shipments(client, json={"limit": 10, "offset": 0, "name": shipment_name})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] >= 1
        
        # Проверяем, что наша отгрузка есть в результатах
        found_shipment = next((s for s in data["result"] if s["name"] == shipment_name), None)
        assert found_shipment is not None
        print(f"[E2E-SHIPMENT] Фильтрация отгрузок: найдено {data['total_count']}")

    def test_10_get_shipment_detail_info(self, client, test_context, mock_api):
        """Шаг 10: Получение детальной информации об отгрузке."""
        shipment_id = test_context.get_last("shipment_id")
        sscc_1_code = test_context.get_last("sscc_1_code")
        sscc_2_code = test_context.get_last("sscc_2_code")
        
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/shipment/get_detail_info",
                json={
                    "id": shipment_id,
                    "name": test_context.get_last("shipment_name"),
                    "status": "active",
                    "line_number": test_context.get_last("shipment_line_number"),
                    "sscc_list": [
                        {"code": sscc_1_code, "status": "added", "packages_count": 10},
                        {"code": sscc_2_code, "status": "added", "packages_count": 15}
                    ],
                    "total_packages": 25,
                    "created_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = get_detail_info(client, params={"id": shipment_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == shipment_id
        assert len(data["sscc_list"]) == 2
        assert data["total_packages"] == 25
        print(f"[E2E-SHIPMENT] Детальная информация об отгрузке получена")

    def test_11_withdrawal_code_from_shipment(self, client, test_context, mock_api):
        """Шаг 11: Изъятие кода из отгрузки."""
        shipment_id = test_context.get_last("shipment_id")
        withdrawal_code = "0104606203399737215withdrawal00193dGVzdA=="
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/withdrawal_code",
                json={
                    "shipment_id": shipment_id,
                    "code": withdrawal_code,
                    "status": "withdrawn",
                    "remaining_packages": 24
                },
                status=200,
            )

        resp = withdrawal_code(client, json={"shipment_id": shipment_id, "code": withdrawal_code})
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == withdrawal_code
        assert data["status"] == "withdrawn"
        print(f"[E2E-SHIPMENT] Код изъят из отгрузки: {withdrawal_code}")

    def test_12_finish_shipment_positive(self, client, test_context, mock_api):
        """Шаг 12: Позитивный сценарий завершения отгрузки."""
        line_number = test_context.get_last("shipment_line_number")
        shipment_id = test_context.get_last("shipment_id")
        pin_code = "123456"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/finish",
                json={
                    "id": shipment_id,
                    "status": "finished",
                    "finished_at": datetime.datetime.now().isoformat(),
                    "total_packages": 24
                },
                status=200,
            )

        finish_data = ShipmentFinish(
            line_number=line_number,
            pin_code=pin_code
        )
        
        resp = finish_shipment(client, body=finish_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "finished"
        assert data["id"] == shipment_id
        print(f"[E2E-SHIPMENT] Отгрузка завершена: {shipment_id}")

    def test_13_finish_shipment_negative_wrong_pin(self, client, test_context, mock_api):
        """Шаг 13: Негативный сценарий - завершение отгрузки с неверным PIN."""
        line_number = test_context.get_last("shipment_line_number")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/finish",
                json={"detail": "Invalid PIN code"},
                status=401,
            )

        finish_data = ShipmentFinish(
            line_number=line_number,
            pin_code="000000"  # Неверный PIN
        )
        
        resp = finish_shipment(client, body=finish_data)
        assert resp.status_code == 401
        print(f"[E2E-SHIPMENT] Негативный тест завершения отгрузки: статус {resp.status_code}")

    def test_14_download_shipment_data(self, client, test_context, mock_api):
        """Шаг 14: Скачивание данных отгрузки."""
        shipment_id = test_context.get_last("shipment_id")
        
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/shipment/download",
                json={
                    "shipment_id": shipment_id,
                    "download_url": f"/downloads/shipment_{shipment_id}.csv",
                    "format": "csv"
                },
                status=200,
            )

        resp = download_shipment(client, params={"id": shipment_id})
        assert resp.status_code == 200
        data = resp.json()
        assert "download_url" in data
        assert data["format"] == "csv"
        print(f"[E2E-SHIPMENT] Данные отгрузки доступны для скачивания")

    def test_15_boundary_test_large_shipment_filter(self, client, test_context, mock_api):
        """Шаг 15: Граничный тест - фильтрация большого количества отгрузок."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/filter",
                json={
                    "total_count": 100,
                    "result": [
                        {
                            "id": str(uuid.uuid4()),
                            "name": f"SHIPMENT_BOUNDARY_{i:03d}",
                            "status": "finished" if i % 2 == 0 else "active",
                            "line_number": 400 + (i % 10),
                            "sscc_count": i + 1
                        } for i in range(100)
                    ]
                },
                status=200,
            )

        # Запрос с максимальным лимитом
        resp = filter_shipments(client, json={"limit": 100, "offset": 0})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["result"]) <= 100
        print(f"[E2E-SHIPMENT] Граничный тест: получено {len(data['result'])} отгрузок")

    def test_16_boundary_test_empty_filter_results(self, client, test_context, mock_api):
        """Шаг 16: Граничный тест - пустые результаты фильтрации."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/filter",
                json={
                    "total_count": 0,
                    "result": []
                },
                status=200,
            )

        # Фильтр по несуществующему имени
        resp = filter_shipments(client, json={"limit": 10, "offset": 0, "name": "NONEXISTENT_SHIPMENT_12345"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] == 0
        assert len(data["result"]) == 0
        print(f"[E2E-SHIPMENT] Граничный тест: пустые результаты фильтрации")

    def test_17_error_test_invalid_shipment_id(self, client, test_context, mock_api):
        """Шаг 17: Тест обработки ошибок - невалидный ID отгрузки."""
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/shipment/get_detail_info",
                json={"detail": "Shipment not found"},
                status=404,
            )

        # Запрос с несуществующим ID
        invalid_id = "00000000-0000-0000-0000-000000000000"
        resp = get_detail_info(client, params={"id": invalid_id})
        assert resp.status_code == 404
        print(f"[E2E-SHIPMENT] Тест обработки ошибок: невалидный ID отгрузки")

    def test_18_error_test_permission_denied(self, client, test_context, mock_api):
        """Шаг 18: Тест обработки ошибок - отказ в доступе."""
        shipment_id = test_context.get_last("shipment_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/delete",
                json={"detail": "Permission denied"},
                status=403,
            )

        # Попытка удаления без необходимых привилегий
        resp = delete_shipment(client, json={"id": shipment_id})
        assert resp.status_code == 403
        print(f"[E2E-SHIPMENT] Тест обработки ошибок: отказ в доступе")

    def test_19_resume_shipment(self, client, test_context, mock_api):
        """Шаг 19: Возобновление отгрузки после прерывания."""
        line_number = test_context.get_last("shipment_line_number")
        shipment_id = test_context.get_last("shipment_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/resume",
                json={
                    "id": shipment_id,
                    "status": "active",
                    "resumed_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = resume_shipment(client, json={"line_number": line_number})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "active"
        assert data["id"] == shipment_id
        print(f"[E2E-SHIPMENT] Отгрузка возобновлена: {shipment_id}")

    def test_20_cleanup_test_shipment(self, client, test_context, mock_api):
        """Шаг 20: Очистка - удаление тестовой отгрузки."""
        shipment_id = test_context.get_last("shipment_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/delete",
                json={
                    "id": shipment_id,
                    "deleted": True
                },
                status=200,
            )

        resp = delete_shipment(client, json={"id": shipment_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["deleted"] is True
        print(f"[E2E-SHIPMENT] Тестовая отгрузка удалена для очистки")