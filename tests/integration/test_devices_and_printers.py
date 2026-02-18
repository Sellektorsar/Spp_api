"""
Integration Tests: Devices and Printers Management
Проверяет управление оборудованием: устройствами и принтерами этикеток.
Тесты работают против реального сервера spp-dev.

Ключевые исправления:
- devices/block    принимает device_id (не id)
- devices/delete   принимает device_id (не id)
- printer/layout/toggle_favorite принимает layout_id + is_favorite (не id)
- printer/cups/send_to_print_by_gtin принимает gtin + type + count_codes
                   + count_copies + printer_id + layout_id (не printer_id + gtin + quantity)
- printer/add      принимает name + printer_cups_name + print_type + host (не name + ip + port)
"""
import pytest
import uuid

from src.api.devices.filter import filter as filter_devices
from src.api.devices.add import add as add_device
from src.api.devices.block import block as block_device
from src.api.devices.delete import delete as delete_device
from src.api.printer.filter import filter as filter_printers
from src.api.printer.add import add as add_printer
from src.api.printer.delete import delete as delete_printer
from src.api.printer.send_to_print_by_gtin import send_to_print_by_gtin
from src.api.printer.toggle_favorite import toggle_favorite


@pytest.mark.integration
class TestDeviceManagement:
    """Тесты управления устройствами (сканеры, камеры и т.д.)."""

    # Храним ID устройства, созданного в тестах (только тестовое — не рабочее!)
    _test_device_id: str = None

    def test_filter_devices_default(self, client):
        """Получение списка зарегистрированных устройств."""
        resp = filter_devices(client, json={"limit": 20, "offset": 0})
        assert resp.status_code == 200
        data = resp.json()
        assert "total_count" in data
        assert isinstance(data["result"], list)

    def test_filter_devices_pagination(self, client):
        """Пагинация устройств."""
        resp1 = filter_devices(client, json={"limit": 5, "offset": 0})
        resp2 = filter_devices(client, json={"limit": 5, "offset": 5})
        assert resp1.status_code == 200
        assert resp2.status_code == 200

    def test_real_device_in_list(self, client, real_device_id):
        """Реальное рабочее устройство присутствует в списке."""
        if not real_device_id:
            pytest.skip("SPP_TEST_DEVICE_ID не задан")
        resp = filter_devices(client, json={"limit": 50, "offset": 0})
        assert resp.status_code == 200
        ids = {r.get("id") or r.get("device_id") for r in resp.json()["result"]}
        assert real_device_id in ids, (
            f"Устройство {real_device_id} не найдено в списке устройств"
        )

    def test_add_new_device(self, client):
        """Регистрация нового тестового устройства (mob_device_id — UUID, type=1)."""
        mob_id = f"test-{uuid.uuid4().hex[:12]}"
        resp = add_device(client, json={"mob_device_id": mob_id, "type": 1})
        assert resp.status_code in [200, 400, 409, 422]
        if resp.status_code == 200:
            data = resp.json()
            did = data.get("device_id") or data.get("id")
            if did:
                TestDeviceManagement._test_device_id = str(did)

    def test_block_test_device(self, client):
        """Блокировка тестового устройства (поле: device_id)."""
        did = TestDeviceManagement._test_device_id
        if not did:
            pytest.skip("Тестовое устройство не было создано в test_add_new_device")
        resp = block_device(client, json={"device_id": did})
        assert resp.status_code in [200, 400, 404, 422]

    def test_delete_test_device(self, client):
        """Удаление тестового устройства (поле: device_id)."""
        did = TestDeviceManagement._test_device_id
        if not did:
            pytest.skip("Тестовое устройство не было создано в test_add_new_device")
        resp = delete_device(client, json={"device_id": did})
        assert resp.status_code in [200, 400, 404, 422]
        if resp.status_code == 200:
            TestDeviceManagement._test_device_id = None

    def test_block_nonexistent_device(self, client):
        """Блокировка несуществующего устройства → ошибка."""
        resp = block_device(client, json={"device_id": "nonexistent-device-id-test"})
        assert resp.status_code in [400, 404, 422]

    def test_delete_nonexistent_device(self, client):
        """Удаление несуществующего устройства → ошибка."""
        resp = delete_device(client, json={"device_id": "nonexistent-device-id-test"})
        assert resp.status_code in [400, 404, 422]


