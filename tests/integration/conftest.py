"""
Integration conftest — специфичные фикстуры для интеграционных тестов.
Основные фикстуры (client, test_context, mock_api) наследуются из tests/conftest.py.

Параметры берутся из .env (scripts/collect_test_data.py собирает их с сервера):
  SPP_TEST_LINE_*        — номера производственных линий
  SPP_TEST_GTIN_*        — GTIN по товарным группам
  SPP_TEST_SHIFT_ID_*    — ID рабочих смен
  SPP_TEST_REPORT_ID_*   — ID отчётов по статусам
  SPP_TEST_AGG_SESSION_* — ID агрегационных сессий
  SPP_TEST_DEVICE_ID     — ID устройства
  SPP_TEST_PRINTER_ID    — layout_id принтера
  SPP_TEST_INN           — ИНН (актуальный: 7731376812)
"""
import os
import pytest


# ──────────────────────────────────────────────────────
# GTIN по товарным группам
# ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def real_gtin() -> str:
    """GTIN по умолчанию (milk)."""
    return os.getenv("SPP_TEST_GTIN", "04600494009044")

@pytest.fixture(scope="session")
def real_gtin_milk() -> str:
    return os.getenv("SPP_TEST_GTIN_MILK", "04600494009044")

@pytest.fixture(scope="session")
def real_gtin_water() -> str:
    return os.getenv("SPP_TEST_GTIN_WATER", "04600494009013")

@pytest.fixture(scope="session")
def real_gtin_shoes() -> str:
    return os.getenv("SPP_TEST_GTIN_SHOES", "04640043463996")

@pytest.fixture(scope="session")
def real_gtin_antiseptic() -> str:
    return os.getenv("SPP_TEST_GTIN_ANTISEPTIC", "04607980207656")

@pytest.fixture(scope="session")
def real_gtin_bio() -> str:
    return os.getenv("SPP_TEST_GTIN_BIO", "04647297654873")

@pytest.fixture(scope="session")
def real_gtin_lp() -> str:
    return os.getenv("SPP_TEST_GTIN_LP", "04640043461343")

@pytest.fixture(scope="session")
def real_gtin_perfumery() -> str:
    return os.getenv("SPP_TEST_GTIN_PERFUMERY", "04607980207113")

@pytest.fixture(scope="session")
def real_gtin_beer() -> str:
    return os.getenv("SPP_TEST_GTIN_BEER", "04632064327432")

@pytest.fixture(scope="session")
def real_gtin_nabeer() -> str:
    return os.getenv("SPP_TEST_GTIN_NABEER", "04870216760007")

@pytest.fixture(scope="session")
def real_gtin_softdrinks() -> str:
    return os.getenv("SPP_TEST_GTIN_SOFTDRINKS", "04619582369274")

@pytest.fixture(scope="session")
def real_gtin_meat() -> str:
    return os.getenv("SPP_TEST_GTIN_MEAT", "03691422358694")

@pytest.fixture(scope="session")
def real_gtin_seafood() -> str:
    return os.getenv("SPP_TEST_GTIN_SEAFOOD", "04549957535525")

@pytest.fixture(scope="session")
def real_gtin_conserve() -> str:
    return os.getenv("SPP_TEST_GTIN_CONSERVE", "07862106441988")

@pytest.fixture(scope="session")
def real_gtin_sweets() -> str:
    return os.getenv("SPP_TEST_GTIN_SWEETS", "04640064327432")

@pytest.fixture(scope="session")
def real_gtin_grocery() -> str:
    return os.getenv("SPP_TEST_GTIN_GROCERY", "04649002935154")

@pytest.fixture(scope="session")
def real_gtin_vetpharma() -> str:
    return os.getenv("SPP_TEST_GTIN_VETPHARMA", "00634479480379")

@pytest.fixture(scope="session")
def real_gtin_toys() -> str:
    return os.getenv("SPP_TEST_GTIN_TOYS", "04640043460667")

@pytest.fixture(scope="session")
def real_gtin_homeware() -> str:
    return os.getenv("SPP_TEST_GTIN_HOMEWARE", "03651541671289")

@pytest.fixture(scope="session")
def real_gtin_chemistry() -> str:
    return os.getenv("SPP_TEST_GTIN_CHEMISTRY", "04857624963725")

@pytest.fixture(scope="session")
def real_gtin_construction() -> str:
    return os.getenv("SPP_TEST_GTIN_CONSTRUCTION", "05900089617029")

@pytest.fixture(scope="session")
def real_gtin_fertilizers() -> str:
    return os.getenv("SPP_TEST_GTIN_FERTILIZERS", "01368401095742")

@pytest.fixture(scope="session")
def real_gtin_fire() -> str:
    return os.getenv("SPP_TEST_GTIN_FIRE", "03200000004160")

@pytest.fixture(scope="session")
def real_gtin_vegetableoil() -> str:
    return os.getenv("SPP_TEST_GTIN_VEGETABLEOIL", "04600494009020")

@pytest.fixture(scope="session")
def real_gtin_petfood() -> str:
    return os.getenv("SPP_TEST_GTIN_PETFOOD", "05404009515759")

@pytest.fixture(scope="session")
def real_gtin_books() -> str:
    return os.getenv("SPP_TEST_GTIN_BOOKS", "04640044990705")

@pytest.fixture(scope="session")
def real_gtin_radio() -> str:
    return os.getenv("SPP_TEST_GTIN_RADIO", "08050500209580")

@pytest.fixture(scope="session")
def real_gtin_autofluids() -> str:
    return os.getenv("SPP_TEST_GTIN_AUTOFLUIDS", "04704319506357")

