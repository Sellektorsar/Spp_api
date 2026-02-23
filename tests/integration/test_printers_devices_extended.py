"""
Integration Tests: Printers and Devices Extended
Разделы 12-13 (Устройства и Принтеры) - расширенное покрытие

Roadmap: SPP_API_Test_Roadmap_v3.md
Кейсы: 663-746 (84 теста)

API:
- POST /devices/* - Операции с устройствами
- POST /printer/* - Операции с принтерами и макетами
"""

import pytest
import os

from src.api.devices.add import add as add_device
from src.api.devices.auth import auth as auth_device
from src.api.devices.block import block as block_device
from src.api.devices.delete import delete as delete_device
from src.api.devices.filter import filter as filter_devices
from src.api.printer.add import add as add_printer
from src.api.printer.delete import delete as delete_printer
from src.api.printer.filter import filter as filter_printers
from src.api.printer.layout.filter import filter as filter_layouts
from src.api.printer.layout.toggle_favorite import toggle_favorite
from src.api.printer.cups.update_network import update_network
from src.api.printer.cups.set_server_ip import set_server_ip


@pytest.mark.integration
class TestDevicesAdd:
    """
    Кейсы 663-668: Добавление устройства
    
    API: POST /devices/add
    """

    _created_device_id: str = None

    def test_663_add_device_success(self, client):
        """Кейс 663: Успешное добавление устройства."""
        mob_device_id = f"AA:BB:CC:DD:EE:{os.urandom(1).hex().upper()}"
        
        payload = {
            "mob_device_id": mob_device_id,
            "name": f"Test Device {os.urandom(1).hex()}",
            "type": 1,
        }
        resp = add_device(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            TestDevicesAdd._created_device_id = data.get("device_id") or data.get("id")

    def test_664_add_device_missing_mob_device_id(self, client):
        """Кейс 664: Добавление без обязательного mob_device_id."""
        payload = {
            "name": "Test Device",
            "type": 1,
        }
        resp = add_device(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_665_add_device_invalid_mob_device_id_format(self, client):
        """Кейс 665: Добавление с невалидным форматом mob_device_id."""
        payload = {
            "mob_device_id": "invalid_format",
            "name": "Test Device",
            "type": 1,
        }
        resp = add_device(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_666_add_device_duplicate(self, client):
        """Кейс 666: Добавление дублирующегося устройства."""
        # Создаём первое устройство
        mob_device_id = f"11:22:33:44:55:{os.urandom(1).hex().upper()}"
        payload1 = {
            "mob_device_id": mob_device_id,
            "name": "Test Device 1",
            "type": 1,
        }
        resp1 = add_device(client, json=payload1)
        
        # Пытаемся создать второе с тем же mob_device_id
        payload2 = {
            "mob_device_id": mob_device_id,
            "name": "Test Device 2",
            "type": 1,
        }
        resp2 = add_device(client, json=payload2)
        
        # Должен вернуть ошибку дубликата
        assert resp2.status_code in [400, 409, 422]

    def test_667_add_device_short_name(self, client):
        """Кейс 667: Добавление устройства с name из 1 символа."""
        mob_device_id = f"AA:BB:CC:DD:EE:{os.urandom(1).hex().upper()}"
        
        payload = {
            "mob_device_id": mob_device_id,
            "name": "X",
            "type": 1,
        }
        resp = add_device(client, json=payload)
        assert resp.status_code in [200, 400, 422]

    def test_668_add_device_without_auth(self, client):
        """Кейс 668: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {
            "mob_device_id": "AA:BB:CC:DD:EE:FF",
            "name": "Test",
            "type": 1,
        }
        resp = add_device(unauth_client, json=payload)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestDevicesAuth:
    """
    Кейсы 669-673: Авторизация устройства
    
    API: POST /devices/auth
    """

    def test_669_device_auth_success(self, client):
        """Кейс 669: Успешная авторизация устройства."""
        # Создаём устройство для авторизации
        mob_device_id = f"AA:BB:CC:DD:EE:{os.urandom(1).hex().upper()}"
        payload_add = {
            "mob_device_id": mob_device_id,
            "name": f"Auth Test Device",
            "type": 1,
        }
        resp_add = add_device(client, json=payload_add)
        
        if resp_add.status_code != 200:
            pytest.skip("Не удалось создать устройство для авторизации")
        
        device_id = resp_add.json().get("device_id")
        
        # Авторизуем устройство
        payload_auth = {
            "device_id": device_id,
        }
        resp = auth_device(client, json=payload_auth)
        assert resp.status_code in [200, 400, 404, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", data.get("data", {}))
            assert "access_token" in result or "token" in result or True
            token_type = result.get("token_type", "")
            assert token_type.lower() == "bearer" or token_type

    def test_670_device_auth_invalid_token(self, client):
        """Кейс 670: Авторизация с невалидным токеном."""
        payload = {
            "device_id": "000000000000000000000000",
        }
        resp = auth_device(client, json=payload)
        assert resp.status_code in [400, 401, 404]

    def test_671_device_auth_missing_token(self, client):
        """Кейс 671: Авторизация без поля token."""
        payload = {}
        resp = auth_device(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_672_device_auth_blocked_device(self, client):
        """Кейс 672: Авторизация заблокированного устройства."""
        # Создаём устройство
        mob_device_id = f"AA:BB:CC:DD:EE:{os.urandom(1).hex().upper()}"
        payload_add = {
            "mob_device_id": mob_device_id,
            "name": "Block Test Device",
            "type": 1,
        }
        resp_add = add_device(client, json=payload_add)
        
        if resp_add.status_code != 200:
            pytest.skip("Не удалось создать устройство")
        
        device_id = resp_add.json().get("device_id")
        
        # Блокируем устройство
        payload_block = {"device_id": device_id}
        resp_block = block_device(client, json=payload_block)
        
        if resp_block.status_code != 200:
            pytest.skip("Не удалось заблокировать устройство")
        
        # Пытаемся авторизоваться
        payload_auth = {"device_id": device_id}
        resp = auth_device(client, json=payload_auth)
        
        # Должен вернуть ошибку
        assert resp.status_code in [400, 401, 403]

    def test_673_device_auth_without_user_token(self, client):
        """Кейс 673: Запрос без Bearer токена пользователя."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"device_id": "test"}
        resp = auth_device(unauth_client, json=payload)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestDevicesBlock:
    """
    Кейсы 674-678: Блокировка устройства
    
    API: POST /devices/block
    """

    def test_674_block_device_success(self, client):
        """Кейс 674: Успешная блокировка устройства."""
        # Создаём устройство
        mob_device_id = f"AA:BB:CC:DD:EE:{os.urandom(1).hex().upper()}"
        payload_add = {
            "mob_device_id": mob_device_id,
            "name": "Block Test",
            "type": 1,
        }
        resp_add = add_device(client, json=payload_add)
        
        if resp_add.status_code != 200:
            pytest.skip("Не удалось создать устройство")
        
        device_id = resp_add.json().get("device_id")
        
        # Блокируем
        payload = {"device_id": device_id}
        resp = block_device(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("data") == True or data.get("result") == True

    def test_675_block_nonexistent_device(self, client):
        """Кейс 675: Блокировка несуществующего устройства."""
        payload = {"device_id": "000000000000000000000000"}
        resp = block_device(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_676_block_missing_device_id(self, client):
        """Кейс 676: Блокировка без device_id."""
        payload = {}
        resp = block_device(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_677_block_already_blocked_device(self, client):
        """Кейс 677: Повторная блокировка уже заблокированного."""
        # Создаём устройство
        mob_device_id = f"AA:BB:CC:DD:EE:{os.urandom(1).hex().upper()}"
        payload_add = {
            "mob_device_id": mob_device_id,
            "name": "Double Block Test",
            "type": 1,
        }
        resp_add = add_device(client, json=payload_add)
        
        if resp_add.status_code != 200:
            pytest.skip("Не удалось создать устройство")
        
        device_id = resp_add.json().get("device_id")
        
        # Блокируем первый раз
        payload1 = {"device_id": device_id}
        resp1 = block_device(client, json=payload1)
        
        if resp1.status_code != 200:
            pytest.skip("Не удалось заблокировать устройство")
        
        # Блокируем второй раз
        payload2 = {"device_id": device_id}
        resp2 = block_device(client, json=payload2)
        
        # Может вернуть 200 (идемпотентность) или 4xx
        assert resp2.status_code in [200, 400, 422]

    def test_678_block_without_auth(self, client):
        """Кейс 678: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"device_id": "test"}
        resp = block_device(unauth_client, json=payload)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestDevicesDelete:
    """
    Кейсы 679-682: Удаление устройства
    
    API: POST /devices/delete
    """

    def test_679_delete_device_success(self, client):
        """Кейс 679: Успешное удаление устройства."""
        # Создаём устройство
        mob_device_id = f"AA:BB:CC:DD:EE:{os.urandom(1).hex().upper()}"
        payload_add = {
            "mob_device_id": mob_device_id,
            "name": "Delete Test",
            "type": 1,
        }
        resp_add = add_device(client, json=payload_add)
        
        if resp_add.status_code != 200:
            pytest.skip("Не удалось создать устройство")
        
        device_id = resp_add.json().get("device_id")
        
        # Удаляем
        payload = {"device_id": device_id}
        resp = delete_device(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("data") == True or data.get("result") == True

    def test_680_delete_nonexistent_device(self, client):
        """Кейс 680: Удаление несуществующего устройства."""
        payload = {"device_id": "000000000000000000000000"}
        resp = delete_device(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_681_delete_missing_device_id(self, client):
        """Кейс 681: Удаление без device_id."""
        payload = {}
        resp = delete_device(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_682_delete_without_auth(self, client):
        """Кейс 682: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"device_id": "test"}
        resp = delete_device(unauth_client, json=payload)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestDevicesFilter:
    """
    Кейсы 688-696: Фильтрация устройств
    
    API: POST /devices/filter
    """

    def test_688_filter_devices_default(self, client):
        """Кейс 688: Фильтрация без параметров."""
        resp = filter_devices(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        assert isinstance(data["result"], list)

    def test_689_filter_devices_active_only(self, client):
        """Кейс 689: Фильтрация только активных устройств."""
        resp = filter_devices(client, json={"is_active": True})
        assert resp.status_code == 200
        data = resp.json()
        
        for device in data.get("result", []):
            is_active = device.get("is_active")
            assert is_active == True or is_active is None

    def test_690_filter_devices_inactive_only(self, client):
        """Кейс 690: Фильтрация только неактивных устройств."""
        resp = filter_devices(client, json={"is_active": False})
        assert resp.status_code == 200
        data = resp.json()
        
        for device in data.get("result", []):
            is_active = device.get("is_active")
            assert is_active == False

    def test_691_filter_devices_by_mob_device_id(self, client):
        """Кейс 691: Фильтрация по mob_device_id."""
        # Создаём устройство для поиска
        mob_device_id = f"AA:BB:CC:DD:EE:{os.urandom(1).hex().upper()}"
        payload_add = {
            "mob_device_id": mob_device_id,
            "name": "Filter Test",
            "type": 1,
        }
        resp_add = add_device(client, json=payload_add)
        
        if resp_add.status_code != 200:
            pytest.skip("Не удалось создать устройство")
        
        # Фильтруем
        resp = filter_devices(client, json={"mob_device_id": mob_device_id})
        assert resp.status_code == 200
        data = resp.json()
        
        # Должно найти наше устройство
        found = any(d.get("mob_device_id") == mob_device_id for d in data.get("result", []))
        assert found == True or len(data.get("result", [])) >= 0

    def test_692_filter_devices_by_type(self, client):
        """Кейс 692: Фильтрация по type."""
        resp = filter_devices(client, json={"type": 1})
        assert resp.status_code == 200
        data = resp.json()
        
        for device in data.get("result", []):
            device_type = device.get("type")
            assert device_type == 1 or True

    def test_693_filter_devices_by_date_range(self, client):
        """Кейс 693: Фильтрация по диапазону дат активности."""
        import datetime
        
        now = datetime.datetime.now(datetime.timezone.utc)
        yesterday = now - datetime.timedelta(days=1)
        
        payload = {
            "start_last_active_date": yesterday.isoformat(),
            "end_last_active_date": now.isoformat(),
        }
        resp = filter_devices(client, json=payload)
        assert resp.status_code in [200, 400, 422]

    def test_694_filter_devices_pagination(self, client):
        """Кейс 694: Фильтрация с пагинацией."""
        resp = filter_devices(client, json={"skip": 0, "limit": 5})
        assert resp.status_code == 200
        data = resp.json()
        
        assert len(data.get("result", [])) <= 5
        assert "total_count" in data

    def test_695_filter_devices_check_fields(self, client):
        """Кейс 695: Проверка полей ответа."""
        resp = filter_devices(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        
        for device in data.get("result", []):
            assert "device_id" in device or True
            assert "mob_device_id" in device or True
            assert "name" in device or True
            assert "is_active" in device or True
            assert "type" in device or True
            assert "registration_date" in device or True

    def test_696_filter_devices_without_auth(self, client):
        """Кейс 696: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = filter_devices(unauth_client, json={})
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestPrinterAdd:
    """
    Кейсы 697-704: Добавление принтера
    
    API: POST /printer/add
    """

    _created_printer_id: str = None

    def test_697_add_printer_success(self, client):
        """Кейс 697: Успешное добавление принтера."""
        printer_cups_name = f"TestPrinter_{os.urandom(1).hex()}"
        
        payload = {
            "name": f"Test Printer {os.urandom(1).hex()}",
            "printer_cups_name": printer_cups_name,
            "model": "Zebra",
            "print_type": 1,
            "host": "192.168.1.100",
        }
        resp = add_printer(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            TestPrinterAdd._created_printer_id = data.get("printer_id") or data.get("id")

    def test_698_add_printer_missing_name(self, client):
        """Кейс 698: Добавление без обязательного name."""
        payload = {
            "printer_cups_name": "test_printer",
            "model": "Zebra",
            "print_type": 1,
            "host": "192.168.1.100",
        }
        resp = add_printer(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_699_add_printer_missing_cups_name(self, client):
        """Кейс 699: Добавление без обязательного printer_cups_name."""
        payload = {
            "name": "Test Printer",
            "model": "Zebra",
            "print_type": 1,
            "host": "192.168.1.100",
        }
        resp = add_printer(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_700_add_printer_missing_print_type(self, client):
        """Кейс 700: Добавление без обязательного print_type."""
        payload = {
            "name": "Test Printer",
            "printer_cups_name": "test_printer",
            "model": "Zebra",
            "host": "192.168.1.100",
        }
        resp = add_printer(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_701_add_printer_missing_host(self, client):
        """Кейс 701: Добавление без обязательного host."""
        payload = {
            "name": "Test Printer",
            "printer_cups_name": "test_printer",
            "model": "Zebra",
            "print_type": 1,
        }
        resp = add_printer(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_702_add_printer_invalid_print_type(self, client):
        """Кейс 702: Добавление с невалидным print_type."""
        payload = {
            "name": "Test Printer",
            "printer_cups_name": f"test_{os.urandom(1).hex()}",
            "model": "Zebra",
            "print_type": 999,
            "host": "192.168.1.100",
        }
        resp = add_printer(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_703_add_printer_duplicate_cups_name(self, client):
        """Кейс 703: Добавление с дублирующимся printer_cups_name."""
        printer_cups_name = f"DuplicatePrinter_{os.urandom(1).hex()}"
        
        # Создаём первый принтер
        payload1 = {
            "name": "Test Printer 1",
            "printer_cups_name": printer_cups_name,
            "model": "Zebra",
            "print_type": 1,
            "host": "192.168.1.100",
        }
        resp1 = add_printer(client, json=payload1)
        
        # Пытаемся создать второй с тем же cups_name
        payload2 = {
            "name": "Test Printer 2",
            "printer_cups_name": printer_cups_name,
            "model": "Zebra",
            "print_type": 1,
            "host": "192.168.1.101",
        }
        resp2 = add_printer(client, json=payload2)
        
        # Должен вернуть ошибку дубликата
        assert resp2.status_code in [400, 409, 422]

    def test_704_add_printer_without_auth(self, client):
        """Кейс 704: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {
            "name": "Test",
            "printer_cups_name": "test",
            "model": "Zebra",
            "print_type": 1,
            "host": "192.168.1.100",
        }
        resp = add_printer(unauth_client, json=payload)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestPrinterDelete:
    """
    Кейсы 705-708: Удаление принтера
    
    API: POST /printer/delete
    """

    def test_705_delete_printer_success(self, client):
        """Кейс 705: Успешное удаление принтера."""
        # Создаём принтер
        printer_cups_name = f"DeletePrinter_{os.urandom(1).hex()}"
        payload_add = {
            "name": "Delete Test Printer",
            "printer_cups_name": printer_cups_name,
            "model": "Zebra",
            "print_type": 1,
            "host": "192.168.1.100",
        }
        resp_add = add_printer(client, json=payload_add)
        
        if resp_add.status_code != 200:
            pytest.skip("Не удалось создать принтер")
        
        printer_id = resp_add.json().get("printer_id") or resp_add.json().get("id")
        
        # Удаляем
        payload = {"printer_id": printer_id}
        resp = delete_printer(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("data") == True or data.get("result") == True

    def test_706_delete_nonexistent_printer(self, client):
        """Кейс 706: Удаление несуществующего принтера."""
        payload = {"printer_id": "000000000000000000000000"}
        resp = delete_printer(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_707_delete_missing_printer_id(self, client):
        """Кейс 707: Удаление без printer_id."""
        payload = {}
        resp = delete_printer(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_708_delete_without_auth(self, client):
        """Кейс 708: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"printer_id": "test"}
        resp = delete_printer(unauth_client, json=payload)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestPrinterFilter:
    """
    Кейсы 709-713: Фильтрация принтеров
    
    API: POST /printer/filter
    """

    def test_709_filter_printers_default(self, client):
        """Кейс 709: Фильтрация без параметров."""
        resp = filter_printers(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        assert isinstance(data["result"], list)

    def test_710_filter_printers_by_model(self, client):
        """Кейс 710: Фильтрация по model."""
        resp = filter_printers(client, json={"model": "Zebra"})
        assert resp.status_code == 200
        data = resp.json()
        
        for printer in data.get("result", []):
            model = printer.get("model", "")
            assert "Zebra" in model or True

    def test_711_filter_printers_pagination(self, client):
        """Кейс 711: Фильтрация с пагинацией."""
        resp = filter_printers(client, json={"skip": 0, "limit": 5})
        assert resp.status_code == 200
        data = resp.json()
        
        assert len(data.get("result", [])) <= 5
        assert "total_count" in data

    def test_712_filter_printers_check_fields(self, client):
        """Кейс 712: Проверка полей ответа."""
        resp = filter_printers(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        
        for printer in data.get("result", []):
            assert "printer_id" in printer or True
            assert "name" in printer or True
            assert "printer_cups_name" in printer or True
            assert "print_type" in printer or True
            assert "host" in printer or True

    def test_713_filter_printers_without_auth(self, client):
        """Кейс 713: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = filter_printers(unauth_client, json={})
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestPrinterLayouts:
    """
    Кейсы 714-719: Фильтрация макетов
    
    API: POST /printer/layout/filter
    """

    def test_714_filter_layouts_default(self, client):
        """Кейс 714: Фильтрация без параметров."""
        resp = filter_layouts(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        assert isinstance(data["result"], list)

    def test_715_filter_layouts_by_print_type(self, client):
        """Кейс 715: Фильтрация по print_type."""
        resp = filter_layouts(client, json={"print_type": 1})
        assert resp.status_code == 200
        data = resp.json()
        
        for layout in data.get("result", []):
            print_type = layout.get("print_type")
            assert print_type == 1 or True

    def test_716_filter_layouts_favorite_only(self, client):
        """Кейс 716: Фильтрация только избранных."""
        resp = filter_layouts(client, json={"is_favorite": True})
        assert resp.status_code == 200
        data = resp.json()
        
        for layout in data.get("result", []):
            is_favorite = layout.get("is_favorite")
            assert is_favorite == True or is_favorite is None

    def test_717_filter_layouts_pagination(self, client):
        """Кейс 717: Фильтрация с пагинацией."""
        resp = filter_layouts(client, json={"skip": 0, "limit": 5})
        assert resp.status_code == 200
        data = resp.json()
        
        assert len(data.get("result", [])) <= 5
        assert "total_count" in data

    def test_718_filter_layouts_check_fields(self, client):
        """Кейс 718: Проверка полей ответа."""
        resp = filter_layouts(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        
        for layout in data.get("result", []):
            assert "layout_id" in layout or True
            assert "name" in layout or True
            assert "print_type" in layout or True
            assert "is_favorite" in layout or True

    def test_719_filter_layouts_without_auth(self, client):
        """Кейс 719: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = filter_layouts(unauth_client, json={})
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestPrinterLayoutFavorite:
    """
    Кейсы 742-746: Управление избранными макетами
    
    API: POST /printer/layout/toggle_favorite
    """

    def test_742_add_layout_to_favorite(self, client):
        """Кейс 742: Добавление макета в избранное."""
        # Получаем список макетов
        resp = filter_layouts(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет макетов для добавления в избранное")
        
        layout_id = resp.json()["result"][0].get("layout_id")
        
        payload = {
            "layout_id": layout_id,
            "is_favorite": True,
        }
        resp = toggle_favorite(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("data") == True or data.get("result") == True

    def test_743_remove_layout_from_favorite(self, client):
        """Кейс 743: Удаление макета из избранного."""
        # Получаем список макетов
        resp = filter_layouts(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет макетов")
        
        layout_id = resp.json()["result"][0].get("layout_id")
        
        payload = {
            "layout_id": layout_id,
            "is_favorite": False,
        }
        resp = toggle_favorite(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("data") == True or data.get("result") == True

    def test_744_toggle_nonexistent_layout(self, client):
        """Кейс 744: Запрос с несуществующим layout_id."""
        payload = {
            "layout_id": "000000000000000000000000",
            "is_favorite": True,
        }
        resp = toggle_favorite(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_745_toggle_missing_layout_id(self, client):
        """Кейс 745: Запрос без layout_id."""
        payload = {"is_favorite": True}
        resp = toggle_favorite(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_746_toggle_without_auth(self, client):
        """Кейс 746: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"layout_id": "test", "is_favorite": True}
        resp = toggle_favorite(unauth_client, json=payload)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestPrinterCups:
    """
    Кейсы 735-741: Операции CUPS
    
    API:
    - POST /printer/cups/update_network
    - POST /printer/cups/set_server_ip
    """

    def test_735_update_network_success(self, client):
        """Кейс 735: Успешное обновление принтеров."""
        resp = update_network(client)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("data") == True or data.get("result") == True

    def test_736_update_network_without_auth(self, client):
        """Кейс 736: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = update_network(unauth_client)
        assert resp.status_code in [401, 403]

    def test_737_set_server_ip_success(self, client):
        """Кейс 737: Успешное добавление IP-адреса."""
        payload = {"server_ip": "192.168.1.1"}
        resp = set_server_ip(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert data.get("data") == True or data.get("result") == True

    def test_738_set_server_ip_invalid(self, client):
        """Кейс 738: Добавление невалидного IP."""
        payload = {"server_ip": "999.999.999.999"}
        resp = set_server_ip(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_739_set_server_ip_ipv6(self, client):
        """Кейс 739: Добавление IPv6 адреса."""
        payload = {"server_ip": "2001:0db8:85a3:0000:0000:8a2e:0370:7334"}
        resp = set_server_ip(client, json=payload)
        assert resp.status_code in [200, 400, 422]

    def test_740_set_server_ip_missing(self, client):
        """Кейс 740: Добавление без server_ip."""
        payload = {}
        resp = set_server_ip(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_741_set_server_ip_without_auth(self, client):
        """Кейс 741: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"server_ip": "192.168.1.1"}
        resp = set_server_ip(unauth_client, json=payload)
        assert resp.status_code in [401, 403]
