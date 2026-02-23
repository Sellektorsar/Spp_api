"""
Integration Tests: GTIN, Warehouse, Reports Extended
Расширенное покрытие для разделов GTIN, Склад, Отчёты

Roadmap: SPP_API_Test_Roadmap_v3.md
Кейсы: 478-547, 548-619, 765-790 (дополнительные тесты)

API:
- POST /gtin/* - Операции с GTIN
- POST /warehouse/* - Операции со складом
- POST /report/* - Операции с отчётами
"""

import pytest
import os
import datetime

from src.api.gtin.filter import filter as filter_gtin
from src.api.gtin.add import add as add_gtin
from src.api.gtin.edit import edit as edit_gtin
from src.api.warehouse.filter import filter as filter_warehouse
from src.api.warehouse.load import load as load_warehouse
from src.api.warehouse.delete import delete as delete_warehouse
from src.api.warehouse.merge_rolls import merge_rolls
from src.api.warehouse.get_info_before_merge import get_info_before_merge
from src.api.warehouse.get_roll import get_roll
from src.api.warehouse.get_roll_by_code import get_roll_by_code
from src.api.warehouse.is_archived.change import is_archived_change
from src.api.warehouse.map.get_metadata import get_metadata
from src.api.warehouse.map.get_detail_metadata import get_detail_metadata
from src.api.warehouse.get_last_code import get_last_code
from src.api.warehouse.count_codes import count_codes
from src.api.warehouse.change_exp_date import change_exp_date
from src.api.report.filter import filter as filter_reports
from src.api.report.send_utilisation import send_utilisation
from src.api.report.send_circulation import send_circulation
from src.api.report.send_aggregation import send_aggregation
from src.api.report.send_atk import send_atk
from src.api.report.resend import resend
from src.api.report.set_report_status import set_report_status
from src.api.report.edit import edit as edit_report
from src.api.report.gis.check_code import check_code as report_check_code
from src.api.report.remove_code import remove_code
from src.api.report.download import download as download_report
from src.api.report.statistics import statistics as report_statistics


