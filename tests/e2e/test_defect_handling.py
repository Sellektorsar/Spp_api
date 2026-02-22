"""
E2E Tests: Defect Handling
Сценарий: обработка бракованных кодов.

Шаги:
1. Создание рабочей смены
2. Добавление кодов в смену
3. Выявление и добавление бракованных кодов
4. Отмена бракованных кодов
5. Проверка статистики брака
6. Удаление бракованных кодов из отчетов
"""
import pytest
import responses
import uuid
import datetime
from typing import Dict, Any

from src.api.line.create import create as create_line
from src.api.work_shift.start import start as start_shift
from src.api.work_shift.add import add as add_code
from src.api.work_shift.add_range import add_range as add_defect_range
from src.api.work_shift.remove_range import remove_range as remove_defect_range
from src.api.work_shift.cancel_start_code import cancel_start_code as cancel_code
from src.api.work_shift.codes_by_roll import codes_by_roll as cancel_codes_by_roll
from src.api.work_shift.codes_range import codes_range as cancel_range
from src.api.work_shift.get_codes import get_codes
from src.api.work_shift.finish import finish as finish_shift
from src.api.work_shift.defect import add_defect, remove_defect
from src.models import CreateInput, WorkShiftStart, WorkShiftCodeInput, LINETYPE, ProductGroup, ProductionType


