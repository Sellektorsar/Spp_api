"""
E2E Tests: Aggregation Cycle
Сценарий: агрегация кодов в упаковки и поддоны → отправка отчёта об агрегации.

Шаги:
1. Создать производственную линию
2. Запустить рабочую смену и добавить коды
3. Завершить смену
4. Создать сессию агрегации
5. Добавить коды в сессию (из смены)
6. Сформировать упаковки (короба)
7. Сформировать поддон из упаковок
8. Завершить сессию агрегации
9. Отправить отчёт об агрегации
"""
import pytest
import responses
import uuid
import datetime

from src.api.line.create import create as create_line
from src.api.work_shift.start import start as start_shift
from src.api.work_shift.add_code import add_code
from src.api.work_shift.finish import finish as finish_shift
from src.api.aggregation_session.create import create as create_agg_session
from src.api.aggregation_session.start import start as start_agg_session
from src.api.aggregation_session.add_codes import add_codes as agg_add_codes
from src.api.aggregation_session.add_package import add_package
from src.api.aggregation_session.add_pallet import add_pallet
from src.api.aggregation_session.get_stats import get_stats
from src.api.aggregation_session.finish import finish as finish_agg_session
from src.api.report.send_aggregation import send_aggregation
from src.models import CreateInput, WorkShiftStart, WorkShiftCodeWithVariableWeight, LINETYPE, ProductGroup, ProductionType


GTIN = "04606203399737"
INN = "7700000000"


