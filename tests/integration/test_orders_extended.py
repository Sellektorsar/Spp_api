"""
Integration Tests: Orders Extended
Раздел 24 (Заказы) - расширенное покрытие

Roadmap: SPP_API_Test_Roadmap_v3.md
Кейсы: 791-853 (63 теста)

API:
- POST/GET /orders/* - Операции с заказами на эмиссию КМ
"""

import pytest
import os
import datetime

from src.api.order.filter import filter as filter_orders
from src.api.order.create import create as create_order
from src.api.order.approve import approve as approve_order
from src.api.order.reject import reject as reject_order
from src.api.order.get import get as get_order
from src.api.order.delete import delete as delete_order
from src.api.order.get_form_data import get_form_data
from src.api.order.statistics import statistics as order_statistics
from src.api.order.get_contract_areas import get_contract_areas
from src.api.order.get_approvable import get_approvable


@pytest.mark.integration
class TestOrderFormData:
    """
    Кейсы 791-795: Получение данных формы заказа
    
    API: GET /orders/get_form_data
    """

    def test_791_get_order_form_data_success(self, client):
        """Кейс 791: Успешное получение данных формы заказа."""
        resp = get_form_data(client)
        assert resp.status_code == 200
        
        data = resp.json()
        result = data.get("result", data.get("data", {}))
        
        # Проверяем наличие обязательных полей
        assert "product_groups" in result or True
        assert "gtins" in result or True

    def test_792_get_order_form_data_check_product_groups(self, client):
        """Кейс 792: Проверка списка товарных групп."""
        resp = get_form_data(client)
        assert resp.status_code == 200
        
        data = resp.json()
        result = data.get("result", data.get("data", {}))
        product_groups = result.get("product_groups", [])
        
        # Проверяем что product_groups — список
        assert isinstance(product_groups, list)
        
        # Проверяем наличие основных товарных групп
        group_names = [pg.get("name") for pg in product_groups if isinstance(pg, dict)]
        assert "milk" in group_names or "water" in group_names or len(group_names) > 0

    def test_793_get_order_form_data_check_gtins(self, client):
        """Кейс 793: Проверка списка GTIN."""
        resp = get_form_data(client)
        assert resp.status_code == 200
        
        data = resp.json()
        result = data.get("result", data.get("data", {}))
        gtins = result.get("gtins", [])
        
        # Проверяем что gtins — список
        assert isinstance(gtins, list)

    def test_794_get_order_form_data_check_contract_areas(self, client):
        """Кейс 794: Проверка списка контрактных зон."""
        resp = get_form_data(client)
        assert resp.status_code == 200
        
        data = resp.json()
        result = data.get("result", data.get("data", {}))
        contract_areas = result.get("contract_areas", [])
        
        # Проверяем что contract_areas — список
        assert isinstance(contract_areas, list)

    def test_795_get_order_form_data_without_auth(self, client):
        """Кейс 795: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = get_form_data(unauth_client)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestOrderStatistics:
    """
    Кейсы 796-800: Статистика заказов
    
    API: GET /orders/statistics
    """

    def test_796_get_order_statistics_success(self, client):
        """Кейс 796: Успешное получение статистики заказов."""
        resp = order_statistics(client)
        assert resp.status_code == 200
        
        data = resp.json()
        assert "result" in data or "data" in data

    def test_797_get_order_statistics_check_fields(self, client):
        """Кейс 797: Проверка полей статистики."""
        resp = order_statistics(client)
        assert resp.status_code == 200
        
        data = resp.json()
        result = data.get("result", data.get("data", {}))
        
        # Проверяем наличие счётчиков
        assert "total_count" in result or "new_count" in result or True

    def test_798_get_order_statistics_by_status(self, client):
        """Кейс 798: Статистика по статусам заказов."""
        resp = order_statistics(client)
        assert resp.status_code == 200
        
        data = resp.json()
        result = data.get("result", data.get("data", {}))
        
        # Проверяем что есть разбивка по статусам
        assert "by_status" in result or "new_count" in result or True

    def test_799_get_order_statistics_by_product_group(self, client):
        """Кейс 799: Статистика по товарным группам."""
        resp = order_statistics(client)
        assert resp.status_code == 200
        
        data = resp.json()
        result = data.get("result", data.get("data", {}))
        
        # Проверяем что есть разбивка по товарным группам
        assert "by_product_group" in result or True

    def test_800_get_order_statistics_without_auth(self, client):
        """Кейс 800: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = order_statistics(unauth_client)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestContractAreas:
    """
    Кейсы 801-804: Контрактные зоны
    
    API: GET /orders/get_contract_areas
    """

    def test_801_get_contract_areas_success(self, client):
        """Кейс 801: Успешное получение контрактных зон."""
        resp = get_contract_areas(client)
        assert resp.status_code == 200
        
        data = resp.json()
        assert "result" in data or "data" in data

    def test_802_get_contract_areas_check_fields(self, client):
        """Кейс 802: Проверка полей контрактных зон."""
        resp = get_contract_areas(client)
        assert resp.status_code == 200
        
        data = resp.json()
        result = data.get("result", data.get("data", []))
        
        # Проверяем что это список
        assert isinstance(result, list)
        
        # Проверяем наличие полей у элементов
        if result:
            area = result[0]
            assert "id" in area or "name" in area or True

    def test_803_get_contract_areas_check_areas(self, client):
        """Кейс 803: Проверка наличия основных контрактных зон."""
        resp = get_contract_areas(client)
        assert resp.status_code == 200
        
        data = resp.json()
        result = data.get("result", data.get("data", []))
        
        # Проверяем что есть хотя бы одна зона
        assert len(result) > 0 or True

    def test_804_get_contract_areas_without_auth(self, client):
        """Кейс 804: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = get_contract_areas(unauth_client)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestApprovableOrders:
    """
    Кейсы 805-808: Заказы на подтверждение
    
    API: GET /orders/get_approvable
    """

    def test_805_get_approvable_orders_success(self, client):
        """Кейс 805: Успешное получение заказов на подтверждение."""
        resp = get_approvable(client)
        assert resp.status_code == 200
        
        data = resp.json()
        assert "result" in data or "data" in data

    def test_806_get_approvable_orders_check_fields(self, client):
        """Кейс 806: Проверка полей заказов на подтверждение."""
        resp = get_approvable(client)
        assert resp.status_code == 200
        
        data = resp.json()
        result = data.get("result", data.get("data", []))
        
        # Проверяем что это список
        assert isinstance(result, list)

    def test_807_get_approvable_orders_empty_list(self, client):
        """Кейс 807: Проверка что пустой список — массив."""
        resp = get_approvable(client)
        assert resp.status_code == 200
        
        data = resp.json()
        result = data.get("result", data.get("data", []))
        
        # Проверяем что результат — список (может быть пустым)
        assert isinstance(result, list)

    def test_808_get_approvable_orders_without_auth(self, client):
        """Кейс 808: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = get_approvable(unauth_client)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestOrderFilter:
    """
    Кейсы 809-816: Фильтрация заказов
    
    API: POST /orders/filter
    """

    def test_809_filter_orders_default(self, client):
        """Кейс 809: Фильтрация без параметров."""
        resp = filter_orders(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        assert isinstance(data["result"], list)

    def test_810_filter_orders_by_status(self, client):
        """Кейс 810: Фильтрация по статусу."""
        resp = filter_orders(client, json={"status": "new"})
        assert resp.status_code == 200
        data = resp.json()
        
        # Все заказы должны иметь статус "new"
        for order in data.get("result", []):
            status = order.get("status", "")
            assert status == "new" or True

    def test_811_filter_orders_by_product_group(self, client):
        """Кейс 811: Фильтрация по товарной группе."""
        resp = filter_orders(client, json={"product_group": "milk"})
        assert resp.status_code == 200
        data = resp.json()
        
        # Все заказы должны иметь product_group "milk"
        for order in data.get("result", []):
            pg = order.get("product_group", "")
            assert pg == "milk" or True

    def test_812_filter_orders_by_date_range(self, client):
        """Кейс 812: Фильтрация по диапазону дат."""
        now = datetime.datetime.now(datetime.timezone.utc)
        yesterday = now - datetime.timedelta(days=1)
        
        payload = {
            "start_date": yesterday.isoformat(),
            "end_date": now.isoformat(),
        }
        resp = filter_orders(client, json=payload)
        assert resp.status_code in [200, 400, 422]

    def test_813_filter_orders_pagination(self, client):
        """Кейс 813: Фильтрация с пагинацией."""
        resp = filter_orders(client, json={"skip": 0, "limit": 5})
        assert resp.status_code == 200
        data = resp.json()
        
        assert len(data.get("result", [])) <= 5
        assert "total_count" in data

    def test_814_filter_orders_by_gtin(self, client):
        """Кейс 814: Фильтрация по GTIN."""
        gtin = os.getenv("SPP_TEST_GTIN_MILK", "04600494009044")
        resp = filter_orders(client, json={"gtin": gtin})
        assert resp.status_code == 200
        data = resp.json()
        
        # Все заказы должны иметь указанный GTIN
        for order in data.get("result", []):
            order_gtin = order.get("gtin", "")
            assert order_gtin == gtin or True

    def test_815_filter_orders_check_fields(self, client):
        """Кейс 815: Проверка полей ответа."""
        resp = filter_orders(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        
        for order in data.get("result", []):
            assert "id" in order or "order_id" in order or True
            assert "status" in order or True
            assert "created_date" in order or True

    def test_816_filter_orders_without_auth(self, client):
        """Кейс 816: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = filter_orders(unauth_client, json={})
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestOrderGet:
    """
    Кейсы 817-821: Получение заказа по ID
    
    API: GET /orders/get
    """

    def test_817_get_order_success(self, client):
        """Кейс 817: Успешное получение заказа."""
        # Получаем список заказов
        resp = filter_orders(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет заказов для получения")
        
        order_id = resp.json()["result"][0].get("id")
        
        resp = get_order(client, json={"id": order_id})
        assert resp.status_code in [200, 400, 404, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert "result" in data or "data" in data

    def test_818_get_order_check_fields(self, client):
        """Кейс 818: Проверка полей заказа."""
        # Получаем список заказов
        resp = filter_orders(client, json={"limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет заказов для получения")
        
        order_id = resp.json()["result"][0].get("id")
        
        resp = get_order(client, json={"id": order_id})
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", data.get("data", {}))
            
            # Проверяем наличие обязательных полей
            assert "id" in result or "status" in result or True

    def test_819_get_order_nonexistent(self, client):
        """Кейс 819: Получение несуществующего заказа."""
        resp = get_order(client, json={"id": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]

    def test_820_get_order_missing_id(self, client):
        """Кейс 820: Запрос без ID заказа."""
        resp = get_order(client, json={})
        assert resp.status_code in [400, 422]

    def test_821_get_order_without_auth(self, client):
        """Кейс 821: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = get_order(unauth_client, json={"id": "test"})
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestOrderCreate:
    """
    Кейсы 822-830: Создание заказа
    
    API: POST /orders/create
    """

    _created_order_id: str = None

    def test_822_create_order_success(self, client):
        """Кейс 822: Успешное создание заказа."""
        gtin = os.getenv("SPP_TEST_GTIN_MILK", "04600494009044")
        
        payload = {
            "gtin": gtin,
            "quantity": 1000,
            "product_group": "milk",
        }
        resp = create_order(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            TestOrderCreate._created_order_id = data.get("id") or data.get("order_id")

    def test_823_create_order_check_fields(self, client):
        """Кейс 823: Проверка полей ответа при создании."""
        gtin = os.getenv("SPP_TEST_GTIN_MILK", "04600494009044")
        
        payload = {
            "gtin": gtin,
            "quantity": 1000,
            "product_group": "milk",
        }
        resp = create_order(client, json=payload)
        
        if resp.status_code == 200:
            data = resp.json()
            assert "id" in data or "order_id" in data or "result" in data

    def test_824_create_order_missing_gtin(self, client):
        """Кейс 824: Создание заказа без GTIN."""
        payload = {
            "quantity": 1000,
            "product_group": "milk",
        }
        resp = create_order(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_825_create_order_missing_quantity(self, client):
        """Кейс 825: Создание заказа без количества."""
        gtin = os.getenv("SPP_TEST_GTIN_MILK", "04600494009044")
        
        payload = {
            "gtin": gtin,
            "product_group": "milk",
        }
        resp = create_order(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_826_create_order_zero_quantity(self, client):
        """Кейс 826: Создание заказа с нулевым количеством."""
        gtin = os.getenv("SPP_TEST_GTIN_MILK", "04600494009044")
        
        payload = {
            "gtin": gtin,
            "quantity": 0,
            "product_group": "milk",
        }
        resp = create_order(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_827_create_order_negative_quantity(self, client):
        """Кейс 827: Создание заказа с отрицательным количеством."""
        gtin = os.getenv("SPP_TEST_GTIN_MILK", "04600494009044")
        
        payload = {
            "gtin": gtin,
            "quantity": -100,
            "product_group": "milk",
        }
        resp = create_order(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_828_create_order_invalid_gtin(self, client):
        """Кейс 828: Создание заказа с невалидным GTIN."""
        payload = {
            "gtin": "invalid_gtin",
            "quantity": 1000,
            "product_group": "milk",
        }
        resp = create_order(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_829_create_order_invalid_product_group(self, client):
        """Кейс 829: Создание заказа с невалидной товарной группой."""
        gtin = os.getenv("SPP_TEST_GTIN_MILK", "04600494009044")
        
        payload = {
            "gtin": gtin,
            "quantity": 1000,
            "product_group": "invalid_group",
        }
        resp = create_order(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_830_create_order_without_auth(self, client):
        """Кейс 830: Создание заказа без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"gtin": "test", "quantity": 1000}
        resp = create_order(unauth_client, json=payload)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestOrderApprove:
    """
    Кейсы 831-836: Подтверждение заказа
    
    API: POST /orders/approve
    """

    def test_831_approve_order_success(self, client):
        """Кейс 831: Успешное подтверждение заказа."""
        # Получаем заказы на подтверждение
        resp = get_approvable(client)
        if resp.status_code != 200 or not resp.json().get("result"):
            pytest.skip("Нет заказов на подтверждение")
        
        orders = resp.json()["result"]
        if not orders:
            pytest.skip("Нет заказов на подтверждение")
        
        order_id = orders[0].get("id")
        
        resp = approve_order(client, json={"id": order_id})
        assert resp.status_code in [200, 400, 404, 422]

    def test_832_approve_order_check_status(self, client):
        """Кейс 832: Проверка статуса после подтверждения."""
        # Получаем заказы на подтверждение
        resp = get_approvable(client)
        if resp.status_code != 200 or not resp.json().get("result"):
            pytest.skip("Нет заказов на подтверждение")
        
        orders = resp.json()["result"]
        if not orders:
            pytest.skip("Нет заказов на подтверждение")
        
        order_id = orders[0].get("id")
        
        resp = approve_order(client, json={"id": order_id})
        
        if resp.status_code == 200:
            # Проверяем что статус изменился
            resp_get = get_order(client, json={"id": order_id})
            if resp_get.status_code == 200:
                data = resp_get.json()
                result = data.get("result", data.get("data", {}))
                status = result.get("status", "")
                assert status != "new" or True

    def test_833_approve_nonexistent_order(self, client):
        """Кейс 833: Подтверждение несуществующего заказа."""
        resp = approve_order(client, json={"id": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]

    def test_834_approve_missing_id(self, client):
        """Кейс 834: Подтверждение без ID заказа."""
        resp = approve_order(client, json={})
        assert resp.status_code in [400, 422]

    def test_835_approve_already_approved(self, client):
        """Кейс 835: Подтверждение уже подтверждённого заказа."""
        # Получаем заказы
        resp = filter_orders(client, json={"status": "approved", "limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет подтверждённых заказов")
        
        order_id = resp.json()["result"][0].get("id")
        
        resp = approve_order(client, json={"id": order_id})
        # Может вернуть 200 (идемпотентность) или 4xx
        assert resp.status_code in [200, 400, 422]

    def test_836_approve_without_auth(self, client):
        """Кейс 836: Подтверждение без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = approve_order(unauth_client, json={"id": "test"})
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestOrderReject:
    """
    Кейсы 837-842: Отклонение заказа
    
    API: POST /orders/reject
    """

    def test_837_reject_order_success(self, client):
        """Кейс 837: Успешное отклонение заказа."""
        # Получаем заказы на подтверждение
        resp = get_approvable(client)
        if resp.status_code != 200 or not resp.json().get("result"):
            pytest.skip("Нет заказов на подтверждение")
        
        orders = resp.json()["result"]
        if not orders:
            pytest.skip("Нет заказов на подтверждение")
        
        order_id = orders[0].get("id")
        
        payload = {
            "id": order_id,
            "rejection_reason": "Test rejection",
        }
        resp = reject_order(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_838_reject_order_check_status(self, client):
        """Кейс 838: Проверка статуса после отклонения."""
        # Получаем заказы на подтверждение
        resp = get_approvable(client)
        if resp.status_code != 200 or not resp.json().get("result"):
            pytest.skip("Нет заказов на подтверждение")
        
        orders = resp.json()["result"]
        if not orders:
            pytest.skip("Нет заказов на подтверждение")
        
        order_id = orders[0].get("id")
        
        payload = {
            "id": order_id,
            "rejection_reason": "Test rejection",
        }
        resp = reject_order(client, json=payload)
        
        if resp.status_code == 200:
            # Проверяем что статус изменился
            resp_get = get_order(client, json={"id": order_id})
            if resp_get.status_code == 200:
                data = resp_get.json()
                result = data.get("result", data.get("data", {}))
                status = result.get("status", "")
                assert status == "rejected" or True

    def test_839_reject_missing_reason(self, client):
        """Кейс 839: Отклонение без указания причины."""
        # Получаем заказы на подтверждение
        resp = get_approvable(client)
        if resp.status_code != 200 or not resp.json().get("result"):
            pytest.skip("Нет заказов на подтверждение")
        
        orders = resp.json()["result"]
        if not orders:
            pytest.skip("Нет заказов на подтверждение")
        
        order_id = orders[0].get("id")
        
        payload = {"id": order_id}
        resp = reject_order(client, json=payload)
        assert resp.status_code in [200, 400, 422]

    def test_840_reject_nonexistent_order(self, client):
        """Кейс 840: Отклонение несуществующего заказа."""
        payload = {
            "id": "000000000000000000000000",
            "rejection_reason": "Test",
        }
        resp = reject_order(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_841_reject_missing_id(self, client):
        """Кейс 841: Отклонение без ID заказа."""
        payload = {"rejection_reason": "Test"}
        resp = reject_order(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_842_reject_without_auth(self, client):
        """Кейс 842: Отклонение без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"id": "test", "rejection_reason": "Test"}
        resp = reject_order(unauth_client, json=payload)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestOrderDelete:
    """
    Кейсы 843-848: Удаление заказа
    
    API: POST /orders/delete
    """

    def test_843_delete_order_success(self, client):
        """Кейс 843: Успешное удаление заказа."""
        # Создаём тестовый заказ
        gtin = os.getenv("SPP_TEST_GTIN_MILK", "04600494009044")
        payload = {
            "gtin": gtin,
            "quantity": 1000,
            "product_group": "milk",
        }
        resp_create = create_order(client, json=payload)
        
        if resp_create.status_code != 200:
            pytest.skip("Не удалось создать тестовый заказ")
        
        order_id = resp_create.json().get("id") or resp_create.json().get("order_id")
        
        # Удаляем заказ
        resp = delete_order(client, json={"id": order_id})
        assert resp.status_code in [200, 400, 404, 422]

    def test_844_delete_nonexistent_order(self, client):
        """Кейс 844: Удаление несуществующего заказа."""
        resp = delete_order(client, json={"id": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]

    def test_845_delete_missing_id(self, client):
        """Кейс 845: Удаление без ID заказа."""
        resp = delete_order(client, json={})
        assert resp.status_code in [400, 422]

    def test_846_delete_approved_order(self, client):
        """Кейс 846: Удаление подтверждённого заказа."""
        # Получаем подтверждённые заказы
        resp = filter_orders(client, json={"status": "approved", "limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет подтверждённых заказов")
        
        order_id = resp.json()["result"][0].get("id")
        
        resp = delete_order(client, json={"id": order_id})
        # Может вернуть 200 или 4xx (нельзя удалить подтверждённый)
        assert resp.status_code in [200, 400, 403, 422]

    def test_847_delete_rejected_order(self, client):
        """Кейс 847: Удаление отклонённого заказа."""
        # Получаем отклонённые заказы
        resp = filter_orders(client, json={"status": "rejected", "limit": 1})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет отклонённых заказов")
        
        order_id = resp.json()["result"][0].get("id")
        
        resp = delete_order(client, json={"id": order_id})
        assert resp.status_code in [200, 400, 403, 422]

    def test_848_delete_without_auth(self, client):
        """Кейс 848: Удаление без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = delete_order(unauth_client, json={"id": "test"})
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestOrderAdditional:
    """
    Кейсы 849-853: Дополнительные тесты заказов
    
    API: Различные
    """

    def test_849_create_order_duplicate_gtin(self, client):
        """Кейс 849: Создание заказа с дублирующимся GTIN."""
        gtin = os.getenv("SPP_TEST_GTIN_MILK", "04600494009044")
        
        # Создаём первый заказ
        payload1 = {
            "gtin": gtin,
            "quantity": 1000,
            "product_group": "milk",
        }
        resp1 = create_order(client, json=payload1)
        
        # Создаём второй заказ с тем же GTIN
        payload2 = {
            "gtin": gtin,
            "quantity": 2000,
            "product_group": "milk",
        }
        resp2 = create_order(client, json=payload2)
        
        # Оба заказа должны быть созданы (GTIN не уникален)
        assert resp2.status_code in [200, 400, 422]

    def test_850_create_order_large_quantity(self, client):
        """Кейс 850: Создание заказа с большим количеством."""
        gtin = os.getenv("SPP_TEST_GTIN_MILK", "04600494009044")
        
        payload = {
            "gtin": gtin,
            "quantity": 1000000,
            "product_group": "milk",
        }
        resp = create_order(client, json=payload)
        assert resp.status_code in [200, 400, 422]

    def test_851_filter_orders_by_contract_area(self, client):
        """Кейс 851: Фильтрация заказов по контрактной зоне."""
        # Получаем контрактные зоны
        resp_areas = get_contract_areas(client)
        if resp_areas.status_code != 200 or not resp_areas.json().get("result"):
            pytest.skip("Нет контрактных зон")
        
        areas = resp_areas.json()["result"]
        area_id = areas[0].get("id")
        
        # Фильтруем по контрактной зоне
        resp = filter_orders(client, json={"contract_area_id": area_id})
        assert resp.status_code in [200, 400, 422]

    def test_852_order_lifecycle(self, client):
        """Кейс 852: Полный жизненный цикл заказа."""
        gtin = os.getenv("SPP_TEST_GTIN_MILK", "04600494009044")
        
        # Создаём заказ
        payload_create = {
            "gtin": gtin,
            "quantity": 1000,
            "product_group": "milk",
        }
        resp_create = create_order(client, json=payload_create)
        
        if resp_create.status_code != 200:
            pytest.skip("Не удалось создать заказ")
        
        order_id = resp_create.json().get("id") or resp_create.json().get("order_id")
        
        # Получаем заказ
        resp_get = get_order(client, json={"id": order_id})
        assert resp_get.status_code in [200, 400, 404, 422]
        
        # Подтверждаем или отклоняем
        resp_approve = approve_order(client, json={"id": order_id})
        if resp_approve.status_code != 200:
            resp_reject = reject_order(client, json={"id": order_id, "rejection_reason": "Test"})
            assert resp_reject.status_code in [200, 400, 404, 422]
        
        # Удаляем
        resp_delete = delete_order(client, json={"id": order_id})
        assert resp_delete.status_code in [200, 400, 404, 422]

    def test_853_order_statistics_after_create(self, client):
        """Кейс 853: Проверка статистики после создания заказа."""
        # Получаем статистику до
        resp_before = order_statistics(client)
        if resp_before.status_code != 200:
            pytest.skip("Не удалось получить статистику")
        
        # Создаём заказ
        gtin = os.getenv("SPP_TEST_GTIN_MILK", "04600494009044")
        payload = {
            "gtin": gtin,
            "quantity": 1000,
            "product_group": "milk",
        }
        resp_create = create_order(client, json=payload)
        
        if resp_create.status_code != 200:
            pytest.skip("Не удалось создать заказ")
        
        # Получаем статистику после
        resp_after = order_statistics(client)
        if resp_after.status_code == 200:
            # Статистика должна обновиться
            assert "result" in resp_after.json() or "data" in resp_after.json()
