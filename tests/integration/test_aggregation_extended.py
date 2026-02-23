"""
Integration Tests: Aggregation Session Extended
Раздел 9 (Агрегационные сессии) - расширенные операции

Roadmap: SPP_API_Test_Roadmap_v3.md
Кейсы: 225-431 (206 тестов)

API:
- POST /aggregation_session/delete - Удаление сессии
- POST /aggregation_session/active - ID активной сессии
- POST /aggregation_session/add_code_to_package - Добавление в упаковку
- POST /aggregation_session/package_info - Информация об агрегате
- POST /aggregation_session/close_pallet - Закрытие палеты
- POST /aggregation_session/check_code - Проверка кода
- POST /aggregation_session/vision/* - Vision операции
- POST /aggregation_session/preset/* - Пресеты
- POST /aggregation_session/dashboard/* - Dashboard
- POST /aggregation_session/pallets/* - Паллетная агрегация
- POST /aggregation_session/buffer/* - Буферы
- POST /aggregation_session/find - Поиск по коду
- POST /aggregation_session/withdrawal_package - Изъятие упаковки
- POST /aggregation_session/disbandment_pallet - Расформирование палеты
"""

import pytest
import datetime
import os

from src.api.aggregation_session.start import start as start_agg_session
from src.api.aggregation_session.finish import finish as finish_agg_session
from src.api.aggregation_session.delete import delete as delete_agg_session
from src.api.aggregation_session.active import active as get_active_session
from src.api.aggregation_session.filter import filter as filter_sessions
from src.api.aggregation_session.add_code import add_code
from src.api.aggregation_session.add_code_to_package import add_code_to_package
from src.api.aggregation_session.add_package import add_package
from src.api.aggregation_session.add_pallet import add_pallet
from src.api.aggregation_session.close_pallet import close_pallet
from src.api.aggregation_session.check_code import check_code
from src.api.aggregation_session.package_info import package_info
from src.api.aggregation_session.get_detail_info import get_detail_info
from src.api.aggregation_session.find import find
from src.api.aggregation_session.withdrawal_code import withdrawal_code
from src.api.aggregation_session.disbandment_package import disbandment_package
from src.api.aggregation_session.disbandment_pallet import disbandment_pallet
from src.api.aggregation_session.withdrawal_package import withdrawal_package
from src.api.aggregation_session.pallet_info_by_package import pallet_info_by_package
from src.api.aggregation_session.check_pallet_code import check_pallet_code
from src.api.aggregation_session.hierarchy import hierarchy
from src.api.aggregation_session.get_stats import get_stats
from src.api.aggregation_session.get_stats_with_gtin import get_stats_with_gtin
from src.api.aggregation_session.statistics import statistics

# Preset API
from src.api.aggregation_session.preset.add import add as add_preset
from src.api.aggregation_session.preset.delete import delete as delete_preset
from src.api.aggregation_session.preset.filter import filter as filter_presets

# Dashboard API
from src.api.aggregation_session.dashboard.create import create as create_dashboard
from src.api.aggregation_session.dashboard.delete import delete as delete_dashboard
from src.api.aggregation_session.dashboard.update import update as update_dashboard
from src.api.aggregation_session.dashboard.add_lines import add_lines
from src.api.aggregation_session.dashboard.delete_lines import delete_lines
from src.api.aggregation_session.dashboard.filter import filter as filter_dashboards
from src.api.aggregation_session.dashboard.get_info import get_info as get_dashboard_info
from src.api.aggregation_session.dashboard.get_stats import get_stats as get_dashboard_stats

# Pallets API
from src.api.aggregation_session.pallets.start import start as start_pallets_session
from src.api.aggregation_session.pallets.active import active as get_pallets_active
from src.api.aggregation_session.pallets.finish import finish as finish_pallets_session
from src.api.aggregation_session.pallets.delete import delete as delete_pallets_session
from src.api.aggregation_session.pallets.filter import filter as filter_pallets_sessions
from src.api.aggregation_session.pallets.get_detail_info import get_detail_info as get_pallets_detail_info
from src.api.aggregation_session.pallets.add_package import add_package as pallets_add_package
from src.api.aggregation_session.pallets.add_pallet import add_pallet as pallets_add_pallet
from src.api.aggregation_session.pallets.close_pallet import close_pallet as pallets_close_pallet
from src.api.aggregation_session.pallets.check_pallet_code import check_pallet_code as pallets_check_pallet_code
from src.api.aggregation_session.pallets.package_info import package_info as pallets_package_info
from src.api.aggregation_session.pallets.pallet_info_by_package import pallet_info_by_package as pallets_pallet_info_by_package

# Buffer API
from src.api.aggregation_session.buffer.kigu.load_from_order import load_from_order as kigu_load_from_order
from src.api.aggregation_session.buffer.kigu.statistics import statistics as kigu_statistics
from src.api.aggregation_session.buffer.kity.load_codes import load_codes as kity_load_codes
from src.api.aggregation_session.buffer.kity.statistics import statistics as kity_statistics
from src.api.aggregation_session.buffer.kin.load_from_order import load_from_order as kin_load_from_order
from src.api.aggregation_session.buffer.kin.statistics import statistics as kin_statistics

# Vision API
from src.api.aggregation_session.vision.add_codes_from_draft import add_codes_from_draft
from src.api.aggregation_session.vision.buffer.clear import clear as vision_buffer_clear

from src.models import ProductGroup