@pytest.mark.e2e
@pytest.mark.order(3)
class TestAggregationCycle:
    """
    E2E Сценарий: Полный цикл агрегации — производство → упаковка → поддон → отчётность.
    """

    def test_01_create_line(self, client, test_context, mock_api):
        """Шаг 1: Создание производственной линии для агрегации."""
        line_id = str(uuid.uuid4())
        line_number = 301

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
                name="Aggregation E2E Line",
                line_type=LINETYPE.integer_1,
                product_group=ProductGroup.milk,
                production_type=ProductionType.integer_1,
            ),
        )

        assert resp.status_code == 200
        data = resp.json()
        test_context.add("agg_line_number", data["number"])
        print(f"[E2E-AGG] Линия создана: {data['number']}")

    def test_02_start_shift_and_scan(self, client, test_context, mock_api):
        """Шаг 2: Старт смены и сканирование кодов."""
        line_number = test_context.get_last("agg_line_number")
        assert line_number, "agg_line_number отсутствует"

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
            batch="BATCH-AGG-001",
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
        test_context.add("agg_shift_id", data["id"])

        # Добавляем 20 кодов (для 2 упаковок по 10)
        codes = [f"0104606203399737215agg{i:03d}93dGVzdA==" for i in range(20)]
        test_context.add("agg_codes", codes)

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
                body=WorkShiftCodeWithVariableWeight(line_number=line_number, code=code_str),
            )
            assert resp.status_code == 200

        print(f"[E2E-AGG] Смена {data['id']} запущена, добавлено {len(codes)} кодов")

    def test_03_finish_shift(self, client, test_context, mock_api):
        """Шаг 3: Завершение рабочей смены."""
        shift_id = test_context.get_last("agg_shift_id")
        assert shift_id, "agg_shift_id отсутствует"

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/finish",
                json={"id": shift_id, "status": "finished"},
                status=200,
            )

        resp = finish_shift(client, json={"id": shift_id})
        assert resp.status_code == 200
        print(f"[E2E-AGG] Смена завершена: {shift_id}")

    def test_04_create_aggregation_session(self, client, test_context, mock_api):
        """Шаг 4: Создание сессии агрегации."""
        session_id = str(uuid.uuid4())

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/dashboard/create",
                json={"id": session_id, "name": "AGG E2E Session"},
                status=200,
            )

        resp = create_agg_session(client, json={"name": "AGG E2E Session"})
        assert resp.status_code == 200
        data = resp.json()
        test_context.add("agg_session_id", data["id"])
        print(f"[E2E-AGG] Сессия агрегации создана: {data['id']}")

    def test_05_start_aggregation_session(self, client, test_context, mock_api):
        """Шаг 5: Запуск сессии агрегации."""
        session_id = test_context.get_last("agg_session_id")
        line_number = test_context.get_last("agg_line_number")
        assert session_id and line_number, "agg_session_id или agg_line_number отсутствует"

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/pallets/start",
                json={"id": session_id, "status": "active"},
                status=200,
            )

        resp = start_agg_session(client, json={"id": session_id, "line_number": line_number})
        assert resp.status_code == 200
        print(f"[E2E-AGG] Сессия агрегации запущена: {session_id}")

    def test_06_add_codes_to_session(self, client, test_context, mock_api):
        """Шаг 6: Добавление кодов маркировки в сессию агрегации."""
        session_id = test_context.get_last("agg_session_id")
        codes = test_context.get_last("agg_codes")
        assert session_id and codes, "agg_session_id или agg_codes отсутствуют"

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/vision/add_codes",
                json={"status": "ok", "added_count": len(codes)},
                status=200,
            )

        resp = agg_add_codes(client, json={"id": session_id, "codes": codes})
        assert resp.status_code == 200
        print(f"[E2E-AGG] В сессию добавлено {len(codes)} кодов")

    def test_07_add_packages(self, client, test_context, mock_api):
        """Шаг 7: Формирование транспортных упаковок (коробов)."""
        session_id = test_context.get_last("agg_session_id")
        assert session_id, "agg_session_id отсутствует"

        package_codes = [f"0038006019111115000000000{i}" for i in range(1, 3)]
        test_context.add("agg_package_codes", package_codes)

        for pkg_code in package_codes:
            if mock_api:
                mock_api.add(
                    responses.POST,
                    f"{client.base_url}/api/web/v1/aggregation_session/pallets/add_package",
                    json={"package_code": pkg_code, "codes_count": 10},
                    status=200,
                )
            resp = add_package(client, json={"id": session_id, "package_code": pkg_code})
            assert resp.status_code == 200

        print(f"[E2E-AGG] Сформировано {len(package_codes)} упаковок")

    def test_08_add_pallet(self, client, test_context, mock_api):
        """Шаг 8: Формирование поддона из упаковок."""
        session_id = test_context.get_last("agg_session_id")
        assert session_id, "agg_session_id отсутствует"

        pallet_code = "00380060191111150000000099"

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/pallets/add_pallet",
                json={"pallet_code": pallet_code, "packages_count": 2},
                status=200,
            )

        resp = add_pallet(client, json={"id": session_id, "pallet_code": pallet_code})
        assert resp.status_code == 200
        test_context.add("agg_pallet_code", pallet_code)
        print(f"[E2E-AGG] Поддон сформирован: {pallet_code}")

    def test_09_check_stats(self, client, test_context, mock_api):
        """Шаг 9: Проверка статистики сессии агрегации."""
        session_id = test_context.get_last("agg_session_id")
        assert session_id, "agg_session_id отсутствует"

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/dashboard/get_stats",
                json={
                    "id": session_id,
                    "total_codes": 20,
                    "packages": 2,
                    "pallets": 1,
                },
                status=200,
            )

        resp = get_stats(client, json={"id": session_id})
        assert resp.status_code == 200
        data = resp.json()
        print(f"[E2E-AGG] Статистика: {data}")

    def test_10_finish_aggregation_session(self, client, test_context, mock_api):
        """Шаг 10: Завершение сессии агрегации."""
        session_id = test_context.get_last("agg_session_id")
        assert session_id, "agg_session_id отсутствует"

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/pallets/finish",
                json={"id": session_id, "status": "finished"},
                status=200,
            )

        resp = finish_agg_session(client, json={"id": session_id})
        assert resp.status_code == 200
        print(f"[E2E-AGG] Сессия завершена: {session_id}")

    def test_11_send_aggregation_report(self, client, test_context, mock_api):
        """Шаг 11: Отправка отчёта об агрегации в ГИС МТ."""
        session_id = test_context.get_last("agg_session_id")
        assert session_id, "agg_session_id отсутствует"

        report_id = str(uuid.uuid4())

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/report/send_aggregation",
                json={"id": report_id, "status": "new", "type": "aggregation"},
                status=200,
            )

        resp = send_aggregation(client, json={"id_agg_session": session_id})
        assert resp.status_code == 200
        data = resp.json()
        test_context.add("agg_report_id", data.get("id", report_id))
        print(f"[E2E-AGG] Отчёт об агрегации отправлен: {data.get('id')}")