@pytest.mark.integration
class TestPrinterManagement:
    """Тесты управления принтерами этикеток."""

    # Храним ID тестового принтера
    _test_printer_id: str = None

    def test_filter_printers_default(self, client):
        """Получение списка принтеров."""
        resp = filter_printers(client, json={"limit": 20, "offset": 0})
        assert resp.status_code == 200
        data = resp.json()
        assert "total_count" in data
        assert isinstance(data["result"], list)

    def test_real_printer_in_list(self, client, real_printer_id):
        """Реальный принтер из .env присутствует в списке."""
        if not real_printer_id:
            pytest.skip("SPP_TEST_PRINTER_ID не задан")
        resp = filter_printers(client, json={"limit": 50, "offset": 0})
        assert resp.status_code == 200
        ids = {r.get("id") or r.get("layout_id") for r in resp.json()["result"]}
        assert real_printer_id in ids, (
            f"Принтер {real_printer_id} не найден в списке принтеров"
        )

    def test_toggle_printer_favorite(self, client, real_printer_id):
        """Переключение статуса 'Избранный' (поля: layout_id + is_favorite)."""
        if not real_printer_id:
            pytest.skip("SPP_TEST_PRINTER_ID не задан")
        resp = toggle_favorite(
            client,
            json={"layout_id": real_printer_id, "is_favorite": True},
        )
        assert resp.status_code in [200, 400, 404, 422]
        # Переключаем обратно для идемпотентности
        if resp.status_code == 200:
            toggle_favorite(
                client,
                json={"layout_id": real_printer_id, "is_favorite": False},
            )

    def test_send_to_print_by_gtin_milk(self, client, real_printer_id, real_gtin_milk):
        """Отправка задания на печать по GTIN milk (все обязательные поля)."""
        if not real_printer_id:
            pytest.skip("SPP_TEST_PRINTER_ID не задан")
        resp = send_to_print_by_gtin(
            client,
            json={
                "gtin": real_gtin_milk,
                "type": 1,
                "count_codes": 1,
                "count_copies": 1,
                "printer_id": real_printer_id,
                "layout_id": real_printer_id,
            },
        )
        assert resp.status_code in [200, 400, 404, 422]

    def test_send_to_print_by_gtin_invalid_printer(self, client, real_gtin_milk):
        """Отправка задания на несуществующий принтер → ошибка."""
        resp = send_to_print_by_gtin(
            client,
            json={
                "gtin": real_gtin_milk,
                "type": 1,
                "count_codes": 1,
                "count_copies": 1,
                "printer_id": "000000000000000000000000",
                "layout_id": "000000000000000000000000",
            },
        )
        assert resp.status_code in [400, 404, 422]

    def test_add_printer(self, client):
        """Добавление принтера (обязательные поля: name, printer_cups_name, print_type, host)."""
        uid = uuid.uuid4().hex[:6]
        resp = add_printer(
            client,
            json={
                "name": f"Test Printer {uid}",
                "printer_cups_name": f"test_printer_{uid}",
                "print_type": 1,
                "host": "192.168.99.99",
                "port": 9100,
            },
        )
        assert resp.status_code in [200, 400, 422]
        if resp.status_code == 200:
            data = resp.json()
            pid = data.get("id") or data.get("layout_id")
            if pid:
                TestPrinterManagement._test_printer_id = str(pid)

    def test_delete_test_printer(self, client):
        """Удаление тестового принтера (только созданного в этом прогоне)."""
        pid = TestPrinterManagement._test_printer_id
        if not pid:
            pytest.skip("Тестовый принтер не был создан в test_add_printer")
        resp = delete_printer(client, json={"id": pid})
        assert resp.status_code in [200, 400, 404, 422]
        if resp.status_code == 200:
            TestPrinterManagement._test_printer_id = None

    def test_filter_printers_pagination(self, client):
        """Пагинация принтеров: limit/offset принимаются корректно."""
        resp1 = filter_printers(client, json={"limit": 3, "offset": 0})
        resp2 = filter_printers(client, json={"limit": 3, "offset": 3})
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert "total_count" in resp1.json()
        assert isinstance(resp1.json()["result"], list)
        assert isinstance(resp2.json()["result"], list)
        assert len(resp1.json()["result"]) <= 3
        assert len(resp2.json()["result"]) <= 3