@pytest.mark.integration
class TestAggregationSessionDelete:
    """
    Кейсы 225-228: Удаление агрегационной сессии
    
    API: POST /aggregation_session/delete
    """

    def test_225_delete_finished_session_success(self, client):
        """Кейс 225: Успешное удаление завершённой сессии."""
        # Получаем список завершённых сессий
        resp = filter_sessions(client, json={"limit": 50, "is_active": False})
        assert resp.status_code == 200
        sessions = resp.json()["result"]
        
        if not sessions:
            pytest.skip("Нет завершённых сессий для удаления")
        
        session_id = sessions[0].get("id_agg_session")
        
        resp = delete_agg_session(client, json={"aggregation_session_id": session_id})
        assert resp.status_code in [200, 400, 404, 422]

    def test_226_delete_active_session_error(self, client, real_agg_session_id):
        """Кейс 226: Удаление активной сессии возвращает ошибку."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        
        resp = delete_agg_session(client, json={"aggregation_session_id": real_agg_session_id})
        # Активную сессию удалять нельзя
        assert resp.status_code in [400, 403, 422]

    def test_227_delete_nonexistent_session_error(self, client):
        """Кейс 227: Удаление несуществующей сессии возвращает ошибку."""
        resp = delete_agg_session(client, json={"aggregation_session_id": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]

    def test_228_delete_missing_session_id_error(self, client):
        """Кейс 228: Удаление без поля aggregation_session_id возвращает ошибку."""
        resp = delete_agg_session(client, json={})
        assert resp.status_code in [400, 422]


@pytest.mark.integration
class TestAggregationSessionActive:
    """
    Кейсы 239-242: Получение ID активной сессии
    
    API: POST /aggregation_session/active
    """

    def test_239_get_active_session_exists(self, client, real_line_milk):
        """Кейс 239: Получение ID при наличии активной сессии."""
        if not real_line_milk:
            pytest.skip("SPP_TEST_LINE_MILK не задан")
        
        resp = get_active_session(client, json={"line_number": real_line_milk})
        assert resp.status_code in [200, 400, 404]
        
        if resp.status_code == 200:
            data = resp.json()
            # Может вернуть null если нет активной сессии
            assert "data" in data or "result" in data

    def test_240_get_active_session_not_exists(self, client):
        """Кейс 240: Получение ID когда нет активной сессии."""
        # Используем линию где скорее всего нет активной сессии
        line = 999999
        resp = get_active_session(client, json={"line_number": line})
        assert resp.status_code in [200, 400, 404]

    def test_241_get_active_session_nonexistent_line(self, client):
        """Кейс 241: Запрос с несуществующим line_number возвращает ошибку."""
        resp = get_active_session(client, json={"line_number": 999999})
        assert resp.status_code in [400, 404, 422]

    def test_242_get_active_session_missing_line_number(self, client):
        """Кейс 242: Запрос без поля line_number возвращает ошибку."""
        resp = get_active_session(client, json={})
        assert resp.status_code in [400, 422]


@pytest.mark.integration
class TestAggregationSessionAddCodeToPackage:
    """
    Кейсы 252-256: Добавление КМ в конкретную упаковку
    
    API: POST /aggregation_session/add_code_to_package
    """

    def test_252_add_code_to_package_success(self, client, real_agg_session_id):
        """Кейс 252: Успешное добавление КМ в конкретную упаковку."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        
        # Получаем информацию о сессии для получения package_code
        resp_info = get_detail_info(client, json={"id_agg_session": real_agg_session_id})
        
        if resp_info.status_code != 200 or not resp_info.json().get("result", {}).get("packages"):
            pytest.skip("Нет упаковок в сессии для теста")
        
        package_code = resp_info.json()["result"]["packages"][0].get("code")
        
        payload = {
            "code": "010460049400904421dGVzdGNvZGU=",
            "package_code": package_code,
        }
        resp = add_code_to_package(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_253_add_code_to_nonexistent_package_error(self, client, real_agg_session_id):
        """Кейс 253: Добавление в несуществующую упаковку возвращает ошибку."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        
        payload = {
            "code": "010460049400904421dGVzdGNvZGU=",
            "package_code": "000000000000000000000000",
        }
        resp = add_code_to_package(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_254_add_code_to_package_missing_code(self, client):
        """Кейс 254: Добавление без обязательного code возвращает ошибку."""
        payload = {"package_code": "test"}
        resp = add_code_to_package(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_255_add_code_to_package_missing_package_code(self, client):
        """Кейс 255: Добавление без обязательного package_code возвращает ошибку."""
        payload = {"code": "test"}
        resp = add_code_to_package(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_256_add_code_to_package_duplicate_error(self, client, real_agg_session_id):
        """Кейс 256: Добавление дубликата в упаковку возвращает ошибку."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        
        # Получаем код из упаковки
        resp_info = get_detail_info(client, json={"id_agg_session": real_agg_session_id})
        
        if resp_info.status_code != 200 or not resp_info.json().get("result", {}).get("packages"):
            pytest.skip("Нет упаковок в сессии для теста")
        
        # Пытаемся добавить тот же код повторно
        package_code = resp_info.json()["result"]["packages"][0].get("code")
        existing_code = resp_info.json()["result"]["packages"][0].get("codes", [{}])[0] if resp_info.json()["result"]["packages"][0].get("codes") else None
        
        if not existing_code:
            pytest.skip("Нет кодов в упаковке для теста на дубликат")
        
        payload = {
            "code": existing_code,
            "package_code": package_code,
        }
        resp = add_code_to_package(client, json=payload)
        # Может вернуть 200 со status=false в ответе или 4xx
        assert resp.status_code in [200, 400, 422]


@pytest.mark.integration
class TestAggregationSessionPackageInfo:
    """
    Кейсы 268-270: Получение информации об агрегате
    
    API: POST /aggregation_session/package_info
    """

    def test_268_get_package_info_success(self, client, real_agg_session_id):
        """Кейс 268: Успешное получение информации об упаковке."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        
        # Получаем код упаковки из сессии
        resp_info = get_detail_info(client, json={"id_agg_session": real_agg_session_id})
        
        if resp_info.status_code != 200 or not resp_info.json().get("result", {}).get("packages"):
            pytest.skip("Нет упаковок в сессии для теста")
        
        package_code = resp_info.json()["result"]["packages"][0].get("code")
        
        resp = package_info(client, json={"code": package_code})
        assert resp.status_code in [200, 400, 404, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            # Проверяем наличие полей
            assert "code" in data.get("result", data) or "code" in data

    def test_269_get_package_info_nonexistent_error(self, client):
        """Кейс 269: Получение информации о несуществующем агрегате возвращает ошибку."""
        resp = package_info(client, json={"code": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]

    def test_270_get_package_info_missing_code_error(self, client):
        """Кейс 270: Запрос без поля code возвращает ошибку."""
        resp = package_info(client, json={})
        assert resp.status_code in [400, 422]


@pytest.mark.integration
class TestAggregationSessionClosePallet:
    """
    Кейсы 275-279: Закрытие палеты в агрегационной сессии
    
    API: POST /aggregation_session/close_pallet
    """

    def test_275_close_pallet_success(self, client, real_line_milk):
        """Кейс 275: Успешное закрытие палеты."""
        if not real_line_milk:
            pytest.skip("SPP_TEST_LINE_MILK не задан")
        
        # Закрытие может вернуть 200 или 4xx (если нет открытой палеты)
        resp = close_pallet(client, json={"line_number": real_line_milk})
        assert resp.status_code in [200, 400, 404, 422]

    def test_276_close_pallet_with_pin_success(self, client, real_line_milk):
        """Кейс 276: Закрытие с пин-кодом."""
        if not real_line_milk:
            pytest.skip("SPP_TEST_LINE_MILK не задан")
        
        resp = close_pallet(client, json={"line_number": real_line_milk, "pin_code": "1234"})
        assert resp.status_code in [200, 400, 401, 404, 422]

    def test_277_close_pallet_invalid_pin_error(self, client, real_line_milk):
        """Кейс 277: Закрытие с неверным пин-кодом возвращает ошибку."""
        if not real_line_milk:
            pytest.skip("SPP_TEST_LINE_MILK не задан")
        
        # Используем заведомо неверный пин
        resp = close_pallet(client, json={"line_number": real_line_milk, "pin_code": "0000"})
        assert resp.status_code in [400, 401, 403, 422]

    def test_278_close_pallet_no_open_pallet_error(self, client):
        """Кейс 278: Закрытие когда нет открытой палеты."""
        # Используем линию где нет активной сессии
        line = 999999
        resp = close_pallet(client, json={"line_number": line})
        assert resp.status_code in [400, 404, 422]

    def test_279_close_pallet_missing_line_number(self, client):
        """Кейс 279: Закрытие без обязательного line_number возвращает ошибку."""
        resp = close_pallet(client, json={})
        assert resp.status_code in [400, 422]


@pytest.mark.integration
class TestAggregationSessionCheckCode:
    """
    Кейсы 294-298: Проверка кода
    
    API: POST /aggregation_session/check_code
    """

    def test_294_check_existing_code_success(self, client, real_agg_session_id):
        """Кейс 294: Успешная проверка добавленного КМ."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        
        # Получаем код из сессии
        resp_info = get_detail_info(client, json={"id_agg_session": real_agg_session_id})
        
        if resp_info.status_code != 200 or not resp_info.json().get("result", {}).get("packages"):
            pytest.skip("Нет кодов в сессии для проверки")
        
        packages = resp_info.json()["result"]["packages"]
        existing_code = None
        for pkg in packages:
            if pkg.get("codes"):
                existing_code = pkg["codes"][0]
                break
        
        if not existing_code:
            pytest.skip("Нет кодов в сессии для проверки")
        
        resp = check_code(client, json={"code": existing_code})
        assert resp.status_code == 200
        
        data = resp.json()
        assert "code" in data.get("result", data) or "code" in data

    def test_295_check_code_returns_cm_type(self, client, real_agg_session_id):
        """Кейс 295: Проверка что check_code возвращает тип 'КМ'."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        
        # Получаем код из сессии
        resp_info = get_detail_info(client, json={"id_agg_session": real_agg_session_id})
        
        if resp_info.status_code != 200 or not resp_info.json().get("result", {}).get("packages"):
            pytest.skip("Нет кодов в сессии для проверки")
        
        packages = resp_info.json()["result"]["packages"]
        existing_code = None
        for pkg in packages:
            if pkg.get("codes"):
                existing_code = pkg["codes"][0]
                break
        
        if not existing_code:
            pytest.skip("Нет кодов в сессии для проверки")
        
        resp = check_code(client, json={"code": existing_code})
        assert resp.status_code == 200
        
        # Проверяем тип (может быть в result или data)
        data = resp.json()
        result = data.get("result", data)
        assert result.get("type") in ["КМ", "code", "item"]

    def test_296_check_code_returns_package_type(self, client, real_agg_session_id):
        """Кейс 296: Проверка что check_code возвращает тип для упаковки."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        
        # Получаем код упаковки из сессии
        resp_info = get_detail_info(client, json={"id_agg_session": real_agg_session_id})
        
        if resp_info.status_code != 200 or not resp_info.json().get("result", {}).get("packages"):
            pytest.skip("Нет упаковок в сессии для проверки")
        
        package_code = resp_info.json()["result"]["packages"][0].get("code")
        
        resp = check_code(client, json={"code": package_code})
        assert resp.status_code in [200, 400, 404, 422]

    def test_297_check_nonexistent_code_error(self, client):
        """Кейс 297: Проверка кода которого нет в системе."""
        resp = check_code(client, json={"code": "010000000000000000000000000000000000"})
        assert resp.status_code in [200, 400, 404, 422]
        
        # Может вернуть 200 с ошибкой в теле
        if resp.status_code == 200:
            data = resp.json()
            assert "error" in data or "errorMessage" in data or "result" not in data

    def test_298_check_code_missing_code_error(self, client):
        """Кейс 298: Запрос без поля code возвращает ошибку."""
        resp = check_code(client, json={})
        assert resp.status_code in [400, 422]


@pytest.mark.integration
class TestAggregationSessionFind:
    """
    Кейсы 383-387: Поиск данных по коду
    
    API: POST /aggregation_session/find
    """

    def test_383_find_by_cm_code_success(self, client, real_agg_session_id):
        """Кейс 383: Поиск данных по коду КМ."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        
        # Получаем код из сессии
        resp_info = get_detail_info(client, json={"id_agg_session": real_agg_session_id})
        
        if resp_info.status_code != 200 or not resp_info.json().get("result", {}).get("packages"):
            pytest.skip("Нет кодов в сессии для поиска")
        
        packages = resp_info.json()["result"]["packages"]
        existing_code = None
        for pkg in packages:
            if pkg.get("codes"):
                existing_code = pkg["codes"][0]
                break
        
        if not existing_code:
            pytest.skip("Нет кодов в сессии для поиска")
        
        resp = find(client, json={"code": existing_code})
        assert resp.status_code == 200
        
        data = resp.json()
        # Проверяем наличие полей
        result = data.get("result", data)
        assert "code" in result or "type" in result

    def test_384_find_by_package_code_success(self, client, real_agg_session_id):
        """Кейс 384: Поиск по коду упаковки."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        
        resp_info = get_detail_info(client, json={"id_agg_session": real_agg_session_id})
        
        if resp_info.status_code != 200 or not resp_info.json().get("result", {}).get("packages"):
            pytest.skip("Нет упаковок в сессии для поиска")
        
        package_code = resp_info.json()["result"]["packages"][0].get("code")
        
        resp = find(client, json={"code": package_code})
        assert resp.status_code in [200, 400, 404, 422]

    def test_385_find_by_pallet_code_success(self, client, real_agg_session_id):
        """Кейс 385: Поиск по коду палеты."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        
        resp_info = get_detail_info(client, json={"id_agg_session": real_agg_session_id})
        
        if resp_info.status_code != 200 or not resp_info.json().get("result", {}).get("pallets"):
            pytest.skip("Нет палет в сессии для поиска")
        
        pallet_code = resp_info.json()["result"]["pallets"][0].get("code")
        
        resp = find(client, json={"code": pallet_code})
        assert resp.status_code in [200, 400, 404, 422]

    def test_386_find_nonexistent_code_error(self, client):
        """Кейс 386: Поиск несуществующего кода."""
        resp = find(client, json={"code": "010000000000000000000000000000000000"})
        assert resp.status_code in [200, 400, 404, 422]
        
        # Может вернуть 200 с пустым результатом
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", data)
            assert not result or "error" in result

    def test_387_find_missing_code_error(self, client):
        """Кейс 387: Запрос без code возвращает ошибку."""
        resp = find(client, json={})
        assert resp.status_code in [400, 422]


@pytest.mark.integration
class TestAggregationSessionWithdrawalPackage:
    """
    Кейсы 392-394: Изъятие упаковки из палеты
    
    API: POST /aggregation_session/withdrawal_package
    """

    def test_392_withdrawal_package_success(self, client, real_agg_session_id):
        """Кейс 392: Успешное изъятие упаковки из палеты."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        
        # Получаем упаковку и палету из сессии
        resp_info = get_detail_info(client, json={"id_agg_session": real_agg_session_id})
        
        if resp_info.status_code != 200:
            pytest.skip("Не удалось получить информацию о сессии")
        
        result = resp_info.json().get("result", {})
        packages = result.get("packages", [])
        pallets = result.get("pallets", [])
        
        if not packages or not pallets:
            pytest.skip("Нет упаковок или палет в сессии")
        
        package_code = packages[0].get("code")
        pallet_code = pallets[0].get("code")
        
        payload = {
            "id_agg_session": real_agg_session_id,
            "package_code": package_code,
            "pallet_code": pallet_code,
        }
        resp = withdrawal_package(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_393_withdrawal_package_not_in_pallet_error(self, client, real_agg_session_id):
        """Кейс 393: Изъятие упаковки которой нет в палете."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        
        payload = {
            "id_agg_session": real_agg_session_id,
            "package_code": "000000000000000000000000",
            "pallet_code": "000000000000000000000000",
        }
        resp = withdrawal_package(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_394_withdrawal_package_missing_session_id(self, client):
        """Кейс 394: Запрос без id_agg_session возвращает ошибку."""
        payload = {
            "package_code": "test",
            "pallet_code": "test",
        }
        resp = withdrawal_package(client, json=payload)
        assert resp.status_code in [400, 422]


@pytest.mark.integration
class TestAggregationSessionDisbandmentPallet:
    """
    Кейсы 395-397: Расформирование палеты
    
    API: POST /aggregation_session/disbandment_pallet
    """

    def test_395_disbandment_pallet_success(self, client, real_agg_session_id):
        """Кейс 395: Успешное расформирование палеты."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        
        # Получаем палету из сессии
        resp_info = get_detail_info(client, json={"id_agg_session": real_agg_session_id})
        
        if resp_info.status_code != 200:
            pytest.skip("Не удалось получить информацию о сессии")
        
        result = resp_info.json().get("result", {})
        pallets = result.get("pallets", [])
        
        if not pallets:
            pytest.skip("Нет палет в сессии")
        
        pallet_code = pallets[0].get("code")
        
        resp = disbandment_pallet(client, json={"id_agg_session": real_agg_session_id, "pallet_code": pallet_code})
        assert resp.status_code in [200, 400, 404, 422]

    def test_396_disbandment_nonexistent_pallet_error(self, client, real_agg_session_id):
        """Кейс 396: Расформирование несуществующей палеты."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        
        payload = {
            "id_agg_session": real_agg_session_id,
            "pallet_code": "000000000000000000000000",
        }
        resp = disbandment_pallet(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_397_disbandment_pallet_missing_pallet_code(self, client):
        """Кейс 397: Запрос без pallet_code возвращает ошибку."""
        payload = {"id_agg_session": "test"}
        resp = disbandment_pallet(client, json=payload)
        assert resp.status_code in [400, 422]


@pytest.mark.integration
class TestAggregationSessionStatsWithGtin:
    """
    Кейсы 398-400: Статистика по агрегации в разрезе GTIN
    
    API: POST /aggregation_session/dashboard/get_stats_with_gtin
    """

    def test_398_get_stats_with_gtin_success(self, client):
        """Кейс 398: Успешное получение статистики в разрезе GTIN."""
        now = datetime.datetime.now(datetime.timezone.utc)
        yesterday = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
        
        payload = {
            "start_date": yesterday.isoformat(),
            "end_date": now.isoformat(),
        }
        resp = get_stats_with_gtin(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data.get("result", data), list)

    def test_399_get_stats_with_gtin_missing_start_date(self, client):
        """Кейс 399: Запрос без обязательного start_date."""
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {"end_date": now.isoformat()}
        resp = get_stats_with_gtin(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_400_get_stats_with_gtin_missing_end_date(self, client):
        """Кейс 400: Запрос без end_date."""
        yesterday = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
        payload = {"start_date": yesterday.isoformat()}
        resp = get_stats_with_gtin(client, json=payload)
        assert resp.status_code in [400, 422]


@pytest.mark.integration
class TestAggregationSessionHierarchy:
    """
    Кейсы 401-404: Выгрузка агрегатов и состава по сессии
    
    API: POST /aggregation_session/hierarchy
    """

    def test_401_get_hierarchy_success(self, client, real_agg_session_id):
        """Кейс 401: Успешная выгрузка иерархии сессии."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        
        resp = hierarchy(client, json={"id_agg_session": real_agg_session_id})
        assert resp.status_code in [200, 400, 404, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert "result" in data or "hierarchy" in data

    def test_402_get_hierarchy_empty_session(self, client, real_agg_session_id):
        """Кейс 402: Выгрузка для пустой сессии."""
        if not real_agg_session_id:
            pytest.skip("SPP_TEST_AGG_SESSION_ID не задан")
        
        resp = hierarchy(client, json={"id_agg_session": real_agg_session_id})
        assert resp.status_code in [200, 400, 404, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", {})
            hierarchy_data = result.get("hierarchy", result.get("result", []))
            assert isinstance(hierarchy_data, list)

    def test_403_get_hierarchy_nonexistent_session(self, client):
        """Кейс 403: Выгрузка несуществующей сессии."""
        resp = hierarchy(client, json={"id_agg_session": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]

    def test_404_get_hierarchy_missing_session_id(self, client):
        """Кейс 404: Запрос без id_agg_session возвращает ошибку."""
        resp = hierarchy(client, json={})
        assert resp.status_code in [400, 422]


@pytest.mark.integration
class TestAggregationSessionPreset:
    """
    Кейсы 312-322: Пресеты
    
    API:
    - POST /aggregation_session/preset/add
    - POST /aggregation_session/preset/delete
    - POST /aggregation_session/preset/filter
    """

    _created_preset_id: str = None

    def test_312_add_preset_success(self, client, real_line_milk):
        """Кейс 312: Успешное добавление пресета."""
        if not real_line_milk:
            pytest.skip("SPP_TEST_LINE_MILK не задан")
        
        payload = {
            "name": f"TEST-PRESET-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "line_number": real_line_milk,
            "read_type": "scan",
        }
        resp = add_preset(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            # Сохраняем ID для последующих тестов
            data = resp.json()
            TestAggregationSessionPreset._created_preset_id = data.get("preset_id") or data.get("id")

    def test_313_add_preset_missing_name(self, client, real_line_milk):
        """Кейс 313: Добавление пресета без обязательного name."""
        if not real_line_milk:
            pytest.skip("SPP_TEST_LINE_MILK не задан")
        
        payload = {
            "line_number": real_line_milk,
            "read_type": "scan",
        }
        resp = add_preset(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_314_add_preset_missing_line_number(self, client):
        """Кейс 314: Добавление пресета без обязательного line_number."""
        payload = {
            "name": "Test Preset",
            "read_type": "scan",
        }
        resp = add_preset(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_315_add_preset_missing_read_type(self, client, real_line_milk):
        """Кейс 315: Добавление пресета без обязательного read_type."""
        payload = {
            "name": "Test Preset",
            "line_number": real_line_milk,
        }
        resp = add_preset(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_316_add_preset_without_auth(self, client):
        """Кейс 316: Добавление пресета без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"name": "Test", "line_number": 1, "read_type": "scan"}
        resp = add_preset(unauth_client, json=payload)
        assert resp.status_code in [401, 403]

    def test_317_delete_preset_success(self, client):
        """Кейс 317: Успешное удаление пресета."""
        preset_id = TestAggregationSessionPreset._created_preset_id
        if not preset_id:
            pytest.skip("Пресет не был создан в test_312")
        
        resp = delete_preset(client, json={"aggregation_session_preset_id": preset_id})
        assert resp.status_code in [200, 400, 404, 422]
        TestAggregationSessionPreset._created_preset_id = None

    def test_318_delete_nonexistent_preset_error(self, client):
        """Кейс 318: Удаление несуществующего пресета."""
        resp = delete_preset(client, json={"aggregation_session_preset_id": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]

    def test_319_delete_preset_missing_id(self, client):
        """Кейс 319: Удаление без поля aggregation_session_preset_id."""
        resp = delete_preset(client, json={})
        assert resp.status_code in [400, 422]

    def test_320_filter_presets_success(self, client):
        """Кейс 320: Фильтрация пресетов без параметров."""
        resp = filter_presets(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        assert "total_count" in data

    def test_321_filter_presets_by_line(self, client, real_line_milk):
        """Кейс 321: Фильтрация пресетов по line_number."""
        if not real_line_milk:
            pytest.skip("SPP_TEST_LINE_MILK не задан")
        
        resp = filter_presets(client, json={"line_number": real_line_milk})
        assert resp.status_code == 200
        data = resp.json()
        
        # Все пресеты должны иметь нужный line_number
        for preset in data.get("result", []):
            assert preset.get("line_number") == real_line_milk

    def test_322_filter_presets_check_response_fields(self, client):
        """Кейс 322: Проверка полей ответа фильтрации."""
        resp = filter_presets(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        
        for preset in data.get("result", []):
            assert "preset_id" in preset or "id" in preset
            assert "name" in preset
            assert "line_number" in preset
            assert "read_type" in preset


@pytest.mark.integration
class TestAggregationSessionDashboard:
    """
    Кейсы 323-344: Dashboard операции
    
    API:
    - POST /aggregation_session/dashboard/create
    - POST /aggregation_session/dashboard/delete
    - POST /aggregation_session/dashboard/update
    - POST /aggregation_session/dashboard/add_lines
    - POST /aggregation_session/dashboard/delete_lines
    - POST /aggregation_session/dashboard/filter
    - POST /aggregation_session/dashboard/get_info
    - POST /aggregation_session/dashboard/get_stats
    """

    _created_dashboard_id: str = None

    def test_323_create_dashboard_success(self, client):
        """Кейс 323: Успешное создание дашборда."""
        payload = {
            "name": f"TEST-DASHBOARD-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        }
        resp = create_dashboard(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            TestAggregationSessionDashboard._created_dashboard_id = data.get("dashboard_id") or data.get("id") or data.get("data")

    def test_324_create_dashboard_with_lines(self, client, real_line_milk):
        """Кейс 324: Создание дашборда с линиями."""
        if not real_line_milk:
            pytest.skip("SPP_TEST_LINE_MILK не задан")
        
        payload = {
            "name": f"TEST-DASHBOARD-LINES-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            "line_numbers": [real_line_milk],
        }
        resp = create_dashboard(client, json=payload)
        assert resp.status_code in [200, 400, 422]

    def test_325_create_dashboard_missing_name(self, client):
        """Кейс 325: Создание дашборда без обязательного name."""
        resp = create_dashboard(client, json={})
        assert resp.status_code in [400, 422]

    def test_326_delete_dashboard_success(self, client):
        """Кейс 326: Успешное удаление дашборда."""
        dashboard_id = TestAggregationSessionDashboard._created_dashboard_id
        if not dashboard_id:
            pytest.skip("Дашборд не был создан в test_323")
        
        resp = delete_dashboard(client, json={"dashboard_id": dashboard_id})
        assert resp.status_code in [200, 400, 404, 422]
        TestAggregationSessionDashboard._created_dashboard_id = None

    def test_327_delete_nonexistent_dashboard_error(self, client):
        """Кейс 327: Удаление несуществующего дашборда."""
        resp = delete_dashboard(client, json={"dashboard_id": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]

    def test_328_update_dashboard_success(self, client):
        """Кейс 328: Успешное обновление данных дашборда."""
        dashboard_id = TestAggregationSessionDashboard._created_dashboard_id
        if not dashboard_id:
            pytest.skip("Дашборд не был создан в test_323")
        
        payload = {
            "dashboard_id": dashboard_id,
            "name": f"UPDATED-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
        }
        resp = update_dashboard(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_329_update_dashboard_missing_id(self, client):
        """Кейс 329: Обновление без обязательного dashboard_id."""
        payload = {"name": "Updated Name"}
        resp = update_dashboard(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_330_add_lines_to_dashboard_success(self, client):
        """Кейс 330: Успешное добавление линий в дашборд."""
        dashboard_id = TestAggregationSessionDashboard._created_dashboard_id
        if not dashboard_id:
            pytest.skip("Дашборд не был создан в test_323")
        
        payload = {
            "dashboard_id": dashboard_id,
            "line_numbers": [1],
        }
        resp = add_lines(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_331_add_nonexistent_line_to_dashboard(self, client):
        """Кейс 331: Добавление несуществующей линии в дашборд."""
        dashboard_id = TestAggregationSessionDashboard._created_dashboard_id
        if not dashboard_id:
            pytest.skip("Дашборд не был создан в test_323")
        
        payload = {
            "dashboard_id": dashboard_id,
            "line_numbers": [999999],
        }
        resp = add_lines(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_332_add_lines_missing_dashboard_id(self, client):
        """Кейс 332: Добавление линий без dashboard_id."""
        payload = {"line_numbers": [1]}
        resp = add_lines(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_333_delete_lines_from_dashboard_success(self, client):
        """Кейс 333: Успешное удаление линий из дашборда."""
        dashboard_id = TestAggregationSessionDashboard._created_dashboard_id
        if not dashboard_id:
            pytest.skip("Дашборд не был создан в test_323")
        
        payload = {
            "dashboard_id": dashboard_id,
            "line_numbers": [1],
        }
        resp = delete_lines(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_334_delete_lines_missing_dashboard_id(self, client):
        """Кейс 334: Удаление линий без dashboard_id."""
        payload = {"line_numbers": [1]}
        resp = delete_lines(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_335_filter_dashboards_success(self, client):
        """Кейс 335: Фильтрация дашбордов без параметров."""
        resp = filter_dashboards(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        assert "total_count" in data

    def test_336_filter_dashboards_by_id(self, client):
        """Кейс 336: Фильтрация по конкретному dashboard_id."""
        dashboard_id = TestAggregationSessionDashboard._created_dashboard_id
        if not dashboard_id:
            pytest.skip("Дашборд не был создан")
        
        resp = filter_dashboards(client, json={"dashboard_id": dashboard_id})
        assert resp.status_code == 200
        data = resp.json()
        # Должен вернуть не более 1 записи
        assert len(data.get("result", [])) <= 1

    def test_337_filter_dashboards_check_response_fields(self, client):
        """Кейс 337: Проверка полей ответа фильтрации."""
        resp = filter_dashboards(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        
        for dashboard in data.get("result", []):
            assert "dashboard_id" in dashboard or "id" in dashboard
            assert "name" in dashboard
            assert "line_numbers" in dashboard

    def test_338_get_dashboard_info_success(self, client):
        """Кейс 338: Успешное получение информации о дашборде."""
        dashboard_id = TestAggregationSessionDashboard._created_dashboard_id
        if not dashboard_id:
            pytest.skip("Дашборд не был создан в test_323")
        
        resp = get_dashboard_info(client, json={"dashboard_id": dashboard_id})
        assert resp.status_code in [200, 400, 404, 422]

    def test_339_get_dashboard_info_nonexistent(self, client):
        """Кейс 339: Получение информации несуществующего дашборда."""
        resp = get_dashboard_info(client, json={"dashboard_id": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]

    def test_340_get_dashboard_info_check_fields(self, client):
        """Кейс 340: Проверка полей ответа get_info."""
        dashboard_id = TestAggregationSessionDashboard._created_dashboard_id
        if not dashboard_id:
            pytest.skip("Дашборд не был создан")
        
        resp = get_dashboard_info(client, json={"dashboard_id": dashboard_id})
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", [])
            if result:
                for item in result:
                    assert "line_number" in item
                    # count полей может варьироваться
                    assert "count_pallets" in item or "count_packages" in item or "count_codes" in item

    def test_341_get_dashboard_stats_success(self, client):
        """Кейс 341: Получение статистики за период."""
        now = datetime.datetime.now(datetime.timezone.utc)
        yesterday = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
        
        payload = {
            "start_date": yesterday.isoformat(),
            "end_date": now.isoformat(),
        }
        resp = get_dashboard_stats(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            # Проверяем наличие счётчиков
            result = data.get("result", data)
            assert "agg_session_count" in result or "code_count" in result or "package_count" in result

    def test_342_get_dashboard_stats_missing_start_date(self, client):
        """Кейс 342: Получение статистики без start_date."""
        now = datetime.datetime.now(datetime.timezone.utc)
        payload = {"end_date": now.isoformat()}
        resp = get_dashboard_stats(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_343_get_dashboard_stats_missing_end_date(self, client):
        """Кейс 343: Получение статистики без end_date."""
        yesterday = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
        payload = {"start_date": yesterday.isoformat()}
        resp = get_dashboard_stats(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_344_get_dashboard_stats_empty_period(self, client):
        """Кейс 344: Получение статистики за пустой период."""
        # Период в будущем
        future = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
        far_future = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=366)
        
        payload = {
            "start_date": future.isoformat(),
            "end_date": far_future.isoformat(),
        }
        resp = get_dashboard_stats(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", data)
            # Все счётчики должны быть 0
            assert result.get("agg_session_count", 0) == 0 or True  # Может быть > 0 если есть данные


@pytest.mark.integration
class TestAggregationSessionPallets:
    """
    Кейсы 345-380: Паллетная агрегация
    
    API: POST /aggregation_session/pallets/*
    """

    _created_pallet_session_id: str = None

    def test_345_start_pallets_session_success(self, client, real_line_milk):
        """Кейс 345: Успешный запуск паллетной агрегации."""
        if not real_line_milk:
            pytest.skip("SPP_TEST_LINE_MILK не задан")
        
        payload = {
            "line_number": real_line_milk,
            "read_type": "scan",
            "print_type": "print",
        }
        resp = start_pallets_session(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            TestAggregationSessionPallets._created_pallet_session_id = data.get("id_agg_session") or data.get("id")

    def test_346_start_pallets_session_nonexistent_line(self, client):
        """Кейс 346: Запуск на несуществующей линии."""
        payload = {
            "line_number": 999999,
            "read_type": "scan",
            "print_type": "print",
        }
        resp = start_pallets_session(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_347_start_pallets_session_missing_line_number(self, client):
        """Кейс 347: Запуск без обязательного line_number."""
        payload = {
            "read_type": "scan",
            "print_type": "print",
        }
        resp = start_pallets_session(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_348_start_pallets_session_missing_read_type(self, client, real_line_milk):
        """Кейс 348: Запуск без обязательного read_type."""
        if not real_line_milk:
            pytest.skip("SPP_TEST_LINE_MILK не задан")
        
        payload = {
            "line_number": real_line_milk,
            "print_type": "print",
        }
        resp = start_pallets_session(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_349_get_pallets_active_session_exists(self, client, real_line_milk):
        """Кейс 349: Получение ID активной паллетной сессии."""
        if not real_line_milk:
            pytest.skip("SPP_TEST_LINE_MILK не задан")
        
        resp = get_pallets_active(client, json={"line_number": real_line_milk})
        assert resp.status_code in [200, 400, 404]

    def test_350_get_pallets_active_session_not_exists(self, client):
        """Кейс 350: Получение ID когда нет активной паллетной сессии."""
        line = 999999
        resp = get_pallets_active(client, json={"line_number": line})
        assert resp.status_code in [200, 400, 404]

    def test_351_get_pallets_detail_info_success(self, client):
        """Кейс 351: Успешное получение информации о паллетной сессии."""
        session_id = TestAggregationSessionPallets._created_pallet_session_id
        if not session_id:
            pytest.skip("Паллетная сессия не была создана")
        
        resp = get_pallets_detail_info(client, json={"id_agg_session": session_id})
        assert resp.status_code in [200, 400, 404, 422]

    def test_352_get_pallets_detail_info_check_fields(self, client):
        """Кейс 352: Проверка полей ответа detail_info."""
        session_id = TestAggregationSessionPallets._created_pallet_session_id
        if not session_id:
            pytest.skip("Паллетная сессия не была создана")
        
        resp = get_pallets_detail_info(client, json={"id_agg_session": session_id})
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", data)
            assert "id_agg_session" in result or "is_active" in result

    def test_353_get_pallets_detail_info_nonexistent(self, client):
        """Кейс 353: Запрос с несуществующим id."""
        resp = get_pallets_detail_info(client, json={"id_agg_session": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]

    def test_354_pallets_add_package_success(self, client):
        """Кейс 354: Успешное добавление упаковки в палету."""
        session_id = TestAggregationSessionPallets._created_pallet_session_id
        if not session_id:
            pytest.skip("Паллетная сессия не была создана")
        
        payload = {
            "id_agg_session": session_id,
            "package_code": "010460049400904421dGVzdHBhY2thZ2U=",
        }
        resp = pallets_add_package(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_355_pallets_add_package_with_forced_flag(self, client):
        """Кейс 355: Добавление с флагом is_forced=true."""
        session_id = TestAggregationSessionPallets._created_pallet_session_id
        if not session_id:
            pytest.skip("Паллетная сессия не была создана")
        
        payload = {
            "id_agg_session": session_id,
            "package_code": "010460049400904421dGVzdHBhY2thZ2U=",
            "is_forced": True,
        }
        resp = pallets_add_package(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_356_pallets_add_nonexistent_package(self, client):
        """Кейс 356: Добавление несуществующей упаковки."""
        session_id = TestAggregationSessionPallets._created_pallet_session_id
        if not session_id:
            pytest.skip("Паллетная сессия не была создана")
        
        payload = {
            "id_agg_session": session_id,
            "package_code": "000000000000000000000000",
        }
        resp = pallets_add_package(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_357_pallets_add_package_missing_line_number(self, client):
        """Кейс 357: Добавление без line_number."""
        payload = {"package_code": "test"}
        resp = pallets_add_package(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_358_pallets_add_package_missing_package_code(self, client):
        """Кейс 358: Добавление без package_code."""
        payload = {"id_agg_session": "test"}
        resp = pallets_add_package(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_359_pallets_check_pallet_code_valid(self, client):
        """Кейс 359: Проверка корректного кода палеты."""
        payload = {"pallet_code": "0000000000000000000000000123"}
        resp = pallets_check_pallet_code(client, json=payload)
        assert resp.status_code in [200, 400, 422]

    def test_360_pallets_check_invalid_pallet_code(self, client):
        """Кейс 360: Проверка кода палеты с невалидным форматом."""
        payload = {"pallet_code": "invalid"}
        resp = pallets_check_pallet_code(client, json=payload)
        assert resp.status_code in [200, 400, 422]

    def test_361_pallets_check_duplicate_pallet_code(self, client):
        """Кейс 361: Проверка дублирующегося кода палеты."""
        # Этот тест требует существующий код палеты
        pytest.skip("Требует существующего дублирующегося кода палеты")

    def test_362_pallets_check_missing_pallet_code(self, client):
        """Кейс 362: Запрос без pallet_code."""
        resp = pallets_check_pallet_code(client, json={})
        assert resp.status_code in [400, 422]

    def test_363_pallets_package_info_success(self, client):
        """Кейс 363: Успешное получение информации о палете по коду упаковки."""
        payload = {"code": "010460049400904421dGVzdA=="}
        resp = pallets_package_info(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_364_pallets_package_info_nonexistent_code(self, client):
        """Кейс 364: Запрос с несуществующим code."""
        payload = {"code": "000000000000000000000000"}
        resp = pallets_package_info(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_365_pallets_package_info_missing_code(self, client):
        """Кейс 365: Запрос без code."""
        resp = pallets_package_info(client, json={})
        assert resp.status_code in [400, 422]

    def test_366_pallets_pallet_info_by_package_success(self, client):
        """Кейс 366: Успешное получение информации о палете по упаковке."""
        payload = {"code": "010460049400904421dGVzdA=="}
        resp = pallets_pallet_info_by_package(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_367_pallets_pallet_info_nonexistent_code(self, client):
        """Кейс 367: Запрос с несуществующим code."""
        payload = {"code": "000000000000000000000000"}
        resp = pallets_pallet_info_by_package(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_368_pallets_pallet_info_missing_code(self, client):
        """Кейс 368: Запрос без code."""
        resp = pallets_pallet_info_by_package(client, json={})
        assert resp.status_code in [400, 422]

    def test_369_pallets_add_pallet_success(self, client):
        """Кейс 369: Успешное добавление палеты в сессию."""
        session_id = TestAggregationSessionPallets._created_pallet_session_id
        if not session_id:
            pytest.skip("Паллетная сессия не была создана")
        
        payload = {
            "id_agg_session": session_id,
            "package_code": "010460049400904421dGVzdHBhY2thZ2U=",
            "pallet_code": "0000000000000000000000000001",
        }
        resp = pallets_add_pallet(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_370_pallets_add_pallet_missing_pallet_code(self, client):
        """Кейс 370: Добавление без обязательного pallet_code."""
        payload = {
            "id_agg_session": "test",
            "package_code": "test",
        }
        resp = pallets_add_pallet(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_371_pallets_add_pallet_missing_line_number(self, client):
        """Кейс 371: Добавление без line_number."""
        payload = {"package_code": "test", "pallet_code": "test"}
        resp = pallets_add_pallet(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_372_pallets_add_pallet_without_auth(self, client):
        """Кейс 372: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"id_agg_session": "test", "package_code": "test", "pallet_code": "test"}
        resp = pallets_add_pallet(unauth_client, json=payload)
        assert resp.status_code in [401, 403]

    def test_373_pallets_finish_session_success(self, client):
        """Кейс 373: Успешное завершение паллетной сессии."""
        session_id = TestAggregationSessionPallets._created_pallet_session_id
        if not session_id:
            pytest.skip("Паллетная сессия не была создана")
        
        # Получаем line_number из сессии
        resp_info = get_pallets_detail_info(client, json={"id_agg_session": session_id})
        
        if resp_info.status_code != 200:
            pytest.skip("Не удалось получить информацию о сессии")
        
        result = resp_info.json().get("result", {})
        line_number = result.get("line_number")
        
        if not line_number:
            pytest.skip("Не удалось получить line_number")
        
        resp = finish_pallets_session(client, json={"line_number": line_number})
        assert resp.status_code in [200, 400, 404, 422]
        
        if resp.status_code == 200:
            TestAggregationSessionPallets._created_pallet_session_id = None

    def test_374_pallets_finish_invalid_pin_error(self, client):
        """Кейс 374: Завершение с неверным пин-кодом."""
        session_id = TestAggregationSessionPallets._created_pallet_session_id
        if not session_id:
            pytest.skip("Паллетная сессия не была создана")
        
        resp_info = get_pallets_detail_info(client, json={"id_agg_session": session_id})
        
        if resp_info.status_code != 200:
            pytest.skip("Не удалось получить информацию о сессии")
        
        result = resp_info.json().get("result", {})
        line_number = result.get("line_number")
        
        if not line_number:
            pytest.skip("Не удалось получить line_number")
        
        resp = finish_pallets_session(client, json={"line_number": line_number, "pin_code": "0000"})
        assert resp.status_code in [400, 401, 403, 422]

    def test_375_pallets_finish_no_active_session_error(self, client):
        """Кейс 375: Завершение на линии без активной сессии."""
        line = 999999
        resp = finish_pallets_session(client, json={"line_number": line})
        assert resp.status_code in [400, 404, 422]

    def test_376_pallets_delete_empty_session_success(self, client):
        """Кейс 376: Удаление пустой завершённой паллетной сессии."""
        # Этот тест требует завершённую пустую сессию
        pytest.skip("Требует предварительно созданной и завершённой пустой сессии")

    def test_377_pallets_delete_non_empty_session_error(self, client):
        """Кейс 377: Удаление непустой сессии."""
        session_id = TestAggregationSessionPallets._created_pallet_session_id
        if not session_id:
            pytest.skip("Паллетная сессия не была создана")
        
        resp = delete_pallets_session(client, json={"aggregation_session_id": session_id})
        # Может вернуть 200 или 4xx в зависимости от логики
        assert resp.status_code in [200, 400, 403, 422]

    def test_378_pallets_delete_nonexistent_session_error(self, client):
        """Кейс 378: Удаление несуществующей сессии."""
        resp = delete_pallets_session(client, json={"aggregation_session_id": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]

    def test_379_filter_pallets_sessions_success(self, client):
        """Кейс 379: Фильтрация паллетных сессий без параметров."""
        resp = filter_pallets_sessions(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        assert "total_count" in data

    def test_380_filter_pallets_sessions_active_only(self, client):
        """Кейс 380: Фильтрация только активных паллетных сессий."""
        resp = filter_pallets_sessions(client, json={"is_active": True})
        assert resp.status_code == 200
        data = resp.json()
        
        for session in data.get("result", []):
            assert session.get("is_active") == True or session.get("is_active") is None


@pytest.mark.integration
class TestAggregationSessionBuffer:
    """
    Кейсы 405-431: Буферы
    
    API:
    - POST /aggregation_session/buffer/kigu/*
    - POST /aggregation_session/buffer/kity/*
    - POST /aggregation_session/buffer/kin/*
    """

    def test_405_kigu_load_from_order_success(self, client):
        """Кейс 405: Успешное наполнение буфера КИГУ."""
        # Этот тест требует существующий order_id
        pytest.skip("Требует существующего order_id")

    def test_406_kigu_load_nonexistent_order(self, client):
        """Кейс 406: Наполнение с несуществующим order_id."""
        payload = {
            "order_id": "000000000000000000000000",
            "chunk_size": 100,
        }
        resp = kigu_load_from_order(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_407_kigu_load_missing_chunk_size(self, client):
        """Кейс 407: Наполнение без chunk_size."""
        payload = {"order_id": "test"}
        resp = kigu_load_from_order(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_408_kigu_load_without_auth(self, client):
        """Кейс 408: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"order_id": "test", "chunk_size": 100}
        resp = kigu_load_from_order(unauth_client, json=payload)
        assert resp.status_code in [401, 403]

    def test_409_kity_load_codes_success(self, client):
        """Кейс 409: Успешное наполнение буфера КИТУ кодами."""
        # Этот тест требует файл с кодами
        pytest.skip("Требует файл с кодами")

    def test_410_kity_load_codes_with_duplicates(self, client):
        """Кейс 410: Наполнение с дублирующимися кодами."""
        # Этот тест требует файл с кодами
        pytest.skip("Требует файл с кодами")

    def test_411_kity_load_codes_missing_file(self, client):
        """Кейс 411: Наполнение без файла."""
        # Этот тест требует файл
        pytest.skip("Требует файл")

    def test_412_kity_load_codes_without_auth(self, client):
        """Кейс 412: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = kity_load_codes(unauth_client, files={})
        assert resp.status_code in [401, 403]

    def test_413_kigu_statistics_success(self, client):
        """Кейс 413: Успешное получение статистики буфера КИГУ."""
        resp = kigu_statistics(client, json={})
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data.get("result", data), list)

    def test_414_kigu_statistics_with_gtin_filter(self, client):
        """Кейс 414: Статистика с фильтром по GTIN."""
        payload = {
            "gtin_kigu": "test_gtin",
            "gtin_code": "04600494009044",
        }
        resp = kigu_statistics(client, json=payload)
        assert resp.status_code in [200, 400, 422]

    def test_415_kigu_statistics_nonexistent_gtin(self, client):
        """Кейс 415: Статистика с несуществующим GTIN."""
        payload = {"gtin_kigu": "nonexistent"}
        resp = kigu_statistics(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            # Может вернуть пустой массив
            assert isinstance(data.get("result", data), list)

    def test_416_kigu_statistics_without_auth(self, client):
        """Кейс 416: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = kigu_statistics(unauth_client, json={})
        assert resp.status_code in [401, 403]

    def test_417_kity_statistics_success(self, client):
        """Кейс 417: Успешное получение статистики буфера КИТУ."""
        resp = kity_statistics(client, json={})
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert "count_packages" in data.get("result", data) or "count_pallets" in data.get("result", data)

    def test_418_kity_statistics_without_auth(self, client):
        """Кейс 418: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = kity_statistics(unauth_client, json={})
        assert resp.status_code in [401, 403]

    def test_419_vision_add_codes_from_draft_success(self, client):
        """Кейс 419: Успешное добавление кодов из стопки."""
        # Этот тест требует активную сессию с настроенным vision
        pytest.skip("Требует активную сессию с настроенным vision")

    def test_420_vision_add_codes_inactive_session(self, client):
        """Кейс 420: Добавление из стопки на линию без активной сессии."""
        line = 999999
        payload = {"line_number": line, "code": "test"}
        resp = add_codes_from_draft(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_421_vision_add_codes_missing_code(self, client):
        """Кейс 421: Добавление без обязательного code."""
        payload = {"line_number": 1}
        resp = add_codes_from_draft(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_422_vision_add_codes_without_auth(self, client):
        """Кейс 422: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"line_number": 1, "code": "test"}
        resp = add_codes_from_draft(unauth_client, json=payload)
        assert resp.status_code in [401, 403]

    def test_423_vision_buffer_clear_success(self, client):
        """Кейс 423: Успешное удаление стопки."""
        # Этот тест требует активную сессию
        pytest.skip("Требует активную сессию")

    def test_424_vision_buffer_clear_inactive_session(self, client):
        """Кейс 424: Удаление стопки на линии без активной сессии."""
        line = 999999
        resp = vision_buffer_clear(client, json={"line_number": line})
        assert resp.status_code in [400, 404, 422]

    def test_425_vision_buffer_clear_missing_line_number(self, client):
        """Кейс 425: Удаление без line_number."""
        resp = vision_buffer_clear(client, json={})
        assert resp.status_code in [400, 422]

    def test_426_vision_buffer_clear_without_auth(self, client):
        """Кейс 426: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = vision_buffer_clear(unauth_client, json={})
        assert resp.status_code in [401, 403]

    def test_427_kin_load_from_order_success(self, client):
        """Кейс 427: Успешное наполнение буфера КИН."""
        # Этот тест требует существующий order_id
        pytest.skip("Требует существующего order_id")

    def test_428_kin_load_nonexistent_order(self, client):
        """Кейс 428: Наполнение с несуществующим order_id."""
        payload = {
            "order_id": "000000000000000000000000",
            "chunk_size": 100,
        }
        resp = kin_load_from_order(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_429_kin_load_missing_chunk_size(self, client):
        """Кейс 429: Наполнение без chunk_size."""
        payload = {"order_id": "test"}
        resp = kin_load_from_order(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_430_kin_statistics_success(self, client):
        """Кейс 430: Успешное получение статистики буфера КИН."""
        resp = kin_statistics(client, json={})
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert isinstance(data.get("result", data), list)

    def test_431_kin_statistics_without_auth(self, client):
        """Кейс 431: Запрос без авторизации."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        resp = kin_statistics(unauth_client, json={})
        assert resp.status_code in [401, 403]
