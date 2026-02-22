"""
E2E Tests: Printer Integration
Сценарий: интеграция с принтерами этикеток.

Шаги:
1. Добавление принтера CUPS
2. Добавление принтера ZPL
3. Настройка параметров печати
4. Печать этикеток по кодам
5. Печать этикеток по GTIN
6. Печать палетных этикеток
7. Проверка статуса печати
8. Обработка ошибок печати
9. Удаление принтера
"""
import pytest
import responses
import uuid
import datetime
from typing import Dict, Any

from src.api.printer.add import add as add_cups_printer
from src.api.printer.send_to_print_by_codes import send_to_print_by_codes as send_cups_print_by_codes
from src.api.printer.send_to_print_by_gtin import send_to_print_by_gtin as send_cups_print_by_gtin
from src.api.printer.add import add as add_zpl_printer
from src.api.printer.send_to_print_by_codes import send_to_print_by_codes as send_zpl_print_by_codes
from src.api.printer.send_to_print_by_gtin import send_to_print_by_gtin as send_zpl_print_by_gtin
from src.api.printer.delete import delete as delete_printer
from src.api.printer.filter import filter as filter_printers
from src.api.printer.toggle_favorite import toggle_favorite as toggle_layout_favorite
from src.api.printer.layout import filter_layouts
from src.models import AddInput


