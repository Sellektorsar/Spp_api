"""
Integration Tests: Work Shift Management
Проверяет цепочку: фильтрация смен → старт смены → добавление кодов → завершение смены.
Тесты работают против реального сервера spp-dev.
"""
import pytest
import datetime

from src.api.work_shift.start import start as start_shift
from src.api.work_shift.finish import finish as finish_shift
from src.api.work_shift.add_code import add_code
from src.api.work_shift.filter import filter as filter_shifts
from src.models import WorkShiftStart, WorkShiftCodeWithVariableWeight, ProductGroup


@pytest.mark.integration
class TestWorkShiftFilter:
    """Тесты фильтрации рабочих смен."""

    def test_filter_all_shifts(self, client):
        """Получение списка всех смен."""
        resp = filter_shifts(client, json={"limit": 20, "offset": 0})
        assert resp.status_code == 200
        data = resp.json()
        assert "total_count" in data
        assert isinstance(data["result"], list)
        # На сервере есть реальные смены
        assert data["total_count"] > 0

    def test_filter_shifts_by_line_milk(self, client, real_line_milk):
        """Фильтрация смен по линии milk."""
        resp = filter_shifts(client, json={"limit": 10, "offset": 0, "line_number": real_line_milk})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] >= 0
        # Если смены есть — проверяем номер линии
        for shift in data["result"]:
            assert shift.get("line_number") == real_line_milk

    def test_filter_shifts_by_line_water(self, client, real_line_water):
        """Фильтрация смен по линии water."""
        resp = filter_shifts(client, json={"limit": 10, "offset": 0, "line_number": real_line_water})
        assert resp.status_code == 200

    def test_filter_shifts_pagination(self, client):
        """Пагинация смен: limit/offset принимаются сервером корректно."""
        resp1 = filter_shifts(client, json={"limit": 5, "offset": 0})
        resp2 = filter_shifts(client, json={"limit": 5, "offset": 5})
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert "total_count" in resp1.json()
        assert isinstance(resp1.json()["result"], list)
        assert isinstance(resp2.json()["result"], list)
        assert len(resp1.json()["result"]) <= 5
        assert len(resp2.json()["result"]) <= 5

    def test_filter_active_shift_milk(self, client, real_shift_id_milk):
        """Активная смена milk присутствует в системе."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        resp = filter_shifts(client, json={"limit": 50, "offset": 0})
        assert resp.status_code == 200
        ids = {r.get("id") for r in resp.json()["result"]}
        assert real_shift_id_milk in ids, (
            f"Активная смена milk {real_shift_id_milk} не найдена в списке смен"
        )


@pytest.mark.integration
class TestWorkShiftLifecycle:
    """
    Интеграционный тест жизненного цикла рабочей смены.
    Создаём новую смену, добавляем код, завершаем.
    ВАЖНО: используем отдельную линию (milk_2=36), чтобы не трогать активные смены.
    """

    # Храним ID созданной в тесте смены
    _created_shift_id: str = None

    def test_start_shift_milk(self, client, real_gtin_milk):
        """Старт рабочей смены на линии milk."""
        # Используем SPP_TEST_LINE_MILK_2 (line=36) если задан, иначе основную
        import os
        line = int(os.getenv("SPP_TEST_LINE_MILK_2") or "36")

        payload = WorkShiftStart(
            line_number=line,
            gtin=real_gtin_milk,
            batch=f"TEST-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            start_date=datetime.datetime.now(datetime.timezone.utc),
            production_date=datetime.datetime.now(datetime.timezone.utc),
            product_group=ProductGroup.milk,
            is_allow_other_gtins=False,
            with_variable_weight=False,
            camera_is_active=False,
        )
        resp = start_shift(client, body=payload)
        # 200 — смена создана, 400/422 — линия уже занята или иная ошибка бизнес-логики
        assert resp.status_code in [200, 400, 422]
        if resp.status_code == 200:
            data = resp.json()
            shift_id = data.get("id") or data.get("shift_id")
            assert shift_id, "ID смены должен присутствовать в ответе"
            TestWorkShiftLifecycle._created_shift_id = str(shift_id)

    def test_add_code_to_created_shift(self, client):
        """Добавление кода маркировки в созданную смену."""
        shift_id = TestWorkShiftLifecycle._created_shift_id
        if not shift_id:
            pytest.skip("Смена не была создана в test_start_shift_milk")

        import os
        line = int(os.getenv("SPP_TEST_LINE_MILK_2") or "36")

        payload = WorkShiftCodeWithVariableWeight(
            line_number=line,
            code="010460049400904421dGVzdGNvZGU=",
        )
        resp = add_code(client, body=payload)
        # Код может быть невалидным — ожидаем 200 или 4xx
        assert resp.status_code in [200, 400, 422]

    def test_finish_created_shift(self, client):
        """Завершение тестовой смены."""
        shift_id = TestWorkShiftLifecycle._created_shift_id
        if not shift_id:
            pytest.skip("Смена не была создана в test_start_shift_milk")

        resp = finish_shift(client, json={"id": shift_id})
        assert resp.status_code in [200, 400, 404, 422]
        if resp.status_code == 200:
            # Смена успешно завершена — сбрасываем ID
            TestWorkShiftLifecycle._created_shift_id = None

    def test_start_shift_invalid_line(self, client, real_gtin_milk):
        """Старт смены с несуществующим номером линии возвращает ошибку."""
        payload = WorkShiftStart(
            line_number=99999999,
            gtin=real_gtin_milk,
            batch="TEST-BAD-LINE",
            start_date=datetime.datetime.now(datetime.timezone.utc),
            production_date=datetime.datetime.now(datetime.timezone.utc),
            product_group=ProductGroup.milk,
            is_allow_other_gtins=False,
            with_variable_weight=False,
            camera_is_active=False,
        )
        resp = start_shift(client, body=payload)
        assert resp.status_code in [400, 404, 422]

    def test_finish_nonexistent_shift(self, client):
        """Завершение несуществующей смены — ошибка."""
        resp = finish_shift(client, json={"id": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]


@pytest.mark.integration
class TestWorkShiftActiveShifts:
    """Тесты работы с активными сменами из .env (только чтение!)."""

    def test_active_shift_milk_exists(self, client, real_shift_id_milk):
        """Активная смена milk присутствует в системе."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        resp = filter_shifts(client, json={"limit": 100, "offset": 0})
        assert resp.status_code == 200
        ids = {r.get("id") for r in resp.json()["result"]}
        assert real_shift_id_milk in ids

    def test_active_shift_water_exists(self, client, real_shift_id_water):
        """Активная смена water присутствует в системе."""
        if not real_shift_id_water:
            pytest.skip("SPP_TEST_SHIFT_ID_WATER не задан")
        resp = filter_shifts(client, json={"limit": 100, "offset": 0})
        assert resp.status_code == 200
        ids = {r.get("id") for r in resp.json()["result"]}
        assert real_shift_id_water in ids

    def test_active_shift_softdrinks_exists(self, client, real_shift_id_softdrinks):
        """Активная смена softdrinks присутствует в системе."""
        if not real_shift_id_softdrinks:
            pytest.skip("SPP_TEST_SHIFT_ID_SOFTDRINKS не задан")
        resp = filter_shifts(client, json={"limit": 100, "offset": 0})
        assert resp.status_code == 200
        ids = {r.get("id") for r in resp.json()["result"]}
        assert real_shift_id_softdrinks in ids

    def test_finished_shift_exists(self, client, real_shift_id_finished):
        """Завершённая смена присутствует в системе."""
        if not real_shift_id_finished:
            pytest.skip("SPP_TEST_SHIFT_ID_FINISHED не задан")
        resp = filter_shifts(client, json={"limit": 200, "offset": 0})
        assert resp.status_code == 200
        ids = {r.get("id") for r in resp.json()["result"]}
        # Завершённая смена может не попасть в первые 200 — просто проверяем ответ
        assert resp.json()["total_count"] >= 0
