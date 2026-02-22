"""
E2E Tests: Process Interruption and Resumption
Сценарий: прерывание и возобновление процессов.

Шаги:
1. Создание рабочей смены
2. Добавление кодов в смену
3. Прерывание рабочей смены
4. Попытка добавления кодов в прерванную смену
5. Возобновление рабочей смены
6. Завершение возобновленной смены
7. Прерывание и возобновление отгрузки
8. Прерывание и возобновление сессии агрегации
"""
import pytest
import responses
import uuid
import datetime
from typing import Dict, Any

from src.api.line.create import create as create_line
from src.api.work_shift.start import start as start_shift
from src.api.work_shift.add_code import add_code as add_code_to_shift
from src.api.work_shift.finish import finish as finish_shift
from src.api.work_shift.resume import resume as resume_shift
from src.api.shipment.start import start as start_shipment
from src.api.shipment.finish import finish as finish_shipment
from src.api.shipment.resume import resume as resume_shipment
from src.api.aggregation_session.create import create as create_agg_session
from src.api.aggregation_session.start import start as start_agg_session
from src.api.aggregation_session.finish import finish as finish_agg_session
from src.api.aggregation_session.resume import resume as resume_agg_session
from src.models import CreateInput, WorkShiftStart, WorkShiftCodeInput, LINETYPE, ProductGroup, ProductionType