@pytest.mark.e2e
@pytest.mark.order(14)
class TestPrinterIntegration:
    """
    E2E Сценарий: Интеграция с принтерами этикеток.
    """

    def test_01_add_cups_printer_positive(self, client, test_context, mock_api):
        """Шаг 1: Позитивный сценарий добавления принтера CUPS."""
        printer_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/add",
                json={
                    "id": printer_id,
                    "name": "CUPS Test Printer",
                    "type": "cups",
                    "host": "192.168.1.100",
                    "port": 631,
                    "status": "active",
                    "created_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        printer_data = AddInput(
            name="CUPS Test Printer",
            type="cups",
            host="192.168.1.100",
            port=631,
            owner_name="Test Owner"
        )
        
        resp = add_cups_printer(client, body=printer_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "cups"
        assert data["status"] == "active"
        
        test_context.add("cups_printer_id", data["id"])
        print(f"[E2E-PRINTER] Принтер CUPS добавлен: {data['name']} (ID: {data['id']})")

    def test_02_add_zpl_printer_positive(self, client, test_context, mock_api):
        """Шаг 2: Позитивный сценарий добавления принтера ZPL."""
        printer_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/add",
                json={
                    "id": printer_id,
                    "name": "ZPL Test Printer",
                    "type": "zpl",
                    "host": "192.168.1.101",
                    "port": 9100,
                    "status": "active",
                    "created_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        printer_data = AddInput(
            name="ZPL Test Printer",
            type="zpl",
            host="192.168.1.101",
            port=9100,
            owner_name="Test Owner"
        )
        
        resp = add_zpl_printer(client, body=printer_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["type"] == "zpl"
        assert data["status"] == "active"
        
        test_context.add("zpl_printer_id", data["id"])
        print(f"[E2E-PRINTER] Принтер ZPL добавлен: {data['name']} (ID: {data['id']})")

    def test_03_add_printer_negative_invalid_type(self, client, test_context, mock_api):
        """Шаг 3: Негативный сценарий - добавление принтера с невалидным типом."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/add",
                json={"detail": "Invalid printer type"},
                status=400,
            )

        printer_data = AddInput(
            name="Invalid Type Printer",
            type="invalid_type",  # Невалидный тип
            host="192.168.1.102",
            port=9101,
            owner_name="Test Owner"
        )
        
        resp = add_cups_printer(client, body=printer_data)
        assert resp.status_code == 400
        print(f"[E2E-PRINTER] Негативный тест добавления принтера: статус {resp.status_code}")

    def test_04_add_printer_negative_duplicate_host(self, client, test_context, mock_api):
        """Шаг 4: Негативный сценарий - добавление принтера с дублирующим хостом."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/add",
                json={"detail": "Printer with this host already exists"},
                status=409,
            )

        printer_data = AddInput(
            name="Duplicate Host Printer",
            type="cups",
            host="192.168.1.100",  # Дублирующийся хост
            port=631,
            owner_name="Test Owner"
        )
        
        resp = add_cups_printer(client, body=printer_data)
        assert resp.status_code == 409
        print(f"[E2E-PRINTER] Негативный тест дублирования хоста: статус {resp.status_code}")

    def test_05_filter_printers_positive(self, client, test_context, mock_api):
        """Шаг 5: Позитивный сценарий фильтрации принтеров."""
        cups_printer_id = test_context.get_last("cups_printer_id")
        zpl_printer_id = test_context.get_last("zpl_printer_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/filter",
                json={
                    "total_count": 2,
                    "result": [
                        {
                            "id": cups_printer_id,
                            "name": "CUPS Test Printer",
                            "type": "cups",
                            "host": "192.168.1.100",
                            "port": 631,
                            "status": "active"
                        },
                        {
                            "id": zpl_printer_id,
                            "name": "ZPL Test Printer",
                            "type": "zpl",
                            "host": "192.168.1.101",
                            "port": 9100,
                            "status": "active"
                        }
                    ]
                },
                status=200,
            )

        resp = filter_printers(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] == 2
        assert len(data["result"]) == 2
        print(f"[E2E-PRINTER] Фильтрация принтеров: найдено {data['total_count']} принтеров")

    def test_06_filter_printers_by_type(self, client, test_context, mock_api):
        """Шаг 6: Позитивный сценарий фильтрации принтеров по типу."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/filter",
                json={
                    "total_count": 1,
                    "result": [
                        {
                            "id": test_context.get_last("cups_printer_id"),
                            "name": "CUPS Test Printer",
                            "type": "cups",
                            "host": "192.168.1.100",
                            "port": 631,
                            "status": "active"
                        }
                    ]
                },
                status=200,
            )

        resp = filter_printers(client, json={"type": "cups"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] == 1
        assert data["result"][0]["type"] == "cups"
        print(f"[E2E-PRINTER] Фильтрация принтеров по типу: найдено {data['total_count']} принтеров типа CUPS")

    def test_07_send_cups_print_by_codes_positive(self, client, test_context, mock_api):
        """Шаг 7: Позитивный сценарий печати этикеток по кодам через CUPS."""
        cups_printer_id = test_context.get_last("cups_printer_id")
        test_codes = ["0104606203399737215print00193dGVzdA==", "0104606203399737215print00293dGVzdA=="]
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/cups/send_to_print_by_codes",
                json={
                    "printer_id": cups_printer_id,
                    "status": "sent",
                    "codes_count": len(test_codes),
                    "sent_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = send_cups_print_by_codes(
            client,
            json={
                "printer_id": cups_printer_id,
                "codes": test_codes
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["codes_count"] == len(test_codes)
        print(f"[E2E-PRINTER] Отправлено на печать {len(test_codes)} кодов через CUPS")

    def test_08_send_cups_print_by_gtin_positive(self, client, test_context, mock_api):
        """Шаг 8: Позитивный сценарий печати этикеток по GTIN через CUPS."""
        cups_printer_id = test_context.get_last("cups_printer_id")
        test_gtin = "04606203399737"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/cups/send_to_print_by_gtin",
                json={
                    "printer_id": cups_printer_id,
                    "status": "sent",
                    "gtin": test_gtin,
                    "sent_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = send_cups_print_by_gtin(
            client,
            json={
                "printer_id": cups_printer_id,
                "gtin": test_gtin
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["gtin"] == test_gtin
        print(f"[E2E-PRINTER] Отправлен на печать GTIN {test_gtin} через CUPS")

    def test_09_send_zpl_print_by_codes_positive(self, client, test_context, mock_api):
        """Шаг 9: Позитивный сценарий печати этикеток по кодам через ZPL."""
        zpl_printer_id = test_context.get_last("zpl_printer_id")
        test_codes = ["0104606203399737215zpl00193dGVzdA==", "0104606203399737215zpl00293dGVzdA=="]
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/zpl/send_to_print_by_codes",
                json={
                    "printer_id": zpl_printer_id,
                    "status": "sent",
                    "codes_count": len(test_codes),
                    "sent_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = send_zpl_print_by_codes(
            client,
            json={
                "printer_id": zpl_printer_id,
                "codes": test_codes
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["codes_count"] == len(test_codes)
        print(f"[E2E-PRINTER] Отправлено на печать {len(test_codes)} кодов через ZPL")

    def test_10_send_zpl_print_by_gtin_positive(self, client, test_context, mock_api):
        """Шаг 10: Позитивный сценарий печати этикеток по GTIN через ZPL."""
        zpl_printer_id = test_context.get_last("zpl_printer_id")
        test_gtin = "04606203399737"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/zpl/send_to_print_by_gtin",
                json={
                    "printer_id": zpl_printer_id,
                    "status": "sent",
                    "gtin": test_gtin,
                    "sent_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = send_zpl_print_by_gtin(
            client,
            json={
                "printer_id": zpl_printer_id,
                "gtin": test_gtin
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["gtin"] == test_gtin
        print(f"[E2E-PRINTER] Отправлен на печать GTIN {test_gtin} через ZPL")

    def test_11_boundary_test_large_print_job(self, client, test_context, mock_api):
        """Шаг 11: Граничный тест - большая задача печати."""
        zpl_printer_id = test_context.get_last("zpl_printer_id")
        # Создаем большую задачу печати (1000 кодов)
        large_codes = [f"0104606203399737215large{i:04d}93dGVzdA==" for i in range(1000)]
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/zpl/send_to_print_by_codes",
                json={
                    "printer_id": zpl_printer_id,
                    "status": "sent",
                    "codes_count": len(large_codes),
                    "sent_at": datetime.datetime.now().isoformat(),
                    "processing_time": 45.2
                },
                status=200,
            )

        resp = send_zpl_print_by_codes(
            client,
            json={
                "printer_id": zpl_printer_id,
                "codes": large_codes
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["codes_count"] == len(large_codes)
        assert data["processing_time"] > 40  # Проверяем, что обработка заняла время
        print(f"[E2E-PRINTER] Граничный тест: отправлена на печать задача из {len(large_codes)} кодов")

    def test_12_error_test_printer_not_found(self, client, test_context, mock_api):
        """Шаг 12: Тест обработки ошибок - принтер не найден."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/cups/send_to_print_by_codes",
                json={"detail": "Printer not found"},
                status=404,
            )

        resp = send_cups_print_by_codes(
            client,
            json={
                "printer_id": "00000000-0000-0000-0000-000000000000",  # Несуществующий ID
                "codes": ["0104606203399737215test00193dGVzdA=="]
            }
        )
        assert resp.status_code == 404
        print(f"[E2E-PRINTER] Тест обработки ошибок: принтер не найден")

    def test_13_error_test_printer_offline(self, client, test_context, mock_api):
        """Шаг 13: Тест обработки ошибок - принтер не в сети."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/cups/send_to_print_by_codes",
                json={"detail": "Printer is offline"},
                status=503,
            )

        resp = send_cups_print_by_codes(
            client,
            json={
                "printer_id": test_context.get_last("cups_printer_id"),
                "codes": ["0104606203399737215test00193dGVzdA=="]
            }
        )
        assert resp.status_code == 503
        print(f"[E2E-PRINTER] Тест обработки ошибок: принтер не в сети")

    def test_14_filter_layouts_positive(self, client, test_context, mock_api):
        """Шаг 14: Позитивный сценарий фильтрации макетов этикеток."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/layout/filter",
                json={
                    "total_count": 1,
                    "result": [
                        {
                            "id": str(uuid.uuid4()),
                            "name": "Test Layout",
                            "description": "Test layout for labels",
                            "is_favorite": True,
                            "created_at": datetime.datetime.now().isoformat()
                        }
                    ]
                },
                status=200,
            )

        resp = filter_layouts(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] == 1
        assert data["result"][0]["is_favorite"] is True
        print(f"[E2E-PRINTER] Фильтрация макетов: найдено {data['total_count']} макет")

    def test_15_toggle_layout_favorite_positive(self, client, test_context, mock_api):
        """Шаг 15: Позитивный сценарий изменения статуса макета."""
        layout_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/layout/toggle_favorite",
                json={
                    "id": layout_id,
                    "is_favorite": False,
                    "updated_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = toggle_layout_favorite(
            client,
            json={
                "id": layout_id,
                "is_favorite": False
            }
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_favorite"] is False
        print(f"[E2E-PRINTER] Статус макета изменен: {data['is_favorite']}")

    def test_16_delete_printer_positive(self, client, test_context, mock_api):
        """Шаг 16: Позитивный сценарий удаления принтера."""
        cups_printer_id = test_context.get_last("cups_printer_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/delete",
                json={
                    "id": cups_printer_id,
                    "deleted": True,
                    "deleted_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = delete_printer(client, json={"id": cups_printer_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["deleted"] is True
        print(f"[E2E-PRINTER] Принтер удален: {cups_printer_id}")

    def test_17_cleanup_printer_test_data(self, client, test_context, mock_api):
        """Шаг 17: Очистка - удаление тестовых принтеров."""
        cups_printer_id = test_context.get_last("cups_printer_id")
        zpl_printer_id = test_context.get_last("zpl_printer_id")
        
        # Удаляем CUPS принтер
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/delete",
                json={
                    "id": cups_printer_id,
                    "deleted": True,
                    "deleted_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = delete_printer(client, json={"id": cups_printer_id})
        assert resp.status_code == 200
        
        # Удаляем ZPL принтер
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/printer/delete",
                json={
                    "id": zpl_printer_id,
                    "deleted": True,
                    "deleted_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = delete_printer(client, json={"id": zpl_printer_id})
        assert resp.status_code == 200
        
        print(f"[E2E-PRINTER] Тестовые принтеры удалены для очистки")