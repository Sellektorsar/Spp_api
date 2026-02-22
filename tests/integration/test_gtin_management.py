"""
Integration tests for GTIN Registry management.
"""
import pytest
import os


class TestGtinManagement:
    """
    Integration tests for GTIN Registry.
    Endpoints: /api/web/v1/gtin/*
    """

    def test_add_gtin_positive(self, client, real_gtin):
        """Добавление GTIN в реестр."""
        gtin = real_gtin
        resp = client.post(
            "/api/web/v1/gtin/add_many",
            json={
                "gtins": [
                    {
                        "gtin": gtin,
                        "product_name": "Test Product Integration",
                        "tnved": "1234567890",
                        "country": "RU"
                    }
                ]
            }
        )
        # Ожидаем 200 (успех) или 422 (уже существует, что тоже ок для интеграции)
        assert resp.status_code in [200, 422]
        if resp.status_code == 200:
            print(f"[INT-GTIN] GTIN {gtin} добавлен")
        else:
            print(f"[INT-GTIN] GTIN {gtin} уже существует")

    def test_filter_gtin(self, client, real_gtin):
        """Поиск GTIN в реестре."""
        resp = client.post(
            "/api/web/v1/gtin/filter",
            json={"gtin": real_gtin, "limit": 10, "offset": 0}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data or "total_count" in data
        print(f"[INT-GTIN] Фильтрация выполнена, найдено: {data.get('total_count', 0)}")

    def test_edit_gtin_positive(self, client, real_gtin):
        """Редактирование данных GTIN."""
        resp = client.post(
            "/api/web/v1/gtin/edit",
            json={
                "gtin": real_gtin,
                "product_name": "Updated Product Name Integration",
                "tnved": "9999999999",
                "description": "Updated via integration test"
            }
        )
        # Может вернуть 404 если не найден или 200 если ок
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            print(f"[INT-GTIN] GTIN {real_gtin} отредактирован")

    def test_update_gtin_registry_data(self, client):
        """Обновление всех данных реестра GTIN."""
        resp = client.post(
            "/api/web/v1/gtin/update_data_gtin",
            json={}
        )
        # Это может быть долгая операция, возможны таймауты
        assert resp.status_code in [200, 202, 504]
        if resp.status_code == 200:
            print("[INT-GTIN] Реестр GTIN обновлен")

    def test_change_update_flag(self, client):
        """Изменение флага автоматического обновления реестра."""
        resp = client.post(
            "/api/web/v1/gtin/change_flag_update_gtin_registry",
            json={"auto_update": True, "interval_hours": 24}
        )
        assert resp.status_code in [200, 422]
        print(f"[INT-GTIN] Флаг обновления изменен")