@pytest.mark.e2e
@pytest.mark.order(13)
class TestProcessInterruption:
    """
    E2E Сценарий: Прерывание и возобновление процессов.
    """

    def test_01_create_production_line_for_interruption(self, client, test_context, mock_api):
        """Шаг 1: Создание производственной линии для тестов прерывания."""
        line_id = str(uuid.uuid4())
        line_number = 1001
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/create",
                json={"id": line_id, "number": line_number},
                status=200,
            )

        payload = CreateInput(
            name="Process Interruption Test Line",
            line_type=LINETYPE.integer_1,
            product_group=ProductGroup.milk,
            production_type=ProductionType.integer_1,
        )
        resp = create_line(client, body=payload)
        assert resp.status_code == 200
        data = resp.json()
        test_context.add("interruption_line_number", data["number"])
        print(f"[E2E-INTERRUPTION] Линия для тестов прерывания создана: {data['number']}")

    def test_02_start_work_shift_for_interruption(self, client, test_context, mock_api):
        """Шаг 2: Запуск рабочей смены для тестов прерывания."""
        line_number = test_context.get_last("interruption_line_number")
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
            gtin="04606203399737",
            batch="BATCH-INTERRUPTION-001",
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
        test_context.add("interruption_shift_id", data["id"])
        print(f"[E2E-INTERRUPTION] Смена для тестов прерывания запущена: {data['id']}")

    def test_03_add_codes_to_shift(self, client, test_context, mock_api):
        """Шаг 3: Добавление кодов в смену."""
        line_number = test_context.get_last("interruption_line_number")
        shift_id = test_context.get_last("interruption_shift_id")
        
        # Добавляем 10 кодов
        codes = [f"0104606203399737215interruption{i:03d}93dGVzdA==" for i in range(10)]
        test_context.add("interruption_codes", codes)
        
        for code in codes:
            if mock_api:
                mock_api.add(
                    responses.POST,
                    f"{client.base_url}/api/web/v1/work_shift/add_code",
                    json={"status": "added"},
                    status=200,
                )

            code_data = WorkShiftCodeInput(
                line_number=line_number,
                code=code
            )
            resp = add_code_to_shift(client, body=code_data)
            assert resp.status_code == 200
        
        print(f"[E2E-INTERRUPTION] Добавлено {len(codes)} кодов в смену")

    def test_04_interrupt_work_shift_positive(self, client, test_context, mock_api):
        """Шаг 4: Позитивный сценарий прерывания рабочей смены."""
        shift_id = test_context.get_last("interruption_shift_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/finish",
                json={
                    "id": shift_id,
                    "status": "interrupted",
                    "interrupted_at": datetime.datetime.now().isoformat(),
                    "codes_count": 10
                },
                status=200,
            )

        resp = finish_shift(client, json={"id": shift_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "interrupted"
        
        test_context.add("interruption_shift_status", "interrupted")
        print(f"[E2E-INTERRUPTION] Смена прервана: {shift_id}")

    def test_05_add_code_to_interrupted_shift_negative(self, client, test_context, mock_api):
        """Шаг 5: Негативный сценарий - добавление кода в прерванную смену."""
        line_number = test_context.get_last("interruption_line_number")
        shift_id = test_context.get_last("interruption_shift_id")
        new_code = "0104606203399737215newcode93dGVzdA=="
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/add_code",
                json={"detail": "Cannot add code to interrupted shift"},
                status=400,
            )

        code_data = WorkShiftCodeInput(
                line_number=line_number,
                code=new_code
        )
        resp = add_code_to_shift(client, body=code_data)
        assert resp.status_code == 400
        print(f"[E2E-INTERRUPTION] Негативный тест добавления кода в прерванную смену: статус {resp.status_code}")

    def test_06_resume_work_shift_positive(self, client, test_context, mock_api):
        """Шаг 6: Позитивный сценарий возобновления рабочей смены."""
        line_number = test_context.get_last("interruption_line_number")
        shift_id = test_context.get_last("interruption_shift_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/resume",
                json={
                    "id": shift_id,
                    "status": "active",
                    "resumed_at": datetime.datetime.now().isoformat(),
                    "codes_count": 10
                },
                status=200,
            )

        resp = resume_shift(client, json={"id": shift_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "active"
        
        test_context.add("interruption_shift_status", "active")
        print(f"[E2E-INTERRUPTION] Смена возобновлена: {shift_id}")

    def test_07_add_code_to_resumed_shift(self, client, test_context, mock_api):
        """Шаг 7: Добавление кода в возобновленную смену."""
        line_number = test_context.get_last("interruption_line_number")
        shift_id = test_context.get_last("interruption_shift_id")
        new_code = "0104606203399737215resumedcode93dGVzdA=="
        
        if mock_api:
            mock_api.add(
                responses.POST,
                    f"{client.base_url}/api/web/v1/work_shift/add_code",
                    json={"status": "added"},
                    status=200,
                )

        code_data = WorkShiftCodeInput(
                line_number=line_number,
                code=new_code
        )
        resp = add_code_to_shift(client, body=code_data)
        assert resp.status_code == 200
        print(f"[E2E-INTERRUPTION] Код добавлен в возобновленную смену: {new_code}")

    def test_08_finish_resumed_shift(self, client, test_context, mock_api):
        """Шаг 8: Завершение возобновленной смены."""
        line_number = test_context.get_last("interruption_line_number")
        shift_id = test_context.get_last("interruption_shift_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/finish",
                json={
                    "id": shift_id,
                    "status": "finished",
                    "finished_at": datetime.datetime.now().isoformat(),
                    "codes_count": 11
                },
                status=200,
            )

        resp = finish_shift(client, json={"id": shift_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "finished"
        assert data["codes_count"] == 11
        
        test_context.add("interruption_shift_status", "finished")
        print(f"[E2E-INTERRUPTION] Возобновленная смены завершена: {shift_id}")

    def test_09_interrupt_shipment_positive(self, client, test_context, mock_api):
        """Шаг 9: Позитивный сценарий прерывания отгрузки."""
        line_number = test_context.get_last("interruption_line_number")
        shipment_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/start",
                json={
                    "id": shipment_id,
                    "line_number": line_number,
                    "status": "active"
                },
                status=200,
            )

        resp = start_shipment(client, json={"line_number": line_number})
        assert resp.status_code == 200
        data = resp.json()
        test_context.add("interruption_shipment_id", data["id"])
        
        # Прерываем отгрузку
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/finish",
                json={
                    "id": shipment_id,
                    "status": "interrupted",
                    "interrupted_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = finish_shipment(client, json={"id": shipment_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "interrupted"
        
        test_context.add("interruption_shipment_status", "interrupted")
        print(f"[E2E-INTERRUPTION] Отгрузка прервана: {shipment_id}")

    def test_10_resume_shipment_positive(self, client, test_context, mock_api):
        """Шаг 10: Позитивный сценарий возобновления отгрузки."""
        shipment_id = test_context.get_last("interruption_shipment_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/resume",
                json={
                    "id": shipment_id,
                    "status": "active",
                    "resumed_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = resume_shipment(client, json={"id": shipment_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "active"
        
        test_context.add("interruption_shipment_status", "active")
        print(f"[E2E-INTERRUPTION] Отгрузка возобновлена: {shipment_id}")

    def test_11_finish_resumed_shipment(self, client, test_context, mock_api):
        """Шаг 11: Завершение возобновленной отгрузки."""
        shipment_id = test_context.get_last("interruption_shipment_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/shipment/finish",
                json={
                    "id": shipment_id,
                    "status": "finished",
                    "finished_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = finish_shipment(client, json={"id": shipment_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "finished"
        
        test_context.add("interruption_shipment_status", "finished")
        print(f"[E2E-INTERRUPTION] Возобновленная отгрузка завершена: {shipment_id}")

    def test_12_interrupt_aggregation_session_positive(self, client, test_context, mock_api):
        """Шаг 12: Позитивный сценарий прерывания сессии агрегации."""
        session_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/dashboard/create",
                json={"id": session_id, "name": "Interruption Test Session"},
                status=200,
            )

        resp = create_agg_session(client, json={"name": "Interruption Test Session"})
        assert resp.status_code == 200
        data = resp.json()
        test_context.add("interruption_session_id", data["id"])
        
        # Запускаем сессию
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/pallets/start",
                json={
                    "id": session_id,
                    "status": "active"
                },
                status=200,
            )

        resp = start_agg_session(client, json={"id": session_id})
        assert resp.status_code == 200
        
        # Прерываем сессию
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/pallets/finish",
                json={
                    "id": session_id,
                    "status": "interrupted",
                    "interrupted_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = finish_agg_session(client, json={"id": session_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "interrupted"
        
        test_context.add("interruption_session_status", "interrupted")
        print(f"[E2E-INTERRUPTION] Сессия агрегации прервана: {session_id}")

    def test_13_resume_aggregation_session_positive(self, client, test_context, mock_api):
        """Шаг 13: Позитивный сценарий возобновления сессии агрегации."""
        session_id = test_context.get_last("interruption_session_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/resume",
                json={
                    "id": session_id,
                    "status": "active",
                    "resumed_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = resume_agg_session(client, json={"id": session_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "active"
        
        test_context.add("interruption_session_status", "active")
        print(f"[E2E-INTERRUPTION] Сессия агрегации возобновлена: {session_id}")

    def test_14_finish_resumed_aggregation_session(self, client, test_context, mock_api):
        """Шаг 14: Завершение возобновленной сессии агрегации."""
        session_id = test_context.get_last("interruption_session_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/pallets/finish",
                json={
                    "id": session_id,
                    "status": "finished",
                    "finished_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = finish_agg_session(client, json={"id": session_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "finished"
        
        test_context.add("interruption_session_status", "finished")
        print(f"[E2E-INTERRUPTION] Возобновленная сессия агрегации завершена: {session_id}")

    def test_15_boundary_test_multiple_interruptions(self, client, test_context, mock_api):
        """Шаг 15: Граничный тест - множественные прерывания."""
        line_number = test_context.get_last("interruption_line_number")
        
        # Создаем несколько смен для прерывания
        shift_ids = []
        for i in range(3):
            shift_id = str(uuid.uuid4())
            shift_ids.append(shift_id)
            
            if mock_api:
                mock_api.add(
                    responses.POST,
                    f"{client.base_url}/api/web/v1/work_shift/start",
                    json={"id": shift_id, "line_number": line_number, "status": "active"},
                    status=200,
                )

            payload = WorkShiftStart(
                line_number=line_number,
                gtin="04606203399737",
                batch=f"BATCH-INTERRUPTION-MULTI-{i+1:03d}",
                start_date=datetime.datetime.now(datetime.timezone.utc),
                production_date=datetime.datetime.now(datetime.timezone.utc),
                product_group=ProductGroup.milk,
                is_allow_other_gtins=False,
                with_variable_weight=False,
                camera_is_active=False,
            )
            resp = start_shift(client, body=payload)
            assert resp.status_code == 200
            
            # Прерываем каждую смену
            if mock_api:
                mock_api.add(
                    responses.POST,
                    f"{client.base_url}/api/web/v1/work_shift/finish",
                    json={
                        "id": shift_id,
                        "status": "interrupted",
                        "interrupted_at": datetime.datetime.now().isoformat()
                    },
                    status=200,
                )

            resp = finish_shift(client, json={"id": shift_id})
            assert resp.status_code == 200
        
        print(f"[E2E-INTERRUPTION] Граничный тест: создано и прервано {len(shift_ids)} смен")

    def test_16_boundary_test_interruption_recovery(self, client, test_context, mock_api):
        """Шаг 16: Граничный тест - восстановление после прерывания."""
        shift_ids = test_context.get("interruption_shift_ids", [])
        
        # Возобновляем первую прерванную смену
        if shift_ids and len(shift_ids) > 0:
            first_shift_id = shift_ids[0]
            
            if mock_api:
                mock_api.add(
                    responses.POST,
                    f"{client.base_url}/api/web/v1/work_shift/resume",
                    json={
                        "id": first_shift_id,
                        "status": "active",
                        "resumed_at": datetime.datetime.now().isoformat()
                    },
                    status=200,
                )

            resp = resume_shift(client, json={"id": first_shift_id})
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "active"
            
            # Завершаем восстановленную смену
            if mock_api:
                mock_api.add(
                    responses.POST,
                    f"{client.base_url}/api/web/v1/work_shift/finish",
                    json={
                        "id": first_shift_id,
                        "status": "finished",
                        "finished_at": datetime.datetime.now().isoformat()
                    },
                    status=200,
                )

            resp = finish_shift(client, json={"id": first_shift_id})
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "finished"
        
        print(f"[E2E-INTERRUPTION] Граничный тест: восстановлена и завершена 1 смена из {len(shift_ids)}")

    def test_17_error_test_invalid_shift_id(self, client, test_context, mock_api):
        """Шаг 17: Тест обработки ошибок - невалидный ID смены."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/resume",
                json={"detail": "Shift not found"},
                status=404,
            )

        resp = resume_shift(client, json={"id": "00000000-0000-0000-0000-000000000000"})
        assert resp.status_code == 404
        print(f"[E2E-INTERRUPTION] Тест обработки ошибок: невалидный ID смены")

    def test_18_error_test_permission_denied(self, client, test_context, mock_api):
        """Шаг 18: Тест обработки ошибок - отказ в доступе."""
        shift_ids = test_context.get("interruption_shift_ids", [])
        
        if shift_ids and len(shift_ids) > 0:
            first_shift_id = shift_ids[0]

            if mock_api:
                mock_api.add(
                    responses.POST,
                    f"{client.base_url}/api/web/v1/work_shift/resume",
                    json={"detail": "Permission denied"},
                    status=403,
                )

            resp = resume_shift(client, json={"id": first_shift_id})
            assert resp.status_code == 403
            print(f"[E2E-INTERRUPTION] Тест обработки ошибок: отказ в доступе")

    def test_19_cleanup_interruption_test_data(self, client, test_context, mock_api):
        """Шаг 19: Очистка - завершение всех тестовых смен."""
        shift_ids = test_context.get("interruption_shift_ids", [])
        
        # Завершаем все оставшиеся смены
        if len(shift_ids) > 1:
            for shift_id in shift_ids[1:]:
                if mock_api:
                    mock_api.add(
                        responses.POST,
                        f"{client.base_url}/api/web/v1/work_shift/finish",
                        json={
                            "id": shift_id,
                            "status": "finished",
                            "finished_at": datetime.datetime.now().isoformat()
                        },
                        status=200,
                    )

                resp = finish_shift(client, json={"id": shift_id})
                assert resp.status_code == 200
        
        print(f"[E2E-INTERRUPTION] Тестовые данные прерывания очищены")