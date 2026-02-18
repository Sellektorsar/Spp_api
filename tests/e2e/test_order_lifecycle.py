"""
E2E Tests: Order Lifecycle
Сценарий: создание заказа на эмиссию КМ → подтверждение → использование кодов в производстве.

Шаги:
1. Создать заказ на эмиссию кодов маркировки
2. Подтвердить заказ
3. Запустить рабочую смену с GTIN из заказа
4. Добавить коды в смену
5. Завершить смену
6. Отправить отчёт о нанесении (utilisation)
7. Отправить отчёт о вводе в оборот (circulation)
"""
import pytest
import responses
import uuid
import datetime

from src.api.network_proxy.orders import orders as create_order
from src.api.network_proxy.approve import approve as approve_order
from src.api.line.create import create as create_line
from src.api.work_shift.start import start as start_shift
from src.api.work_shift.add_code import add_code
from src.api.work_shift.finish import finish as finish_shift
from src.api.report.send_utilisation import send_utilisation
from src.api.report.send_circulation import send_circulation
from src.models import CreateInput, WorkShiftStart, WorkShiftCodeWithVariableWeight, LINETYPE, ProductGroup, ProductionType


GTIN = "04606203399737"
INN = "7700000000"


@pytest.mark.e2e
@pytest.mark.order(2)
class TestOrderLifecycle:
    """
    E2E Сценарий: Полный жизненный цикл заказа — от создания до отчётности.
    """

    def test_01_create_order(self, client, test_context, mock_api):
        """Шаг 1: Создание заказа на эмиссию кодов маркировки."""
        order_id = str(uuid.uuid4())

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/network_proxy/api/network/v1/orders",
                json={"id": order_id, "status": "created", "gtin": GTIN, "quantity": 500},
                status=200,
            )

        resp = create_order(
            client,
            json={"gtin": GTIN, "quantity": 500, "serviceProviderId": str(uuid.uuid4())},
        )

        assert resp.status_code == 200
        data = resp.json()
        assert "id" in data

        test_context.add("order_id", data["id"])
        test_context.add("order_gtin", GTIN)
        print(f"[E2E] Создан заказ: {data['id']}")

    def test_02_approve_order(self, client, test_context, mock_api):
        """Шаг 2: Подтверждение заказа на эмиссию."""
        order_id = test_context.get_last("order_id")
        assert order_id, "order_id от предыдущего шага отсутствует"

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/network_proxy/api/network/v1/orders/approve",
                json={"id": order_id, "status": "approved"},
                status=200,
            )

        resp = approve_order(client, json={"id": order_id})

        assert resp.status_code == 200
        print(f"[E2E] Заказ подтверждён: {order_id}")

    def test_03_create_production_line(self, client, test_context, mock_api):
        """Шаг 3: Создание производственной линии."""
        line_id = str(uuid.uuid4())
        line_number = 201

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/create",
                json={"id": line_id, "number": line_number},
                status=200,
            )

        resp = create_line(
            client,
            body=CreateInput(
                name="Order E2E Line",
                line_type=LINETYPE.integer_1,
                product_group=ProductGroup.milk,
                production_type=ProductionType.integer_1,
            ),
        )

        assert resp.status_code == 200
        data = resp.json()
        test_context.add("e2e_line_number", data["number"])
        print(f"[E2E] Создана линия: {data['number']}")

    def test_04_start_work_shift(self, client, test_context, mock_api):
        """Шаг 4: Старт рабочей смены для производства."""
        line_number = test_context.get_last("e2e_line_number")
        assert line_number, "e2e_line_number от предыдущего шага отсутствует"

        shift_id = str(uuid.uuid4())

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/start",
                json={"id": shift_id, "line_number": line_number, "status": "active"},
                status=200,
            )

        payload = WorkShiftStart(
            line_number=line_number,
            gtin=GTIN,
            batch="BATCH-ORDER-001",
            start_date=datetime.datetime.now(datetime.timezone.utc),
            production_date=datetime.datetime.now(datetime.timezone.utc),
            product_group=ProductGroup.milk,
            is_allow_other_gtins=False,
            with_variable_weight=False,
            camera_is_active=False,
        )
        resp = start_shift(client, body=payload)

        assert resp.status_code == 200
        data = resp.json()
        test_context.add("e2e_shift_id", data["id"])
        print(f"[E2E] Смена запущена: {data['id']}")

    def test_05_scan_codes(self, client, test_context, mock_api):
        """Шаг 5: Сканирование кодов маркировки в смену."""
        line_number = test_context.get_last("e2e_line_number")
        assert line_number, "e2e_line_number от предыдущего шага отсутствует"

        codes = [f"0104606203399737215code{i}93dGVzdA==" for i in range(5)]

        for code_str in codes:
            if mock_api:
                mock_api.add(
                    responses.POST,
                    f"{client.base_url}/api/web/v1/work_shift/add_code",
                    json={"status": "ok"},
                    status=200,
                )

            resp = add_code(
                client,
                body=WorkShiftCodeWithVariableWeight(
                    line_number=line_number,
                    code=code_str,
                ),
            )
            assert resp.status_code == 200

        print(f"[E2E] Добавлено {len(codes)} кодов в смену")

    def test_06_finish_shift(self, client, test_context, mock_api):
        """Шаг 6: Завершение рабочей смены."""
        shift_id = test_context.get_last("e2e_shift_id")
        assert shift_id, "e2e_shift_id от предыдущего шага отсутствует"

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/finish",
                json={"id": shift_id, "status": "finished"},
                status=200,
            )

        resp = finish_shift(client, json={"id": shift_id})

        assert resp.status_code == 200
        print(f"[E2E] Смена завершена: {shift_id}")

    def test_07_send_utilisation_report(self, client, test_context, mock_api):
        """Шаг 7: Отправка отчёта о нанесении (utilisation)."""
        shift_id = test_context.get_last("e2e_shift_id")
        assert shift_id, "e2e_shift_id от предыдущего шага отсутствует"

        report_id = str(uuid.uuid4())

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/send_utilisation",
                json={"id": report_id, "status": "new", "type": "utilisation"},
                status=200,
            )

        resp = send_utilisation(client, json={"work_shift_id": shift_id, "inn": INN})

        assert resp.status_code == 200
        data = resp.json()
        test_context.add("utilisation_report_id", data.get("id", report_id))
        print(f"[E2E] Отчёт о нанесении создан: {data.get('id')}")

    def test_08_send_circulation_report(self, client, test_context, mock_api):
        """Шаг 8: Отправка отчёта о вводе в оборот (circulation)."""
        shift_id = test_context.get_last("e2e_shift_id")
        assert shift_id, "e2e_shift_id от предыдущего шага отсутствует"

        report_id = str(uuid.uuid4())

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/send_circulation",
                json={"id": report_id, "status": "new", "type": "circulation"},
                status=200,
            )

        resp = send_circulation(client, json={"work_shift_id": shift_id, "inn": INN})

        assert resp.status_code == 200
        data = resp.json()
        test_context.add("circulation_report_id", data.get("id", report_id))
        print(f"[E2E] Отчёт о вводе в оборот создан: {data.get('id')}")
