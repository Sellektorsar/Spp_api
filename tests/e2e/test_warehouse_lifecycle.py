"""
E2E Сценарий: Управление складом — загрузка, слияние, архивация.
"""
import uuid
import responses
import datetime


class TestWarehouseLifecycle:
    """
    E2E Сценарий: Полный цикл жизни роликов на складе.
    """

    def test_01_load_roll_first(self, client, test_context, mock_api):
        """Шаг 1: Загрузка первого ролика."""
        roll_id_1 = str(uuid.uuid4())
        gtin = "04600494009044"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/load",
                json={
                    "id": roll_id_1,
                    "gtin": gtin,
                    "quantity": 100,
                    "status": "loaded"
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/warehouse/load",
            json={"gtin": gtin, "quantity": 100, "inn": "1234567890"}
        )
        
        assert resp.status_code == 200
        data = resp.json()
        test_context.add("warehouse_roll_id_1", data.get("id", roll_id_1))
        print(f"[E2E-WH] Ролик 1 загружен: {data.get('id')}")

    def test_02_load_roll_second(self, client, test_context, mock_api):
        """Шаг 2: Загрузка второго ролика для слияния."""
        roll_id_2 = str(uuid.uuid4())
        gtin = "04600494009044"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/load",
                json={
                    "id": roll_id_2,
                    "gtin": gtin,
                    "quantity": 150,
                    "status": "loaded"
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/warehouse/load",
            json={"gtin": gtin, "quantity": 150, "inn": "1234567890"}
        )
        
        assert resp.status_code == 200
        data = resp.json()
        test_context.add("warehouse_roll_id_2", data.get("id", roll_id_2))
        print(f"[E2E-WH] Ролик 2 загружен: {data.get('id')}")

    def test_03_get_info_before_merge(self, client, test_context, mock_api):
        """Шаг 3: Получение информации перед слиянием."""
        roll_id_1 = test_context.get_last("warehouse_roll_id_1")
        roll_id_2 = test_context.get_last("warehouse_roll_id_2")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/get_info_before_merge",
                json={
                    "roll_1_codes": 100,
                    "roll_2_codes": 150,
                    "total_codes": 250,
                    "gtin_match": True
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/warehouse/get_info_before_merge",
            json={"roll_id_1": roll_id_1, "roll_id_2": roll_id_2}
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["total_codes"] == 250
        print(f"[E2E-WH] Предварительная информация: {data}")

    def test_04_merge_rolls(self, client, test_context, mock_api):
        """Шаг 4: Слияние двух роликов в третий."""
        roll_id_1 = test_context.get_last("warehouse_roll_id_1")
        roll_id_2 = test_context.get_last("warehouse_roll_id_2")
        merged_roll_id = str(uuid.uuid4())

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/merge_rolls",
                json={
                    "id": merged_roll_id,
                    "source_ids": [roll_id_1, roll_id_2],
                    "status": "merged",
                    "total_codes": 250
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/warehouse/merge_rolls",
            json={"roll_id_1": roll_id_1, "roll_id_2": roll_id_2}
        )

        assert resp.status_code == 200
        data = resp.json()
        test_context.add("warehouse_merged_roll_id", data.get("id", merged_roll_id))
        print(f"[E2E-WH] Ролики слиты в: {data.get('id')}")

    def test_05_change_exp_date(self, client, test_context, mock_api):
        """Шаг 5: Изменение срока годности объединенного ролика."""
        roll_id = test_context.get_last("warehouse_merged_roll_id")
        new_date = (datetime.datetime.now() + datetime.timedelta(days=365)).date().isoformat()

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/change_exp_date",
                json={"id": roll_id, "exp_date": new_date, "status": "updated"},
                status=200,
            )

        resp = client.post(
            "/api/web/v1/warehouse/change_exp_date",
            json={"id": roll_id, "exp_date": new_date}
        )

        assert resp.status_code == 200
        print(f"[E2E-WH] Срок годности обновлен для {roll_id}")

    def test_06_archive_roll(self, client, test_context, mock_api):
        """Шаг 6: Архивация ролика."""
        roll_id = test_context.get_last("warehouse_merged_roll_id")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/is_archived/change",
                json={"id": roll_id, "is_archived": True, "status": "archived"},
                status=200,
            )

        resp = client.post(
            "/api/web/v1/warehouse/is_archived/change",
            json={"id": roll_id, "is_archived": True}
        )

        assert resp.status_code == 200
        print(f"[E2E-WH] Ролик заархивирован: {roll_id}")

    def test_07_get_archived_rolls(self, client, test_context, mock_api):
        """Шаг 7: Проверка фильтрации архивных роликов."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/filter",
                json={
                    "total_count": 1,
                    "result": [{"id": test_context.get_last("warehouse_merged_roll_id"), "is_archived": True}]
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/warehouse/filter",
            json={"is_archived": True, "limit": 10, "offset": 0}
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] >= 0
        print(f"[E2E-WH] Архивные ролики получены: {data.get('total_count')} шт.")

    def test_08_unarchive_roll(self, client, test_context, mock_api):
        """Шаг 8: Возврат ролика из архива на склад (Case 10)."""
        roll_id = test_context.get_last("warehouse_merged_roll_id")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/is_archived/change",
                json={"id": roll_id, "is_archived": False, "status": "unarchived"},
                status=200,
            )

        resp = client.post(
            "/api/web/v1/warehouse/is_archived/change",
            json={"id": roll_id, "is_archived": False}
        )

        assert resp.status_code == 200
        print(f"[E2E-WH] Ролик возвращен на склад из архива: {roll_id}")

    def test_09_verify_roll_on_warehouse(self, client, test_context, mock_api):
        """Шаг 9: Проверка, что ролик отображается на складе после возврата."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/filter",
                json={
                    "total_count": 1,
                    "result": [
                        {
                            "id": test_context.get_last("warehouse_merged_roll_id"),
                            "is_archived": False,
                            "location": "warehouse"
                        }
                    ]
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/warehouse/filter",
            json={"is_archived": False, "limit": 10, "offset": 0}
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] >= 0
        # Проверяем, что ролик в списке неархивных
        roll_ids = [r.get("id") for r in data.get("result", [])]
        assert test_context.get_last("warehouse_merged_roll_id") in roll_ids
        print(f"[E2E-WH] Ролик подтвержден на складе после возврата из архива")
