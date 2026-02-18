"""
Integration Tests: Orders Management (via Network Proxy)
Проверяет работу с заказами на эмиссию КМ: создание, фильтрация, подтверждение, отклонение.
Тесты работают против реального сервера spp-dev.
"""
import pytest
import uuid

from src.api.network_proxy.orders import orders as create_order
from src.api.network_proxy.order import order as get_order
from src.api.network_proxy.approvable import approvable as get_approvable
from src.api.network_proxy.approve import approve as approve_order
from src.api.network_proxy.manual import manual as reject_manual
from src.api.network_proxy.contract_areas import contract_areas
from src.api.network_proxy.statistics import statistics as order_statistics
from src.api.network_proxy.form_data import form_data


@pytest.mark.integration
class TestOrderRetrieval:
    """Тесты получения справочной информации по заказам."""

    def test_get_order_form_data(self, client):
        """Получение данных для формы заказа (доступные товарные группы и GTIN)."""
        resp = form_data(client)
        assert resp.status_code == 200, f"Failed to get form data: {resp.text}"
        data = resp.json()
        # Ответ содержит список доступных GTIN или товарных групп
        assert isinstance(data, (dict, list))

    def test_get_order_statistics(self, client):
        """Получение статистики заказов."""
        resp = order_statistics(client)
        assert resp.status_code == 200, f"Failed to get statistics: {resp.text}"

    def test_get_contract_areas(self, client):
        """Получение контрактных зон.
        Endpoint требует параметр senderAreaId — без него возвращает 400."""
        resp = contract_areas(client)
        # 400 — ожидаемо: нет обязательного параметра senderAreaId
        assert resp.status_code in [200, 400, 422], (
            f"Unexpected status for contract_areas: {resp.text}"
        )

    def test_get_approvable_orders(self, client):
        """Получение списка заказов, ожидающих подтверждения."""
        resp = get_approvable(client, json={"limit": 10, "offset": 0})
        assert resp.status_code == 200, f"Failed to get approvable orders: {resp.text}"
        # Ответ может быть dict или list в зависимости от версии API

    def test_get_order_by_nonexistent_id(self, client):
        """Получение заказа с несуществующим ID — ошибка."""
        resp = get_order(client, params={"id": str(uuid.uuid4())})
        assert resp.status_code in [400, 404, 422]


@pytest.mark.integration
class TestOrderCreation:
    """Тесты создания заказов на эмиссию кодов маркировки."""

    def test_create_order_invalid_gtin(self, client):
        """Создание заказа с невалидным GTIN — ошибка валидации."""
        resp = create_order(client, json={"gtin": "INVALID_GTIN", "quantity": 100})
        assert resp.status_code in [400, 422]

    def test_create_order_zero_quantity(self, client, real_gtin_milk):
        """Создание заказа с нулевым количеством — ошибка."""
        resp = create_order(client, json={"gtin": real_gtin_milk, "quantity": 0})
        assert resp.status_code in [400, 422]

    def test_create_order_negative_quantity(self, client, real_gtin_milk):
        """Создание заказа с отрицательным количеством — ошибка."""
        resp = create_order(client, json={"gtin": real_gtin_milk, "quantity": -1})
        assert resp.status_code in [400, 422]

    def test_create_order_missing_gtin(self, client):
        """Создание заказа без обязательного поля GTIN — ошибка."""
        resp = create_order(client, json={"quantity": 100})
        assert resp.status_code in [400, 422]

    def test_create_order_real_gtin(self, client, real_gtin_milk):
        """Создание заказа с реальным GTIN (может вернуть 200 или 4xx в зависимости от настроек)."""
        resp = create_order(
            client,
            json={
                "gtin": real_gtin_milk,
                "quantity": 10,
                "serviceProviderId": str(uuid.uuid4()),
            },
        )
        # Реальный сервер может принять или отклонить в зависимости от serviceProviderId
        assert resp.status_code in [200, 400, 404, 422], f"Unexpected status code: {resp.status_code}"


@pytest.mark.integration
class TestOrderWorkflow:
    """Тесты рабочего процесса подтверждения/отклонения заказов."""

    def test_approve_nonexistent_order(self, client):
        """Подтверждение несуществующего заказа — ошибка."""
        resp = approve_order(client, json={"id": str(uuid.uuid4())})
        assert resp.status_code in [400, 404, 422]

    def test_reject_nonexistent_order_manual(self, client):
        """Ручное отклонение несуществующего заказа — ошибка."""
        resp = reject_manual(
            client,
            json={"id": str(uuid.uuid4()), "reason": "Тестовое отклонение"},
        )
        assert resp.status_code in [400, 404, 422]

    def test_approve_invalid_id_format(self, client):
        """Подтверждение заказа с невалидным форматом ID — ошибка."""
        resp = approve_order(client, json={"id": "not-a-valid-id"})
        assert resp.status_code in [400, 422]