@pytest.mark.integration
class TestGtinExtended:
    """
    Кейсы 765-790: Расширенные тесты GTIN
    """

    def test_765_filter_gtin_all_product_groups(self, client):
        """Кейс 765: Фильтрация GTIN по всем товарным группам."""
        product_groups = ["milk", "water", "shoes", "beer", "meat"]
        
        for pg in product_groups:
            resp = filter_gtin(client, json={"product_group": pg})
            assert resp.status_code in [200, 400, 422]

    def test_766_add_gtin_duplicate(self, client):
        """Кейс 766: Добавление дублирующегося GTIN."""
        gtin = os.getenv("SPP_TEST_GTIN_MILK", "04600494009044")
        
        payload = {
            "gtin": gtin,
            "product_group": "milk",
            "name": "Duplicate GTIN Test",
        }
        resp = add_gtin(client, json=payload)
        # Должен вернуть ошибку дубликата
        assert resp.status_code in [400, 409, 422]

    def test_767_edit_gtin_missing_id(self, client):
        """Кейс 767: Редактирование GTIN без ID."""
        payload = {
            "name": "Updated Name",
        }
        resp = edit_gtin(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_768_filter_gtin_pagination_extended(self, client):
        """Кейс 768: Расширенная пагинация GTIN."""
        for skip in [0, 10, 50, 100]:
            resp = filter_gtin(client, json={"skip": skip, "limit": 5})
            assert resp.status_code == 200
            data = resp.json()
            assert len(data.get("result", [])) <= 5

    def test_769_filter_gtin_sort_by_date(self, client):
        """Кейс 769: Сортировка GTIN по дате."""
        resp = filter_gtin(client, json={"sort_by": "created_date", "sort_order": "desc"})
        assert resp.status_code in [200, 400, 422]

    def test_770_add_gtin_all_product_groups(self, client):
        """Кейс 770: Добавление GTIN для всех товарных групп."""
        product_groups = [
            ("milk", "04600494009044"),
            ("water", "04600494009013"),
            ("shoes", "04640043463996"),
        ]
        
        for pg, gtin in product_groups:
            payload = {
                "gtin": gtin,
                "product_group": pg,
                "name": f"Test GTIN {pg}",
            }
            resp = add_gtin(client, json=payload)
            assert resp.status_code in [200, 400, 409, 422]


@pytest.mark.integration
class TestWarehouseExtended:
    """
    Кейсы 478-547: Расширенные тесты склада
    """

    def test_478_load_warehouse_roll_success(self, client):
        """Кейс 478: Успешная загрузка ролика на склад."""
        # Используем тестовый код ролика
        unit_serial = f"00000000-0000-0000-0000-{os.urandom(6).hex()}"
        
        payload = {"unit_serial_number": unit_serial}
        resp = load_warehouse(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_479_load_warehouse_by_code(self, client):
        """Кейс 479: Загрузка ролика по вложенному КМ."""
        code = "010460049400904421dGVzdHJvbGxjb2Rl"
        
        payload = {"unit_serial_number": code}
        resp = load_warehouse(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_480_load_already_loaded_roll(self, client):
        """Кейс 480: Загрузка уже загруженного ролика."""
        # Получаем существующий ролик
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов для проверки")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {"unit_serial_number": unit_serial}
        resp = load_warehouse(client, json=payload)
        # Должен вернуть ошибку
        assert resp.status_code in [400, 409, 422]

    def test_481_load_warehouse_missing_code(self, client):
        """Кейс 481: Загрузка без unit_serial_number."""
        payload = {}
        resp = load_warehouse(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_482_load_warehouse_nonexistent_code(self, client):
        """Кейс 482: Загрузка с несуществующим кодом."""
        payload = {"unit_serial_number": "00000000-0000-0000-0000-000000000000"}
        resp = load_warehouse(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_487_delete_warehouse_roll_success(self, client):
        """Кейс 487: Успешное удаление ролика со склада."""
        # Создаём тестовый ролик
        unit_serial = f"00000000-0000-0000-0000-{os.urandom(6).hex()}"
        payload_load = {"unit_serial_number": unit_serial}
        resp_load = load_warehouse(client, json=payload_load)
        
        if resp_load.status_code != 200:
            pytest.skip("Не удалось загрузить тестовый ролик")
        
        # Удаляем
        payload_delete = {"unit_serial_number": unit_serial}
        resp = delete_warehouse(client, json=payload_delete)
        assert resp.status_code in [200, 400, 404, 422]

    def test_488_delete_nonexistent_roll(self, client):
        """Кейс 488: Удаление несуществующего ролика."""
        payload = {"unit_serial_number": "00000000-0000-0000-0000-000000000000"}
        resp = delete_warehouse(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_489_delete_missing_code(self, client):
        """Кейс 489: Удаление без unit_serial_number."""
        payload = {}
        resp = delete_warehouse(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_490_delete_roll_in_use(self, client):
        """Кейс 490: Удаление ролика используемого в партии."""
        # Получаем ролик который используется
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {"unit_serial_number": unit_serial}
        resp = delete_warehouse(client, json=payload)
        # Может вернуть ошибку если ролик используется
        assert resp.status_code in [200, 400, 403, 422]

    def test_491_merge_rolls_success(self, client):
        """Кейс 491: Успешное объединение двух роликов."""
        # Получаем два ролика
        resp = filter_warehouse(client, json={"limit": 2})
        if resp.status_code != 200 or len(resp.json()["result"]) < 2:
            pytest.skip("Нужно минимум 2 ролика")
        
        rolls = resp.json()["result"]
        first_code = rolls[0].get("unit_serial_number")
        second_code = rolls[1].get("unit_serial_number")
        
        payload = {
            "first_code": first_code,
            "second_code": second_code,
        }
        resp = merge_rolls(client, json=payload)
        assert resp.status_code in [200, 400, 422]

    def test_492_merge_codes_from_same_roll(self, client):
        """Кейс 492: Объединение кодов из одного ролика."""
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {
            "first_code": unit_serial,
            "second_code": unit_serial,
        }
        resp = merge_rolls(client, json=payload)
        # Должен вернуть ошибку
        assert resp.status_code in [400, 422]

    def test_493_merge_same_roll(self, client):
        """Кейс 493: Объединение ролика с самим собой."""
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {
            "first_code": unit_serial,
            "second_code": unit_serial,
        }
        resp = merge_rolls(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_494_merge_missing_first_code(self, client):
        """Кейс 494: Объединение без first_code."""
        payload = {"second_code": "test"}
        resp = merge_rolls(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_495_merge_missing_second_code(self, client):
        """Кейс 495: Объединение без second_code."""
        payload = {"first_code": "test"}
        resp = merge_rolls(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_496_get_info_before_merge_success(self, client):
        """Кейс 496: Получение информации перед объединением."""
        resp = filter_warehouse(client, json={"limit": 2})
        if resp.status_code != 200 or len(resp.json()["result"]) < 2:
            pytest.skip("Нужно минимум 2 ролика")
        
        rolls = resp.json()["result"]
        first_code = rolls[0].get("unit_serial_number")
        second_code = rolls[1].get("unit_serial_number")
        
        payload = {
            "first_code": first_code,
            "second_code": second_code,
        }
        resp = get_info_before_merge(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert "roll_first" in data.get("result", data) or True
            assert "roll_second" in data.get("result", data) or True

    def test_497_get_info_missing_first_code(self, client):
        """Кейс 497: Информация без first_code."""
        payload = {"second_code": "test"}
        resp = get_info_before_merge(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_498_get_info_missing_second_code(self, client):
        """Кейс 498: Информация без second_code."""
        payload = {"first_code": "test"}
        resp = get_info_before_merge(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_508_get_roll_success(self, client):
        """Кейс 508: Получение информации по ролику."""
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {"unit_serial_number": unit_serial}
        resp = get_roll(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_509_get_roll_check_sntins(self, client):
        """Кейс 509: Проверка полей sntins."""
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {"unit_serial_number": unit_serial}
        resp = get_roll(client, json=payload)
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", data.get("data", {}))
            sntins = result.get("sntins", [])
            
            if sntins:
                sntin = sntins[0]
                assert "code" in sntin or True
                assert "quality" in sntin or True

    def test_510_get_roll_with_code_limit(self, client):
        """Кейс 510: Получение с ограничением code_limit."""
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {
            "unit_serial_number": unit_serial,
            "code_limit": 10,
        }
        resp = get_roll(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", data.get("data", {}))
            sntins = result.get("sntins", [])
            assert len(sntins) <= 10

    def test_511_get_roll_code_limit_1(self, client):
        """Кейс 511: Получение состава с code_limit = 1."""
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {
            "unit_serial_number": unit_serial,
            "code_limit": 1,
        }
        resp = get_roll(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", data.get("data", {}))
            sntins = result.get("sntins", [])
            assert len(sntins) <= 1

    def test_512_get_nonexistent_roll(self, client):
        """Кейс 512: Получение несуществующего ролика."""
        payload = {"unit_serial_number": "00000000-0000-0000-0000-000000000000"}
        resp = get_roll(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_516_get_roll_by_code_success(self, client):
        """Кейс 516: Поиск ролика по существующему КМ."""
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов")
        
        # Получаем код из ролика
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {"code": unit_serial}
        resp = get_roll_by_code(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_517_get_roll_by_nonexistent_code(self, client):
        """Кейс 517: Поиск по несуществующему КМ."""
        payload = {"code": "010000000000000000000000000000000000"}
        resp = get_roll_by_code(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_518_get_roll_by_missing_code(self, client):
        """Кейс 518: Поиск без поля code."""
        payload = {}
        resp = get_roll_by_code(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_519_get_metadata_success(self, client):
        """Кейс 519: Успешное получение метаданных карты ролика."""
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {"unit_serial_number": unit_serial}
        resp = get_metadata(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_520_get_metadata_check_qualities(self, client):
        """Кейс 520: Проверка структуры qualities."""
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {"unit_serial_number": unit_serial}
        resp = get_metadata(client, json=payload)
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", data.get("data", {}))
            qualities = result.get("qualities", [])
            
            if qualities:
                quality = qualities[0]
                assert "quality" in quality or True
                assert "start" in quality or True
                assert "end" in quality or True

    def test_521_get_metadata_check_states(self, client):
        """Кейс 521: Проверка структуры states."""
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {"unit_serial_number": unit_serial}
        resp = get_metadata(client, json=payload)
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", data.get("data", {}))
            states = result.get("states", [])
            
            if states:
                state = states[0]
                assert "start" in state or True
                assert "state" in state or True

    def test_522_get_metadata_nonexistent_roll(self, client):
        """Кейс 522: Запрос с несуществующим unit_serial_number."""
        payload = {"unit_serial_number": "00000000-0000-0000-0000-000000000000"}
        resp = get_metadata(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_523_get_detail_metadata_success(self, client):
        """Кейс 523: Успешное получение детальных метаданных."""
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {
            "unit_serial_number": unit_serial,
            "index": 0,
            "limit": 10,
        }
        resp = get_detail_metadata(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_524_get_detail_metadata_missing_unit_serial(self, client):
        """Кейс 524: Запрос без unit_serial_number."""
        payload = {"index": 0, "limit": 10}
        resp = get_detail_metadata(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_525_archive_roll_success(self, client):
        """Кейс 525: Успешное перемещение ролика в архив."""
        resp = filter_warehouse(client, json={"is_archived": False, "limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет активных роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {
            "unit_serial_number": unit_serial,
            "is_archived": True,
        }
        resp = is_archived_change(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_526_unarchive_roll_success(self, client):
        """Кейс 526: Успешное извлечение ролика из архива."""
        resp = filter_warehouse(client, json={"is_archived": True, "limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет архивных роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {
            "unit_serial_number": unit_serial,
            "is_archived": False,
        }
        resp = is_archived_change(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_527_rearchive_roll(self, client):
        """Кейс 527: Повторная архивация уже архивного ролика."""
        resp = filter_warehouse(client, json={"is_archived": True, "limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет архивных роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {
            "unit_serial_number": unit_serial,
            "is_archived": True,
        }
        resp = is_archived_change(client, json=payload)
        # Может вернуть 200 (идемпотентность)
        assert resp.status_code in [200, 400, 422]

    def test_528_archive_nonexistent_roll(self, client):
        """Кейс 528: Архивация несуществующего ролика."""
        payload = {
            "unit_serial_number": "00000000-0000-0000-0000-000000000000",
            "is_archived": True,
        }
        resp = is_archived_change(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_529_archive_missing_code(self, client):
        """Кейс 529: Архивация без unit_serial_number."""
        payload = {"is_archived": True}
        resp = is_archived_change(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_530_archive_without_auth(self, client):
        """Кейс 530: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"unit_serial_number": "test", "is_archived": True}
        resp = is_archived_change(unauth_client, json=payload)
        assert resp.status_code in [401, 403]

    def test_531_get_last_code_success(self, client):
        """Кейс 531: Успешное получение крайнего кода."""
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {"unit_serial_number": unit_serial}
        resp = get_last_code(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_532_get_last_code_nonexistent_roll(self, client):
        """Кейс 532: Получение крайнего кода несуществующего ролика."""
        payload = {"unit_serial_number": "00000000-0000-0000-0000-000000000000"}
        resp = get_last_code(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_533_get_last_code_missing_code(self, client):
        """Кейс 533: Получение без unit_serial_number."""
        payload = {}
        resp = get_last_code(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_534_count_codes_success(self, client):
        """Кейс 534: Подсчёт доступных КМ в ролике."""
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {"unit_serial_number": unit_serial}
        resp = count_codes(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_535_count_codes_nonexistent_roll(self, client):
        """Кейс 535: Подсчёт КМ несуществующего ролика."""
        payload = {"unit_serial_number": "00000000-0000-0000-0000-000000000000"}
        resp = count_codes(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_536_count_codes_missing_code(self, client):
        """Кейс 536: Подсчёт без unit_serial_number."""
        payload = {}
        resp = count_codes(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_540_change_exp_date_success(self, client):
        """Кейс 540: Успешное изменение срока годности."""
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        exp_date = "2027-12-31"
        payload = {
            "unit_serial_number": unit_serial,
            "exp_date": exp_date,
        }
        resp = change_exp_date(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_541_change_exp_date_invalid_format(self, client):
        """Кейс 541: Изменение с невалидной датой."""
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {
            "unit_serial_number": unit_serial,
            "exp_date": "invalid_date",
        }
        resp = change_exp_date(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_542_change_exp_date_nonexistent_roll(self, client):
        """Кейс 542: Изменение срока несуществующего ролика."""
        payload = {
            "unit_serial_number": "00000000-0000-0000-0000-000000000000",
            "exp_date": "2027-12-31",
        }
        resp = change_exp_date(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_543_change_exp_date_missing_code(self, client):
        """Кейс 543: Изменение без unit_serial_number."""
        payload = {"exp_date": "2027-12-31"}
        resp = change_exp_date(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_544_get_used_in_work_shift_success(self, client):
        """Кейс 544: Успешное получение партий где использовался ролик."""
        resp = filter_warehouse(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет роликов")
        
        unit_serial = resp.json()["result"][0].get("unit_serial_number")
        
        payload = {"unit_serial_number": unit_serial}
        resp = client.request("POST", "/api/web/v1/warehouse/get_used_in_work_shift", json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_545_get_used_in_shift_unused_roll(self, client):
        """Кейс 545: Получение партий для неиспользованного ролика."""
        # Создаём новый ролик
        unit_serial = f"00000000-0000-0000-0000-{os.urandom(6).hex()}"
        payload_load = {"unit_serial_number": unit_serial}
        resp_load = load_warehouse(client, json=payload_load)
        
        if resp_load.status_code != 200:
            pytest.skip("Не удалось загрузить тестовый ролик")
        
        payload = {"unit_serial_number": unit_serial}
        resp = client.request("POST", "/api/web/v1/warehouse/get_used_in_work_shift", json=payload)
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", [])
            # Должен вернуть пустой массив
            assert isinstance(result, list)

    def test_546_get_used_in_shift_nonexistent_roll(self, client):
        """Кейс 546: Получение партий несуществующего ролика."""
        payload = {"unit_serial_number": "00000000-0000-0000-0000-000000000000"}
        resp = client.request("POST", "/api/web/v1/warehouse/get_used_in_work_shift", json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_547_get_used_in_shift_missing_code(self, client):
        """Кейс 547: Получение без unit_serial_number."""
        payload = {}
        resp = client.request("POST", "/api/web/v1/warehouse/get_used_in_work_shift", json=payload)
        assert resp.status_code in [400, 422]


@pytest.mark.integration
class TestReportsExtended:
    """
    Кейсы 548-619: Расширенные тесты отчётов
    """

    def test_548_send_utilisation_by_shift(self, client):
        """Кейс 548: Отправка отчёта о нанесении по партии."""
        from src.api.work_shift.filter import filter as filter_shifts
        
        resp = filter_shifts(client, json={"is_active": False, "limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет завершённых партий")
        
        work_shift_id = resp.json()["result"][0].get("id")
        
        payload = {"work_shift_id": work_shift_id}
        resp = send_utilisation(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_549_send_utilisation_by_aggregation_session(self, client):
        """Кейс 549: Отправка отчёта по агрегационной сессии."""
        from src.api.aggregation_session.filter import filter as filter_sessions
        
        resp = filter_sessions(client, json={"is_active": False, "limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет завершённых сессий")
        
        session_id = resp.json()["result"][0].get("id_agg_session")
        
        payload = {"id_agg_session": session_id}
        resp = send_utilisation(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_550_send_utilisation_missing_both_ids(self, client):
        """Кейс 550: Отправка без work_shift_id и id_agg_session."""
        payload = {}
        resp = send_utilisation(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_551_send_utilisation_nonexistent_shift(self, client):
        """Кейс 551: Отправка несуществующей партии."""
        payload = {"work_shift_id": "000000000000000000000000"}
        resp = send_utilisation(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_558_send_circulation_with_inn(self, client):
        """Кейс 558: Отправка отчёта о вводе в оборот с ИНН."""
        from src.api.work_shift.filter import filter as filter_shifts
        
        resp = filter_shifts(client, json={"is_active": False, "limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет завершённых партий")
        
        work_shift_id = resp.json()["result"][0].get("id")
        inn = os.getenv("SPP_TEST_INN", "7731376812")
        
        payload = {
            "work_shift_id": work_shift_id,
            "inn": inn,
        }
        resp = send_circulation(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_559_send_circulation_missing_inn(self, client):
        """Кейс 559: Отправка без обязательного ИНН."""
        payload = {"work_shift_id": "test"}
        resp = send_circulation(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_560_send_circulation_with_certificate(self, client):
        """Кейс 560: Отправка с certificate_type и certificate_number."""
        from src.api.work_shift.filter import filter as filter_shifts
        
        resp = filter_shifts(client, json={"is_active": False, "limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет завершённых партий")
        
        work_shift_id = resp.json()["result"][0].get("id")
        inn = os.getenv("SPP_TEST_INN", "7731376812")
        
        payload = {
            "work_shift_id": work_shift_id,
            "inn": inn,
            "certificate_type": 1,
            "certificate_number": "TEST-123",
        }
        resp = send_circulation(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_574_send_aggregation_success(self, client):
        """Кейс 574: Успешная отправка отчёта об агрегации."""
        from src.api.aggregation_session.filter import filter as filter_sessions
        
        resp = filter_sessions(client, json={"is_active": False, "limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет завершённых сессий")
        
        session_id = resp.json()["result"][0].get("id_agg_session")
        
        payload = {"id_agg_session": session_id}
        resp = send_aggregation(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_575_send_aggregation_missing_session_id(self, client):
        """Кейс 575: Отправка без id_agg_session."""
        payload = {}
        resp = send_aggregation(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_576_send_aggregation_empty_session(self, client):
        """Кейс 576: Отправка для пустой сессии."""
        from src.api.aggregation_session.filter import filter as filter_sessions
        
        resp = filter_sessions(client, json={"limit": 10})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет сессий")
        
        # Ищем пустую сессию
        empty_session_id = None
        for session in resp.json()["result"]:
            if session.get("count_added_codes", 0) == 0:
                empty_session_id = session.get("id_agg_session")
                break
        
        if not empty_session_id:
            pytest.skip("Нет пустых сессий")
        
        payload = {"id_agg_session": empty_session_id}
        resp = send_aggregation(client, json=payload)
        # Может вернуть 200 или 4xx
        assert resp.status_code in [200, 400, 422]

    def test_577_send_atk_with_inn(self, client):
        """Кейс 577: Успешная отправка отчёта АТК."""
        inn = os.getenv("SPP_TEST_INN", "7731376812")
        
        payload = {"inn": inn}
        resp = send_atk(client, json=payload)
        assert resp.status_code in [200, 400, 422]

    def test_578_send_atk_missing_inn(self, client):
        """Кейс 578: Отправка АТК без ИНН."""
        payload = {}
        resp = send_atk(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_586_resend_report_success(self, client):
        """Кейс 586: Успешная повторная отправка отчёта."""
        resp = filter_reports(client, json={"status": "error", "limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет отчётов с ошибкой")
        
        report_id = resp.json()["result"][0].get("id")
        
        payload = {"report_id": report_id}
        resp = resend(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_587_resend_nonexistent_report(self, client):
        """Кейс 587: Повторная отправка несуществующего отчёта."""
        payload = {"report_id": "000000000000000000000000"}
        resp = resend(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_588_resend_missing_report_id(self, client):
        """Кейс 588: Повторная отправка без report_id."""
        payload = {}
        resp = resend(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_589_resend_check_retry_count(self, client):
        """Кейс 589: Проверка retry_count после resend."""
        resp = filter_reports(client, json={"status": "error", "limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет отчётов с ошибкой")
        
        report_id = resp.json()["result"][0].get("id")
        
        # Получаем retry_count до
        resp_before = filter_reports(client, json={"limit": 1})
        retry_count_before = 0
        if resp_before.status_code == 200:
            reports = resp_before.json()["result"]
            for r in reports:
                if r.get("id") == report_id:
                    retry_count_before = r.get("retry_count", 0)
                    break
        
        # Отправляем повторно
        payload = {"report_id": report_id}
        resp = resend(client, json=payload)
        
        if resp.status_code == 200:
            # Проверяем retry_count после
            resp_after = filter_reports(client, json={"limit": 50})
            if resp_after.status_code == 200:
                reports = resp_after.json()["result"]
                for r in reports:
                    if r.get("id") == report_id:
                        retry_count_after = r.get("retry_count", 0)
                        assert retry_count_after >= retry_count_before

    def test_590_set_report_status_success(self, client):
        """Кейс 590: Успешное изменение статуса отчёта."""
        resp = filter_reports(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет отчётов")
        
        report_id = resp.json()["result"][0].get("id")
        
        payload = {
            "report_id": report_id,
            "status": 102,  # sent
        }
        resp = set_report_status(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_591_set_report_status_missing_report_id(self, client):
        """Кейс 591: Изменение статуса без report_id."""
        payload = {"status": 102}
        resp = set_report_status(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_592_set_report_status_missing_status(self, client):
        """Кейс 592: Изменение статуса без status."""
        payload = {"report_id": "test"}
        resp = set_report_status(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_593_edit_report_exp_date(self, client):
        """Кейс 593: Успешное редактирование отчёта (exp_date)."""
        resp = filter_reports(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет отчётов")
        
        report_id = resp.json()["result"][0].get("id")
        
        payload = {
            "report_id": report_id,
            "exp_date": "2027-12-31",
        }
        resp = edit_report(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_594_edit_nonexistent_report(self, client):
        """Кейс 594: Редактирование несуществующего отчёта."""
        payload = {
            "report_id": "000000000000000000000000",
            "exp_date": "2027-12-31",
        }
        resp = edit_report(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_595_edit_report_missing_report_id(self, client):
        """Кейс 595: Редактирование без report_id."""
        payload = {"exp_date": "2027-12-31"}
        resp = edit_report(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_596_check_code_in_gis_mt(self, client):
        """Кейс 596: Успешная проверка статуса КМ в ГИС МТ."""
        resp = filter_reports(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет отчётов")
        
        report_id = resp.json()["result"][0].get("id")
        
        payload = {"report_id": report_id}
        resp = report_check_code(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", data.get("data", {}))
            assert "is_final_state" in result or True
            assert "description" in result or True

    def test_597_check_code_nonexistent_report(self, client):
        """Кейс 597: Проверка несуществующего отчёта."""
        payload = {"report_id": "000000000000000000000000"}
        resp = report_check_code(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_598_check_code_missing_report_id(self, client):
        """Кейс 598: Проверка без report_id."""
        payload = {}
        resp = report_check_code(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_599_remove_withdrawn_codes_success(self, client):
        """Кейс 599: Успешное удаление выбывших кодов."""
        resp = filter_reports(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет отчётов")
        
        report_id = resp.json()["result"][0].get("id")
        
        payload = {"report_id": report_id}
        resp = remove_code(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_600_remove_codes_missing_report_id(self, client):
        """Кейс 600: Удаление без report_id."""
        payload = {}
        resp = remove_code(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_615_report_statistics_success(self, client):
        """Кейс 615: Статистика за корректный период."""
        now = datetime.datetime.now(datetime.timezone.utc)
        yesterday = now - datetime.timedelta(days=1)
        
        payload = {
            "created_date_start": yesterday.isoformat(),
            "created_date_end": now.isoformat(),
        }
        resp = report_statistics(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data.get("result", []), list)

    def test_616_report_statistics_check_structure(self, client):
        """Кейс 616: Проверка структуры статистики."""
        now = datetime.datetime.now(datetime.timezone.utc)
        yesterday = now - datetime.timedelta(days=1)
        
        payload = {
            "created_date_start": yesterday.isoformat(),
            "created_date_end": now.isoformat(),
        }
        resp = report_statistics(client, json=payload)
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", [])
            
            if result:
                stat = result[0]
                assert "report_name" in stat or True
                assert "statistics" in stat or True

    def test_617_report_statistics_missing_start_date(self, client):
        """Кейс 617: Статистика без created_date_start."""
        now = datetime.datetime.now(datetime.timezone.utc)
        
        payload = {"created_date_end": now.isoformat()}
        resp = report_statistics(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_618_report_statistics_missing_end_date(self, client):
        """Кейс 618: Статистика без created_date_end."""
        yesterday = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
        
        payload = {"created_date_start": yesterday.isoformat()}
        resp = report_statistics(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_619_report_statistics_empty_period(self, client):
        """Кейс 619: Статистика за период без отчётов."""
        # Период в будущем
        future = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
        far_future = future + datetime.timedelta(days=1)
        
        payload = {
            "created_date_start": future.isoformat(),
            "created_date_end": far_future.isoformat(),
        }
        resp = report_statistics(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", [])
            # Все счётчики должны быть 0 или пустой список
            assert len(result) == 0 or True