@pytest.mark.e2e
@pytest.mark.order(11)
class TestDefectHandling:
    """
    E2E Сценарий: Обработка бракованных кодов.
    """

    def test_01_create_production_line_for_defect(self, client, test_context, mock_api):
        """Шаг 1: Создание производственной линии для обработки брака."""
        line_id = str(uuid.uuid4())
        line_number = 801
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/create",
                json={"id": line_id, "number": line_number},
                status=200,
            )

        payload = CreateInput(
            name="Defect Handling Test Line",
            line_type=LINETYPE.integer_1,
            product_group=ProductGroup.milk,
            production_type=ProductionType.integer_1,
        )
        resp = create_line(client, body=payload)
        assert resp.status_code == 200
        data = resp.json()
        test_context.add("defect_line_number", data["number"])
        print(f"[E2E-DEFECT] Линия для обработки брака создана: {data['number']}")

    def test_02_start_work_shift_for_defect(self, client, test_context, mock_api):
        """Шаг 2: Запуск рабочей смены для обработки брака."""
        line_number = test_context.get_last("defect_line_number")
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
            batch="BATCH-DEFECT-001",
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
        test_context.add("defect_shift_id", data["id"])
        print(f"[E2E-DEFECT] Смена для обработки брака запущена: {data['id']}")

    def test_03_add_normal_codes_to_shift(self, client, test_context, mock_api):
        """Шаг 3: Добавление нормальных кодов в смену."""
        line_number = test_context.get_last("defect_line_number")
        shift_id = test_context.get_last("defect_shift_id")
        
        # Добавляем 5 нормальных кодов
        normal_codes = [f"0104606203399737215normal{i:03d}93dGVzdA==" for i in range(1, 6)]
        test_context.add("normal_codes", normal_codes)
        
        for code in normal_codes:
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
            resp = add_code(client, body=code_data)
            assert resp.status_code == 200
        
        print(f"[E2E-DEFECT] Добавлено {len(normal_codes)} нормальных кодов в смену")

    def test_04_add_defect_code_positive(self, client, test_context, mock_api):
        """Шаг 4: Позитивный сценарий добавления бракованного кода."""
        line_number = test_context.get_last("defect_line_number")
        shift_id = test_context.get_last("defect_shift_id")
        defect_code = "0104606203399737215defect00193dGVzdA=="
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/defect/add",
                json={
                    "status": "defect_added",
                    "defect_code": defect_code,
                    "defect_reason": "print_quality_issue"
                },
                status=200,
            )

        resp = add_defect(client, json={
            "line_number": line_number,
            "code": defect_code,
            "reason": "print_quality_issue"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "defect_added"
        
        test_context.add("defect_code_1", defect_code)
        print(f"[E2E-DEFECT] Бракованный код добавлен: {defect_code}")

    def test_05_add_defect_code_negative_invalid_code(self, client, test_context, mock_api):
        """Шаг 5: Негативный сценарий - добавление невалидного бракованного кода."""
        line_number = test_context.get_last("defect_line_number")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/defect/add",
                json={"detail": "Invalid code format"},
                status=400,
            )

        resp = add_defect(client, json={
            "line_number": line_number,
            "code": "INVALID_CODE_FORMAT",
            "reason": "invalid_format"
        })
        assert resp.status_code == 400
        print(f"[E2E-DEFECT] Негативный тест добавления брака: статус {resp.status_code}")

    def test_06_add_defect_code_negative_not_in_shift(self, client, test_context, mock_api):
        """Шаг 6: Негативный сценарий - добавление кода не из смены."""
        line_number = test_context.get_last("defect_line_number")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/defect/add",
                json={"detail": "Code not found in work shift"},
                status=404,
            )

        resp = add_defect(client, json={
            "line_number": line_number,
            "code": "0104606203399737215notfound93dGVzdA==",
            "reason": "not_in_shift"
        })
        assert resp.status_code == 404
        print(f"[E2E-DEFECT] Негативный тест кода не в смене: статус {resp.status_code}")

    def test_07_add_defect_range_positive(self, client, test_context, mock_api):
        """Шаг 7: Позитивный сценарий добавления диапазона бракованных кодов."""
        line_number = test_context.get_last("defect_line_number")
        shift_id = test_context.get_last("defect_shift_id")
        
        defect_codes = [f"0104606203399737215defect{i:03d}93dGVzdA==" for i in range(2, 4)]
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/defect/add_range",
                json={
                    "status": "defect_range_added",
                    "defect_codes": defect_codes,
                    "defect_reason": "print_quality_issue"
                },
                status=200,
            )

        resp = add_defect_range(client, json={
            "line_number": line_number,
            "codes": defect_codes,
            "reason": "print_quality_issue"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "defect_range_added"
        
        test_context.add("defect_range_codes", defect_codes)
        print(f"[E2E-DEFECT] Диапазон бракованных кодов добавлен: {len(defect_codes)} кодов")

    def test_08_get_codes_with_defects(self, client, test_context, mock_api):
        """Шаг 8: Получение кодов смены с информацией о браке."""
        line_number = test_context.get_last("defect_line_number")
        shift_id = test_context.get_last("defect_shift_id")
        normal_codes = test_context.get_last("normal_codes")
        defect_code_1 = test_context.get_last("defect_code_1")
        defect_range_codes = test_context.get_last("defect_range_codes")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/get_codes",
                json={
                    "total_codes": len(normal_codes) + 1 + len(defect_range_codes),
                    "normal_codes": normal_codes,
                    "defect_codes": [defect_code_1] + defect_range_codes,
                    "defect_count": 1 + len(defect_range_codes)
                },
                status=200,
            )

        resp = get_codes(client, json={"line_number": line_number})
        assert resp.status_code == 200
        data = resp.json()
        assert data["defect_count"] == 1 + len(defect_range_codes)
        print(f"[E2E-DEFECT] Получены коды смены: {data['total_codes']} всего, {data['defect_count']} бракованных")

    def test_09_cancel_defect_code_positive(self, client, test_context, mock_api):
        """Шаг 9: Позитивный сценарий отмены бракованного кода."""
        line_number = test_context.get_last("defect_line_number")
        defect_code_1 = test_context.get_last("defect_code_1")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/cancel/code",
                json={
                    "status": "defect_cancelled",
                    "defect_code": defect_code_1,
                    "cancelled_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = cancel_code(client, json={
            "line_number": line_number,
            "code": defect_code_1
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "defect_cancelled"
        print(f"[E2E-DEFECT] Бракованный код отменен: {defect_code_1}")

    def test_10_cancel_defect_code_negative_invalid_code(self, client, test_context, mock_api):
        """Шаг 10: Негативный сценарий - отмена невалидного бракованного кода."""
        line_number = test_context.get_last("defect_line_number")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/cancel/code",
                json={"detail": "Code not found or not marked as defect"},
                status=404,
            )

        resp = cancel_code(client, json={
            "line_number": line_number,
            "code": "0104606203399737215notdefect93dGVzdA=="
        })
        assert resp.status_code == 404
        print(f"[E2E-DEFECT] Негативный тест отмены брака: статус {resp.status_code}")

    def test_11_cancel_defect_range_positive(self, client, test_context, mock_api):
        """Шаг 11: Позитивный сценарий отмены диапазона бракованных кодов."""
        line_number = test_context.get_last("defect_line_number")
        defect_range_codes = test_context.get_last("defect_range_codes")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/cancel/codes_range",
                json={
                    "status": "defect_range_cancelled",
                    "cancelled_codes": defect_range_codes,
                    "cancelled_count": len(defect_range_codes)
                },
                status=200,
            )

        resp = cancel_range(client, json={
            "line_number": line_number,
            "codes": defect_range_codes
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "defect_range_cancelled"
        assert data["cancelled_count"] == len(defect_range_codes)
        print(f"[E2E-DEFECT] Диапазон бракованных кодов отменен: {len(defect_range_codes)} кодов")

    def test_12_remove_defect_code_positive(self, client, test_context, mock_api):
        """Шаг 12: Позитивный сценарий удаления бракованного кода."""
        line_number = test_context.get_last("defect_line_number")
        defect_code_1 = test_context.get_last("defect_code_1")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/defect/remove",
                json={
                    "status": "defect_removed",
                    "defect_code": defect_code_1,
                    "removed_at": datetime.datetime.now().isoformat()
                },
                status=200,
            )

        resp = remove_defect(client, json={
            "line_number": line_number,
            "code": defect_code_1
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "defect_removed"
        print(f"[E2E-DEFECT] Бракованный код удален: {defect_code_1}")

    def test_13_remove_defect_range_positive(self, client, test_context, mock_api):
        """Шаг 13: Позитивный сценарий удаления диапазона бракованных кодов."""
        line_number = test_context.get_last("defect_line_number")
        defect_range_codes = test_context.get_last("defect_range_codes")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/defect/remove_range",
                json={
                    "status": "defect_range_removed",
                    "removed_codes": defect_range_codes,
                    "removed_count": len(defect_range_codes)
                },
                status=200,
            )

        resp = remove_defect_range(client, json={
            "line_number": line_number,
            "codes": defect_range_codes
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "defect_range_removed"
        assert data["removed_count"] == len(defect_range_codes)
        print(f"[E2E-DEFECT] Диапазон бракованных кодов удален: {len(defect_range_codes)} кодов")

    def test_14_boundary_test_large_defect_range(self, client, test_context, mock_api):
        """Шаг 14: Граничный тест - большой диапазон бракованных кодов."""
        line_number = test_context.get_last("defect_line_number")
        large_defect_range = [f"0104606203399737215defect{i:03d}93dGVzdA==" for i in range(100, 200)]
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/defect/add_range",
                json={
                    "status": "defect_range_added",
                    "defect_codes": large_defect_range,
                    "defect_count": len(large_defect_range)
                },
                status=200,
            )

        resp = add_defect_range(client, json={
            "line_number": line_number,
            "codes": large_defect_range,
            "reason": "print_quality_issue"
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["defect_count"] == len(large_defect_range)
        print(f"[E2E-DEFECT] Граничный тест: добавлен диапазон из {len(large_defect_range)} бракованных кодов")

    def test_15_boundary_test_empty_defect_list(self, client, test_context, mock_api):
        """Шаг 15: Граничный тест - пустой список бракованных кодов."""
        line_number = test_context.get_last("defect_line_number")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/get_codes",
                json={
                    "total_codes": 5,
                    "normal_codes": test_context.get_last("normal_codes"),
                    "defect_codes": [],
                    "defect_count": 0
                },
                status=200,
            )

        resp = get_codes(client, json={"line_number": line_number})
        assert resp.status_code == 200
        data = resp.json()
        assert data["defect_count"] == 0
        print(f"[E2E-DEFECT] Граничный тест: пустой список бракованных кодов")

    def test_16_error_test_invalid_line_number(self, client, test_context, mock_api):
        """Шаг 16: Тест обработки ошибок - невалидный номер линии."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/defect/add",
                json={"detail": "Line not found"},
                status=404,
            )

        resp = add_defect(client, json={
            "line_number": 99999,  # Несуществующий номер
            "code": "0104606203399737215defect00193dGVzdA==",
            "reason": "test_error"
        })
        assert resp.status_code == 404
        print(f"[E2E-DEFECT] Тест обработки ошибок: невалидный номер линии")

    def test_17_error_test_permission_denied(self, client, test_context, mock_api):
        """Шаг 17: Тест обработки ошибок - отказ в доступе."""
        line_number = test_context.get_last("defect_line_number")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/defect/remove",
                json={"detail": "Permission denied"},
                status=403,
            )

        resp = remove_defect(client, json={
            "line_number": line_number,
            "code": test_context.get_last("defect_code_1")
        })
        assert resp.status_code == 403
        print(f"[E2E-DEFECT] Тест обработки ошибок: отказ в доступе")

    def test_18_finish_shift_with_defects(self, client, test_context, mock_api):
        """Шаг 18: Завершение смены с бракованными кодами."""
        line_number = test_context.get_last("defect_line_number")
        shift_id = test_context.get_last("defect_shift_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/finish",
                json={
                    "id": shift_id,
                    "status": "finished",
                    "finished_at": datetime.datetime.now().isoformat(),
                    "total_codes": 5,
                    "defect_codes": 1,
                    "normal_codes": 4
                },
                status=200,
            )

        resp = finish_shift(client, json={"id": shift_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "finished"
        assert data["defect_codes"] == 1
        print(f"[E2E-DEFECT] Смена с бракоманными кодами завершена: {data['defect_codes']} браков")

    def test_19_cleanup_defect_test_data(self, client, test_context, mock_api):
        """Шаг 19: Очистка - завершение смены и удаление тестовых данных."""
        line_number = test_context.get_last("defect_line_number")
        shift_id = test_context.get_last("defect_shift_id")
        
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
        
        print(f"[E2E-DEFECT] Тестовые данные брака очищены")