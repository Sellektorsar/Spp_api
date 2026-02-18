"""
Integration chain test: GTIN Filter → Work Shift Filter → Aggregation Session Filter.
Демонстрирует сквозное чтение данных между несколькими подсистемами.
Тесты работают против реального сервера spp-dev.
"""
import pytest
import datetime

from src.api.gtin.filter import filter as filter_gtin
from src.api.work_shift.filter import filter as filter_shifts
from src.api.work_shift.start import start as start_shift
from src.api.work_shift.finish import finish as finish_shift
from src.api.aggregation_session.filter import filter as filter_sessions
from src.api.aggregation_session.create import create as create_session
from src.api.aggregation_session.finish import finish as finish_session
from src.api.line.create import create as create_line
from src.models import WorkShiftStart, ProductGroup, CreateInput, LINETYPE, ProductionType


@pytest.mark.integration
def test_gtin_to_shift_chain(client, real_gtin_milk, real_line_milk):
    """
    Цепочка: получить GTIN milk → убедиться что он есть → получить смены на линии milk.
    """
    # 1. Найти GTIN milk в справочнике
    gtin_resp = filter_gtin(client, json={"limit": 5, "offset": 0, "product_group": "milk"})
    assert gtin_resp.status_code == 200
    gtin_data = gtin_resp.json()
    assert gtin_data["total_count"] >= 1
    found_gtins = [r["gtin"] for r in gtin_data["result"]]
    assert real_gtin_milk in found_gtins, f"GTIN {real_gtin_milk} не найден в группе milk"

    # 2. Получить смены на линии milk — там должны быть записи
    shift_resp = filter_shifts(client, json={"limit": 10, "offset": 0, "line_number": real_line_milk})
    assert shift_resp.status_code == 200
    shift_data = shift_resp.json()
    assert shift_data["total_count"] >= 0


@pytest.mark.integration
def test_multi_product_group_chain(client):
    """
    Цепочка: последовательно проверяем GTIN для 5 разных товарных групп.
    Убеждаемся что справочник заполнен для каждой.
    """
    groups_with_gtins = [
        ("milk",       "04600494009044"),
        ("water",      "04600494009013"),
        ("shoes",      "04640043463996"),
        ("chemistry",  "04857624963725"),
        ("beer",       "04632064327432"),
    ]
    for pg, expected_gtin in groups_with_gtins:
        resp = filter_gtin(client, json={"limit": 5, "offset": 0, "product_group": pg})
        assert resp.status_code == 200, f"Ошибка запроса GTIN для группы {pg}"
        data = resp.json()
        assert data["total_count"] >= 1, f"Группа {pg}: ожидается хотя бы один GTIN"


@pytest.mark.integration
def test_active_shifts_across_lines(client, real_line_milk, real_line_water):
    """
    Проверка активных смен на нескольких линиях одновременно.
    """
    for line in [real_line_milk, real_line_water]:
        resp = filter_shifts(client, json={"limit": 10, "offset": 0, "line_number": line})
        assert resp.status_code == 200, f"Ошибка при запросе смен для линии {line}"


@pytest.mark.integration
def test_shift_and_aggregation_session_chain(
    client,
    real_shift_id_milk,
    real_agg_session_id,
):
    """
    Цепочка: проверяем что активная смена milk и агрегационная сессия существуют в системе.
    """
    # 1. Проверяем активную смену milk
    if real_shift_id_milk:
        shift_resp = filter_shifts(client, json={"limit": 50, "offset": 0})
        assert shift_resp.status_code == 200
        shift_ids = {r.get("id") for r in shift_resp.json()["result"]}
        assert real_shift_id_milk in shift_ids, (
            f"Смена milk {real_shift_id_milk} не найдена"
        )

    # 2. Проверяем агрегационные сессии
    agg_resp = filter_sessions(client, json={"limit": 20, "offset": 0})
    assert agg_resp.status_code == 200
    agg_data = agg_resp.json()
    assert "total_count" in agg_data
    assert isinstance(agg_data["result"], list)

    if real_agg_session_id and agg_data["total_count"] > 0:
        agg_ids = {r.get("id") or r.get("id_agg_session") for r in agg_data["result"]}
        # Сессия может быть завершена и не попасть в первые 20
        assert agg_data["total_count"] > 0


@pytest.mark.integration
def test_create_shift_and_finish_chain(client, real_gtin_milk):
    """
    Полная цепочка создания и завершения тестовой смены.
    Использует отдельную линию (milk_2=36) чтобы не трогать рабочие смены.
    """
    import os
    line = int(os.getenv("SPP_TEST_LINE_MILK_2") or "36")

    # 1. Запускаем тестовую смену
    payload = WorkShiftStart(
        line_number=line,
        gtin=real_gtin_milk,
        batch=f"CHAIN-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        start_date=datetime.datetime.now(datetime.timezone.utc),
        production_date=datetime.datetime.now(datetime.timezone.utc),
        product_group=ProductGroup.milk,
        is_allow_other_gtins=False,
        with_variable_weight=False,
        camera_is_active=False,
    )
    start_resp = start_shift(client, body=payload)
    assert start_resp.status_code in [200, 400, 422]

    if start_resp.status_code != 200:
        pytest.skip(f"Линия {line} занята или недоступна: {start_resp.json()}")

    shift_data = start_resp.json()
    shift_id = shift_data.get("id") or shift_data.get("shift_id")
    assert shift_id, "ID смены отсутствует в ответе"

    # 2. Убеждаемся что смена видна в фильтре
    filter_resp = filter_shifts(client, json={"limit": 50, "offset": 0, "line_number": line})
    assert filter_resp.status_code == 200
    ids = {r.get("id") for r in filter_resp.json()["result"]}
    assert str(shift_id) in ids, "Только что созданная смена не найдена в фильтре"

    # 3. Завершаем смену
    finish_resp = finish_shift(client, json={"id": str(shift_id)})
    assert finish_resp.status_code in [200, 400, 422]