@pytest.fixture(scope="session")
def real_gtin_carparts() -> str:
    return os.getenv("SPP_TEST_GTIN_CARPARTS", "04549957467994")

@pytest.fixture(scope="session")
def real_gtin_bicycle() -> str:
    return os.getenv("SPP_TEST_GTIN_BICYCLE", "03574660482799")

@pytest.fixture(scope="session")
def real_gtin_wheelchairs() -> str:
    return os.getenv("SPP_TEST_GTIN_WHEELCHAIRS", "04648349498179")


# ──────────────────────────────────────────────────────
# ИНН
# ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def real_inn() -> str:
    """Актуальный ИНН владельца."""
    return os.getenv("SPP_TEST_INN", "7731376812")


# ──────────────────────────────────────────────────────
# Производственные линии
# ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def real_line_number() -> int:
    """Номер линии milk (основная)."""
    v = os.getenv("SPP_TEST_LINE_MILK") or os.getenv("SPP_TEST_LINE_NUMBER") or "1"
    return int(v)

@pytest.fixture(scope="session")
def real_line_milk() -> int:
    v = os.getenv("SPP_TEST_LINE_MILK", "1")
    return int(v)

@pytest.fixture(scope="session")
def real_line_water() -> int:
    v = os.getenv("SPP_TEST_LINE_WATER", "100")
    return int(v)

@pytest.fixture(scope="session")
def real_line_softdrinks() -> int:
    v = os.getenv("SPP_TEST_LINE_SOFTDRINKS", "994872")
    return int(v)

@pytest.fixture(scope="session")
def real_line_fertilizers() -> int:
    v = os.getenv("SPP_TEST_LINE_FERTILIZERS", "995080")
    return int(v)

@pytest.fixture(scope="session")
def real_line_chemistry() -> int:
    v = os.getenv("SPP_TEST_LINE_CHEMISTRY", "994862")
    return int(v)


# ──────────────────────────────────────────────────────
# Рабочие смены
# ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def real_shift_id() -> str:
    """Активная смена milk (не завершать в тестах!)."""
    return (
        os.getenv("SPP_TEST_SHIFT_ID_MILK")
        or os.getenv("SPP_TEST_SHIFT_ID")
        or ""
    )

@pytest.fixture(scope="session")
def real_shift_id_milk() -> str:
    return os.getenv("SPP_TEST_SHIFT_ID_MILK", "")

@pytest.fixture(scope="session")
def real_shift_id_water() -> str:
    return os.getenv("SPP_TEST_SHIFT_ID_WATER", "")

@pytest.fixture(scope="session")
def real_shift_id_softdrinks() -> str:
    return os.getenv("SPP_TEST_SHIFT_ID_SOFTDRINKS", "")

@pytest.fixture(scope="session")
def real_shift_id_fertilizers() -> str:
    return os.getenv("SPP_TEST_SHIFT_ID_FERTILIZERS", "")

@pytest.fixture(scope="session")
def real_shift_id_finished() -> str:
    """Завершённая смена — безопасна для send_circulation/utilisation."""
    return os.getenv("SPP_TEST_SHIFT_ID_FINISHED", "")

@pytest.fixture(scope="session")
def real_shift_id_finished_2() -> str:
    return os.getenv("SPP_TEST_SHIFT_ID_FINISHED_2", "")


# ──────────────────────────────────────────────────────
# Устройства и принтеры
# ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def real_device_id() -> str:
    """Реальный device_id (не блокировать/удалять — рабочее устройство!)."""
    return os.getenv("SPP_TEST_DEVICE_ID", "")

@pytest.fixture(scope="session")
def real_mob_device_id() -> str:
    return os.getenv("SPP_TEST_MOB_DEVICE_ID", "")

@pytest.fixture(scope="session")
def real_printer_id() -> str:
    """Основной layout_id принтера."""
    return os.getenv("SPP_TEST_PRINTER_ID", "")

@pytest.fixture(scope="session")
def real_printer_id_2() -> str:
    return os.getenv("SPP_TEST_PRINTER_ID_2", "")

@pytest.fixture(scope="session")
def real_printer_id_3() -> str:
    return os.getenv("SPP_TEST_PRINTER_ID_3", "")


# ──────────────────────────────────────────────────────
# Отчёты
# ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def real_report_id() -> str:
    """Отчёт со статусом 0 (new)."""
    return os.getenv("SPP_TEST_REPORT_ID_NEW") or os.getenv("SPP_TEST_REPORT_ID", "")

@pytest.fixture(scope="session")
def real_report_id_sent() -> str:
    """Отчёт со статусом 102 (sent)."""
    return os.getenv("SPP_TEST_REPORT_ID_SENT", "")

@pytest.fixture(scope="session")
def real_report_id_error() -> str:
    """Отчёт со статусом 103 (error) — подходит для resend."""
    return os.getenv("SPP_TEST_REPORT_ID_ERROR", "")

@pytest.fixture(scope="session")
def real_report_id_pending() -> str:
    """Отчёт со статусом 104 (pending)."""
    return os.getenv("SPP_TEST_REPORT_ID_PENDING", "")


# ──────────────────────────────────────────────────────
# Агрегационные сессии
# ──────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def real_agg_session_id() -> str:
    """Реальный id_agg_session для тестов send_aggregation/send_atk."""
    return os.getenv("SPP_TEST_AGG_SESSION_ID", "")

@pytest.fixture(scope="session")
def real_agg_session_id_2() -> str:
    return os.getenv("SPP_TEST_AGG_SESSION_ID_2", "")
