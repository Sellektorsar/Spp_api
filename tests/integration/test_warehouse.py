import pytest
import os
from src.api.warehouse.filter import filter as filter_rolls
from src.api.warehouse.get_metadata import get_metadata


@pytest.mark.integration
class TestWarehouse:
    """
    Integration tests for Warehouse management.
    """

    def test_filter_rolls_archived(self, client):
        """Фильтрация архивных роликов (Case 10)."""
        resp = filter_rolls(client, json={
            "limit": 50,
            "skip": 0,
            "is_archived": True
        })
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        print(f"[INT-WH] Архивных роликов: {data.get('total_count', 0)}")
        
    def test_get_roll_by_code(self, client, real_gtin):
        """Поиск ролика по КМ (Case 7)."""
        test_code = f"01{real_gtin}215test12345678"

        resp = client.post(
            "/api/web/v1/warehouse/get_roll_by_code",
            json={"code": test_code}
        )
        assert resp.status_code in [200, 404]
        print(f"[INT-WH] Поиск ролика по КМ: {resp.status_code}")

    def test_count_codes_in_roll(self, client):
        """Подсчет кодов в ролике."""
        roll_id = os.getenv("SPP_TEST_ROLL_ID")
        if not roll_id:
            pytest.skip("SPP_TEST_ROLL_ID не задан")

        resp = client.post(
            "/api/web/v1/warehouse/count_codes",
            json={"id": roll_id}
        )
        assert resp.status_code in [200, 404]
        print(f"[INT-WH] Подсчет кодов: {resp.status_code}")

    def test_get_roll_info(self, client):
        """Получение полной информации о ролике."""
        roll_id = os.getenv("SPP_TEST_ROLL_ID")
        if not roll_id:
            pytest.skip("SPP_TEST_ROLL_ID не задан")

        resp = client.post(
            "/api/web/v1/warehouse/get_roll",
            json={"id": roll_id}
        )
        assert resp.status_code in [200, 404]
        print(f"[INT-WH] Информация о ролике: {resp.status_code}")

    def test_get_used_in_work_shift(self, client):
        """Получение истории использования ролика."""
        roll_id = os.getenv("SPP_TEST_ROLL_ID")
        if not roll_id:
            pytest.skip("SPP_TEST_ROLL_ID не задан")

        resp = client.post(
            "/api/web/v1/warehouse/get_used_in_work_shift",
            json={"roll_id": roll_id, "limit": 10}
        )
        assert resp.status_code in [200, 404]
        print(f"[INT-WH] История использования: {resp.status_code}")

    def test_get_last_code(self, client):
        """Получение последнего кода ролика."""
        roll_id = os.getenv("SPP_TEST_ROLL_ID")
        if not roll_id:
            pytest.skip("SPP_TEST_ROLL_ID не задан")

        resp = client.post(
            "/api/web/v1/warehouse/get_last_code",
            json={"roll_id": roll_id}
        )
        assert resp.status_code in [200, 404]
        print(f"[INT-WH] Последний код: {resp.status_code}")

    def test_download_warehouse_codes(self, client):
        """Скачивание кодов ролика."""
        roll_id = os.getenv("SPP_TEST_ROLL_ID")
        if not roll_id:
            pytest.skip("SPP_TEST_ROLL_ID не задан")

        resp = client.post(
            "/api/web/v1/warehouse/download",
            json={"id": roll_id, "format": "csv"}
        )
        assert resp.status_code in [200, 404]
        print(f"[INT-WH] Скачивание кодов: {resp.status_code}")

    def test_map_get_metadata(self, client):
        """Получение метаданных карты ролика."""
        roll_id = os.getenv("SPP_TEST_ROLL_ID")
        if not roll_id:
            pytest.skip("SPP_TEST_ROLL_ID не задан")

        resp = client.post(
            "/api/web/v1/warehouse/map/get_metadata",
            json={"roll_id": roll_id}
        )
        assert resp.status_code in [200, 404]
        print(f"[INT-WH] Метаданные карты: {resp.status_code}")

    def test_map_get_detail_metadata(self, client):
        """Получение детальных метаданных карты ролика."""
        roll_id = os.getenv("SPP_TEST_ROLL_ID")
        if not roll_id:
            pytest.skip("SPP_TEST_ROLL_ID не задан")

        resp = client.post(
            "/api/web/v1/warehouse/map/get_detail_metadata",
            json={"roll_id": roll_id, "zoom": 2}
        )
        assert resp.status_code in [200, 404]
        print(f"[INT-WH] Детальные метаданные: {resp.status_code}")


    def test_filter_rolls_default(self, client):
        """Test filtering rolls with default parameters."""
        resp = filter_rolls(client, json={"limit": 20, "skip": 0})
        assert resp.status_code == 200
        data = resp.json()
        
        # Verify structure
        assert "result" in data, "Response should contain 'result' list"
        assert "total_count" in data, "Response should contain 'total_count'"
        assert isinstance(data["result"], list)

    def test_filter_rolls_by_product_group(self, client):
        """Test filtering rolls by product group (milk)."""
        resp = filter_rolls(client, json={"limit": 10, "skip": 0, "product_group": "milk"})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data["result"], list)

    def test_get_roll_metadata(self, client):
        """Test getting metadata for a real roll found in the warehouse."""
        # 1. Find a roll first
        f_resp = filter_rolls(client, json={"limit": 1, "skip": 0})
        if f_resp.status_code != 200:
            pytest.skip(f"Failed to filter rolls: {f_resp.status_code}")
        
        rolls = f_resp.json().get("result", [])
        if not rolls:
            pytest.skip("No rolls found in warehouse to test metadata")
            
        roll = rolls[0]
        usn = roll.get("unit_serial_number")
        
        if not usn:
            pytest.skip(f"Roll found but has no unit_serial_number: {roll}")

        # 2. Get metadata
        resp = get_metadata(client, json={"unit_serial_number": usn})
        
        # It might return 200 or 4xx depending on roll state, but 500 would be bad.
        assert resp.status_code in [200, 400, 422, 404]
        
        if resp.status_code == 200:
            data = resp.json()
            # Expecting some metadata structure
            assert isinstance(data, dict)
            # Likely contains rows/cols or similar map info
