"""
E2E Tests: Warehouse Operations
Сценарий: полный цикл работы со складом.

Шаги:
1. Загрузка роликов на склад
2. Проверка метаданных роликов
3. Слияние нескольких роликов
4. Изменение срока годности
5. Поиск кодов на складе
6. Удаление роликов
"""
import pytest
import responses
import uuid
import datetime
from typing import Dict, Any

from src.api.warehouse.load import load as load_roll
from src.api.warehouse.load_roll_by_api import load_roll_by_api
from src.api.warehouse.filter import filter as filter_warehouse
from src.api.warehouse.get_roll import get_roll
from src.api.warehouse.get_roll_by_code import get_roll_by_code
from src.api.warehouse.get_metadata import get_metadata
from src.api.warehouse.get_detail_metadata import get_detail_metadata
from src.api.warehouse.get_info_before_merge import get_info_before_merge
from src.api.warehouse.merge_rolls import merge_rolls
from src.api.warehouse.change_exp_date import change_exp_date
from src.api.warehouse.count_codes import count_codes
from src.api.warehouse.get_last_code import get_last_code
from src.api.warehouse.get_used_in_work_shift import get_used_in_work_shift
from src.api.warehouse.delete import delete as delete_roll
from src.api.warehouse.download import download
from src.api.warehouse.change import change as change_roll
from src.models import LoadInput, MergeInput, ChangeExpDateInput, WarehouseFilterInput


@pytest.mark.e2e
@pytest.mark.order(6)
class TestWarehouseOperations:
    """
    E2E Сценарий: Полный цикл работы со складом.
    """

    def test_01_load_first_roll_positive(self, client, test_context, mock_api):
        """Шаг 1: Позитивный сценарий загрузки первого ролика на склад."""
        roll_id = str(uuid.uuid4())
        serial_number = f"ROLL_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_001"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/load",
                json={
                    "id": roll_id,
                    "serial_number": serial_number,
                    "status": "loaded",
                    "codes_count": 100,
                    "created_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        load_data = LoadInput(unit_serial_number=serial_number)
        resp = load_roll(client, body=load_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["serial_number"] == serial_number
        assert data["status"] == "loaded"
        
        test_context.add("roll_1_id", data["id"])
        test_context.add("roll_1_serial", serial_number)
        print(f"[E2E-WAREHOUSE] Первый ролик загружен: {serial_number} (ID: {data['id']})")

    def test_02_load_second_roll_positive(self, client, test_context, mock_api):
        """Шаг 2: Позитивный сценарий загрузки второго ролика на склад."""
        roll_id = str(uuid.uuid4())
        serial_number = f"ROLL_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_002"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/load",
                json={
                    "id": roll_id,
                    "serial_number": serial_number,
                    "status": "loaded",
                    "codes_count": 150,
                    "created_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        load_data = LoadInput(unit_serial_number=serial_number)
        resp = load_roll(client, body=load_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["serial_number"] == serial_number
        assert data["status"] == "loaded"
        
        test_context.add("roll_2_id", data["id"])
        test_context.add("roll_2_serial", serial_number)
        print(f"[E2E-WAREHOUSE] Второй ролик загружен: {serial_number} (ID: {data['id']})")

    def test_03_load_roll_negative_invalid_serial(self, client, test_context, mock_api):
        """Шаг 3: Негативный сценарий - загрузка ролика с невалидным серийным номером."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/load",
                json={"detail": "Invalid serial number format"},
                status=400,
            )

        load_data = LoadInput(unit_serial_number="")  # Пустой серийный номер
        resp = load_roll(client, body=load_data)
        assert resp.status_code == 400
        print(f"[E2E-WAREHOUSE] Негативный тест загрузки: статус {resp.status_code}")

    def test_04_load_roll_negative_duplicate_serial(self, client, test_context, mock_api):
        """Шаг 4: Негативный сценарий - загрузка ролика с дублирующим серийным номером."""
        roll_1_serial = test_context.get_last("roll_1_serial")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/load",
                json={"detail": "Roll with this serial number already exists"},
                status=409,
            )

        load_data = LoadInput(unit_serial_number=roll_1_serial)  # Дублирующий серийный номер
        resp = load_roll(client, body=load_data)
        assert resp.status_code == 409
        print(f"[E2E-WAREHOUSE] Тест дублирования серийного номера: статус {resp.status_code}")

    def test_05_filter_warehouse_rolls(self, client, test_context, mock_api):
        """Шаг 5: Фильтрация роликов на складе."""
        roll_1_serial = test_context.get_last("roll_1_serial")
        roll_1_id = test_context.get_last("roll_1_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/filter",
                json={
                    "total_count": 2,
                    "result": [
                        {
                            "id": roll_1_id,
                            "serial_number": roll_1_serial,
                            "status": "loaded",
                            "codes_count": 100
                        },
                        {
                            "id": test_context.get_last("roll_2_id"),
                            "serial_number": test_context.get_last("roll_2_serial"),
                            "status": "loaded",
                            "codes_count": 150
                        }
                    ]
                },
                status=200,
            )

        filter_data = WarehouseFilterInput(
            limit=10,
            offset=0,
            serial_number=roll_1_serial
        )
        
        resp = filter_warehouse(client, body=filter_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] >= 1
        
        # Проверяем, что наш ролик есть в результатах
        found_roll = next((r for r in data["result"] if r["serial_number"] == roll_1_serial), None)
        assert found_roll is not None
        print(f"[E2E-WAREHOUSE] Фильтрация роликов: найдено {data['total_count']}")

    def test_06_get_roll_details(self, client, test_context, mock_api):
        """Шаг 6: Получение детальной информации о ролике."""
        roll_1_id = test_context.get_last("roll_1_id")
        roll_1_serial = test_context.get_last("roll_1_serial")
        
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/warehouse/get_roll",
                json={
                    "id": roll_1_id,
                    "serial_number": roll_1_serial,
                    "status": "loaded",
                    "codes_count": 100,
                    "created_at": datetime.datetime.now().isoformat(),
                    "expired_date": (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat(),
                    "gtin": "04606203399737"
                },
                status=200,
            )

        resp = get_roll(client, params={"id": roll_1_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == roll_1_id
        assert data["serial_number"] == roll_1_serial
        print(f"[E2E-WAREHOUSE] Детали ролика получены: {roll_1_serial}")

    def test_07_get_roll_by_code(self, client, test_context, mock_api):
        """Шаг 7: Поиск ролика по коду маркировки."""
        roll_1_id = test_context.get_last("roll_1_id")
        test_code = "0104606203399737215warehouse00193dGVzdA=="
        
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/warehouse/get_roll_by_code",
                json={
                    "roll_id": roll_1_id,
                    "code": test_code,
                    "status": "found",
                    "position_in_roll": 1
                },
                status=200,
            )

        resp = get_roll_by_code(client, params={"code": test_code})
        assert resp.status_code == 200
        data = resp.json()
        assert data["code"] == test_code
        assert data["roll_id"] == roll_1_id
        print(f"[E2E-WAREHOUSE] Ролик найден по коду: {test_code}")

    def test_08_get_roll_metadata(self, client, test_context, mock_api):
        """Шаг 8: Получение метаданных ролика."""
        roll_1_id = test_context.get_last("roll_1_id")
        
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/warehouse/get_metadata",
                json={
                    "roll_id": roll_1_id,
                    "metadata": {
                        "created_at": datetime.datetime.now().isoformat(),
                        "codes_count": 100,
                        "gtin": "04606203399737",
                        "batch_number": "BATCH-WAREHOUSE-001",
                        "production_date": datetime.datetime.now().isoformat()
                    }
                },
                status=200,
            )

        resp = get_metadata(client, params={"roll_id": roll_1_id})
        assert resp.status_code == 200
        data = resp.json()
        assert "metadata" in data
        assert data["metadata"]["codes_count"] == 100
        print(f"[E2E-WAREHOUSE] Метаданные ролика получены")

    def test_09_get_roll_detail_metadata(self, client, test_context, mock_api):
        """Шаг 9: Получение детальных метаданных ролика."""
        roll_1_id = test_context.get_last("roll_1_id")
        
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/warehouse/get_detail_metadata",
                json={
                    "roll_id": roll_1_id,
                    "detail_metadata": {
                        "created_at": datetime.datetime.now().isoformat(),
                        "codes_count": 100,
                        "gtin": "04606203399737",
                        "batch_number": "BATCH-WAREHOUSE-001",
                        "production_date": datetime.datetime.now().isoformat(),
                        "expired_date": (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat(),
                        "codes": [
                            {"code": "0104606203399737215warehouse00193dGVzdA==", "status": "available"},
                            {"code": "0104606203399737215warehouse00293dGVzdA==", "status": "available"}
                        ]
                    }
                },
                status=200,
            )

        resp = get_detail_metadata(client, params={"roll_id": roll_1_id})
        assert resp.status_code == 200
        data = resp.json()
        assert "detail_metadata" in data
        assert "codes" in data["detail_metadata"]
        print(f"[E2E-WAREHOUSE] Детальные метаданные ролика получены")

    def test_10_get_info_before_merge(self, client, test_context, mock_api):
        """Шаг 10: Получение информации перед слиянием роликов."""
        roll_1_id = test_context.get_last("roll_1_id")
        roll_2_id = test_context.get_last("roll_2_id")
        
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/warehouse/get_info_before_merge",
                json={
                    "first_roll": {
                        "id": roll_1_id,
                        "serial_number": test_context.get_last("roll_1_serial"),
                        "codes_count": 100,
                        "gtin": "04606203399737"
                    },
                    "second_roll": {
                        "id": roll_2_id,
                        "serial_number": test_context.get_last("roll_2_serial"),
                        "codes_count": 150,
                        "gtin": "04606203399737"
                    },
                    "can_merge": True,
                    "result_codes_count": 250
                },
                status=200,
            )

        resp = get_info_before_merge(client, params={"first_roll_id": roll_1_id, "second_roll_id": roll_2_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["can_merge"] is True
        assert data["result_codes_count"] == 250
        print(f"[E2E-WAREHOUSE] Информация перед слиянием получена")

    def test_11_merge_rolls_positive(self, client, test_context, mock_api):
        """Шаг 11: Позитивный сценарий слияния роликов."""
        roll_1_id = test_context.get_last("roll_1_id")
        roll_2_id = test_context.get_last("roll_2_id")
        merged_roll_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/merge_rolls",
                json={
                    "id": merged_roll_id,
                    "first_roll_id": roll_1_id,
                    "second_roll_id": roll_2_id,
                    "status": "merged",
                    "codes_count": 250,
                    "serial_number": f"MERGED_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                },
                status=200,
            )

        merge_data = MergeInput(
            first_code=roll_1_id,
            second_code=roll_2_id
        )
        
        resp = merge_rolls(client, body=merge_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "merged"
        assert data["codes_count"] == 250
        
        test_context.add("merged_roll_id", data["id"])
        test_context.add("merged_roll_serial", data["serial_number"])
        print(f"[E2E-WAREHOUSE] Ролики слиты: {data['serial_number']} (ID: {data['id']})")

    def test_12_merge_rolls_negative_incompatible(self, client, test_context, mock_api):
        """Шаг 12: Негативный сценарий - слияние несовместимых роликов."""
        incompatible_roll_1_id = str(uuid.uuid4())
        incompatible_roll_2_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/merge_rolls",
                json={"detail": "Rolls are incompatible for merging (different GTIN)"},
                status=400,
            )

        merge_data = MergeInput(
            first_code=incompatible_roll_1_id,
            second_code=incompatible_roll_2_id
        )
        
        resp = merge_rolls(client, body=merge_data)
        assert resp.status_code == 400
        print(f"[E2E-WAREHOUSE] Негативный тест слияния: статус {resp.status_code}")

    def test_13_change_expiration_date_positive(self, client, test_context, mock_api):
        """Шаг 13: Позитивный сценарий изменения срока годности."""
        merged_roll_id = test_context.get_last("merged_roll_id")
        new_exp_date = (datetime.datetime.now() + datetime.timedelta(days=730)).isoformat()  # +2 года
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/change_exp_date",
                json={
                    "id": merged_roll_id,
                    "expired_date": new_exp_date,
                    "updated": True
                },
                status=200,
            )

        exp_date_data = ChangeExpDateInput(
            unit_serial_number=merged_roll_id,
            expired_date=new_exp_date
        )
        
        resp = change_exp_date(client, body=exp_date_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["updated"] is True
        assert data["expired_date"] == new_exp_date
        
        test_context.add("updated_exp_date", new_exp_date)
        print(f"[E2E-WAREHOUSE] Срок годности изменен: {new_exp_date}")

    def test_14_change_expiration_date_negative_past_date(self, client, test_context, mock_api):
        """Шаг 14: Негативный сценарий - изменение срока годности на прошедшую дату."""
        merged_roll_id = test_context.get_last("merged_roll_id")
        past_date = (datetime.datetime.now() - datetime.timedelta(days=10)).isoformat()  # 10 дней назад
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/change_exp_date",
                json={"detail": "Expiration date cannot be in the past"},
                status=400,
            )

        exp_date_data = ChangeExpDateInput(
            unit_serial_number=merged_roll_id,
            expired_date=past_date
        )
        
        resp = change_exp_date(client, body=exp_date_data)
        assert resp.status_code == 400
        print(f"[E2E-WAREHOUSE] Негативный тест изменения срока годности: статус {resp.status_code}")

    def test_15_count_codes_in_roll(self, client, test_context, mock_api):
        """Шаг 15: Подсчет кодов в ролике."""
        merged_roll_id = test_context.get_last("merged_roll_id")
        
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/warehouse/count_codes",
                json={
                    "roll_id": merged_roll_id,
                    "total_codes": 250,
                    "available_codes": 250,
                    "used_codes": 0
                },
                status=200,
            )

        resp = count_codes(client, params={"roll_id": merged_roll_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_codes"] == 250
        assert data["available_codes"] == 250
        assert data["used_codes"] == 0
        print(f"[E2E-WAREHOUSE] Коды в ролике подсчитаны: {data['total_codes']}")

    def test_16_get_last_code_in_roll(self, client, test_context, mock_api):
        """Шаг 16: Получение последнего кода в ролике."""
        merged_roll_id = test_context.get_last("merged_roll_id")
        last_code = "0104606203399737215lastcode25093dGVzdA=="
        
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/warehouse/get_last_code",
                json={
                    "roll_id": merged_roll_id,
                    "last_code": last_code,
                    "position": 250
                },
                status=200,
            )

        resp = get_last_code(client, params={"roll_id": merged_roll_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["last_code"] == last_code
        assert data["position"] == 250
        print(f"[E2E-WAREHOUSE] Последний код в ролике получен: позиция {data['position']}")

    def test_17_get_used_in_work_shift(self, client, test_context, mock_api):
        """Шаг 17: Получение информации об использовании ролика в рабочих сменах."""
        merged_roll_id = test_context.get_last("merged_roll_id")
        
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/warehouse/get_used_in_work_shift",
                json={
                    "roll_id": merged_roll_id,
                    "used_in_shifts": [],
                    "total_used_codes": 0
                },
                status=200,
            )

        resp = get_used_in_work_shift(client, params={"roll_id": merged_roll_id})
        assert resp.status_code == 200
        data = resp.json()
        assert "used_in_shifts" in data
        assert "total_used_codes" in data
        print(f"[E2E-WAREHOUSE] Информация об использовании в сменах получена")

    def test_18_boundary_test_large_roll_filter(self, client, test_context, mock_api):
        """Шаг 18: Граничный тест - фильтрация большого количества роликов."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/filter",
                json={
                    "total_count": 100,
                    "result": [
                        {
                            "id": str(uuid.uuid4()),
                            "serial_number": f"ROLL_BOUNDARY_{i:03d}",
                            "status": "loaded",
                            "codes_count": 100 + i
                        } for i in range(100)
                    ]
                },
                status=200,
            )

        # Запрос с максимальным лимитом
        filter_data = WarehouseFilterInput(
            limit=100,  # Максимальный лимит
            offset=0
        )
        
        resp = filter_warehouse(client, body=filter_data)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["result"]) <= 100
        print(f"[E2E-WAREHOUSE] Граничный тест: получено {len(data['result'])} роликов")

    def test_19_boundary_test_empty_filter_results(self, client, test_context, mock_api):
        """Шаг 19: Граничный тест - пустые результаты фильтрации."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/filter",
                json={
                    "total_count": 0,
                    "result": []
                },
                status=200,
            )

        # Фильтр по несуществующему серийному номеру
        filter_data = WarehouseFilterInput(
            limit=10,
            offset=0,
            serial_number="NONEXISTENT_ROLL_12345"
        )
        
        resp = filter_warehouse(client, body=filter_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] == 0
        assert len(data["result"]) == 0
        print(f"[E2E-WAREHOUSE] Граничный тест: пустые результаты фильтрации")

    def test_20_error_test_invalid_roll_id(self, client, test_context, mock_api):
        """Шаг 20: Тест обработки ошибок - невалидный ID ролика."""
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/warehouse/get_roll",
                json={"detail": "Roll not found"},
                status=404,
            )

        # Запрос с несуществующим ID
        invalid_id = "00000000-0000-0000-0000-000000000000"
        resp = get_roll(client, params={"id": invalid_id})
        assert resp.status_code == 404
        print(f"[E2E-WAREHOUSE] Тест обработки ошибок: невалидный ID ролика")

    def test_21_cleanup_test_rolls(self, client, test_context, mock_api):
        """Шаг 21: Очистка - удаление тестовых роликов."""
        merged_roll_id = test_context.get_last("merged_roll_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/delete",
                json={
                    "id": merged_roll_id,
                    "deleted": True
                },
                status=200,
            )

        resp = delete_roll(client, json={"id": merged_roll_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["deleted"] is True
        print(f"[E2E-WAREHOUSE] Тестовый ролик удален для очистки")