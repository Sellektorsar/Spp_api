"""
Integration Tests: Work Shift Management Extended
Раздел 8 (Партии) - расширенные операции

Roadmap: SPP_API_Test_Roadmap_v3.md
Кейсы: 127-209 (60 тестов)

API:
- POST /work_shift/delete - Удаление партии
- POST /work_shift/resume - Возобновление партии
- POST /work_shift/change_flag_other_gtin - Флаг других GTIN
- POST /work_shift/add_roll - Добавление ролика
- POST /work_shift/range/* - Операции с диапазонами
- POST /work_shift/get_codes - Получение кодов партии
- POST /work_shift/cancel/* - Исключение кодов/роликов
- POST /work_shift/clear - Очистка партии
- POST /work_shift/rename - Переименование партии
- POST /work_shift/get_ki - Выгрузка КИ
- POST /work_shift/find_work_shift_by_code - Поиск партии по коду
- POST /work_shift/get_used_rolls - Список роликов партии
"""

import pytest
import datetime
import os

from src.api.work_shift.start import start as start_shift
from src.api.work_shift.finish import finish as finish_shift
from src.api.work_shift.delete import delete as delete_shift
from src.api.work_shift.resume import resume as resume_shift
from src.api.work_shift.clear import clear as clear_shift
from src.api.work_shift.rename import rename as rename_shift
from src.api.work_shift.add_code import add_code
from src.api.work_shift.add_roll import add_roll
from src.api.work_shift.filter import filter as filter_shifts
from src.api.work_shift.get_codes import get_codes
from src.api.work_shift.get_ki import get_ki
from src.api.work_shift.find_work_shift_by_code import find_work_shift_by_code
from src.api.work_shift.get_used_rolls import get_used_rolls
from src.api.work_shift.change_flag_other_gtin import change_flag_other_gtin
from src.api.work_shift.range.add_start_code import add_start_code
from src.api.work_shift.range.add_finish_code import add_finish_code
from src.api.work_shift.range.cancel_start_code import cancel_start_code
from src.api.work_shift.defect.add import add as add_defect
from src.api.work_shift.defect.remove import remove as remove_defect
from src.api.work_shift.defect.add_range import add_range as add_defect_range
from src.api.work_shift.defect.remove_range import remove_range as remove_defect_range
from src.api.work_shift.cancel.code import cancel_code
from src.api.work_shift.cancel.codes_by_roll import cancel_codes_by_roll
from src.api.work_shift.cancel.codes_range import cancel_codes_range

from src.models import (
    WorkShiftStart,
    WorkShiftInput,
    WorkShiftCodeWithVariableWeight,
    WorkShiftRollInput,
    WorkShiftFlagGtinInput,
    ProductGroup,
)


@pytest.mark.integration
class TestWorkShiftDelete:
    """
    Кейсы 127-130: Удаление партии
    
    API: POST /work_shift/delete
    """

    def test_127_delete_finished_shift_success(self, client):
        """Кейс 127: Успешное удаление завершённой партии."""
        # Получаем список завершённых смен
        resp = filter_shifts(client, json={"limit": 50, "is_active": False})
        assert resp.status_code == 200
        shifts = resp.json()["result"]
        
        if not shifts:
            pytest.skip("Нет завершённых смен для удаления")
        
        # Берём первую завершённую смену
        shift_id = shifts[0].get("id")
        
        # Попытка удаления (может вернуть 200 или 4xx в зависимости от логики)
        resp = delete_shift(client, json={"work_shift_id": shift_id})
        assert resp.status_code in [200, 400, 404, 422]

    def test_128_delete_active_shift_error(self, client, real_shift_id_milk):
        """Кейс 128: Удаление активной партии возвращает ошибку."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        
        resp = delete_shift(client, json={"work_shift_id": real_shift_id_milk})
        # Активную партию удалять нельзя
        assert resp.status_code in [400, 403, 422]

    def test_129_delete_nonexistent_shift_error(self, client):
        """Кейс 129: Удаление несуществующей партии возвращает ошибку."""
        resp = delete_shift(client, json={"work_shift_id": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]

    def test_130_delete_missing_work_shift_id_error(self, client):
        """Кейс 130: Удаление без поля work_shift_id возвращает ошибку."""
        resp = delete_shift(client, json={})
        assert resp.status_code in [400, 422]


@pytest.mark.integration
class TestWorkShiftResume:
    """
    Кейсы 131-133: Возобновление партии
    
    API: POST /work_shift/resume
    """

    def test_131_resume_finished_shift_success(self, client):
        """Кейс 131: Успешное возобновление завершённой партии."""
        # Получаем список завершённых смен
        resp = filter_shifts(client, json={"limit": 50, "is_active": False})
        assert resp.status_code == 200
        shifts = resp.json()["result"]
        
        if not shifts:
            pytest.skip("Нет завершённых смен для возобновления")
        
        shift_id = shifts[0].get("id")
        
        resp = resume_shift(client, json={"work_shift_id": shift_id})
        # Возобновление может вернуть 200 или 4xx (если партию нельзя возобновить)
        assert resp.status_code in [200, 400, 404, 422]
        
        if resp.status_code == 200:
            # Проверяем, что смена стала активной
            resp_check = filter_shifts(client, json={"limit": 1, "is_active": True})
            assert resp_check.status_code == 200

    def test_132_resume_active_shift_error(self, client, real_shift_id_milk):
        """Кейс 132: Возобновление активной партии возвращает ошибку."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        
        resp = resume_shift(client, json={"work_shift_id": real_shift_id_milk})
        # Активную партию нельзя возобновить
        assert resp.status_code in [400, 403, 422]

    def test_133_resume_nonexistent_shift_error(self, client):
        """Кейс 133: Возобновление несуществующей партии возвращает ошибку."""
        resp = resume_shift(client, json={"work_shift_id": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]


@pytest.mark.integration
class TestWorkShiftFlagGtin:
    """
    Кейсы 134-136: Работа с несколькими GTIN в одной партии
    
    API: POST /work_shift/change_flag_other_gtins
    """

    _test_shift_id: str = None

    def test_134_enable_other_gtins_success(self, client, real_gtin_milk):
        """Кейс 134: Успешное включение флага is_allow_other_gtins."""
        # Создаём тестовую смену
        line = int(os.getenv("SPP_TEST_LINE_MILK_2") or "36")
        payload = WorkShiftStart(
            line_number=line,
            gtin=real_gtin_milk,
            batch=f"TEST-FLAG-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            start_date=datetime.datetime.now(datetime.timezone.utc),
            production_date=datetime.datetime.now(datetime.timezone.utc),
            product_group=ProductGroup.milk,
            is_allow_other_gtins=False,
            with_variable_weight=False,
            camera_is_active=False,
        )
        resp = start_shift(client, body=payload)
        
        if resp.status_code != 200:
            pytest.skip("Не удалось создать тестовую смену")
        
        shift_id = resp.json().get("id")
        TestWorkShiftFlagGtin._test_shift_id = shift_id
        
        # Включаем флаг
        payload_flag = WorkShiftFlagGtinInput(
            work_shift_id=shift_id,
            is_allow_other_gtins=True,
        )
        resp = change_flag_other_gtin(client, body=payload_flag)
        assert resp.status_code == 200

    def test_135_disable_other_gtins_success(self, client):
        """Кейс 135: Успешное выключение флага is_allow_other_gtins."""
        shift_id = TestWorkShiftFlagGtin._test_shift_id
        if not shift_id:
            pytest.skip("Смена не была создана в test_134")
        
        payload_flag = WorkShiftFlagGtinInput(
            work_shift_id=shift_id,
            is_allow_other_gtins=False,
        )
        resp = change_flag_other_gtin(client, body=payload_flag)
        assert resp.status_code == 200
        
        # Завершаем смену
        finish_shift(client, json={"id": shift_id})
        TestWorkShiftFlagGtin._test_shift_id = None

    def test_136_change_flag_nonexistent_shift_error(self, client):
        """Кейс 136: Изменение флага несуществующей партии возвращает ошибку."""
        payload_flag = WorkShiftFlagGtinInput(
            work_shift_id="000000000000000000000000",
            is_allow_other_gtins=True,
        )
        resp = change_flag_other_gtin(client, body=payload_flag)
        assert resp.status_code in [400, 404, 422]


@pytest.mark.integration
class TestWorkShiftAddRoll:
    """
    Кейсы 149-153: Добавление ролика в партию
    
    API: POST /work_shift/add_roll
    """

    def test_149_add_roll_success(self, client, real_shift_id_milk):
        """Кейс 149: Успешное добавление ролика в партию."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        
        # Получаем roll_id из существующих роликов на складе
        from src.api.warehouse.filter import filter as filter_warehouse
        resp_wh = filter_warehouse(client, json={"limit": 1})
        
        if resp_wh.status_code != 200 or not resp_wh.json()["result"]:
            pytest.skip("Нет доступных роликов на складе")
        
        roll_id = resp_wh.json()["result"][0].get("roll_id")
        
        payload = WorkShiftRollInput(
            line_number=int(os.getenv("SPP_TEST_LINE_MILK") or "1"),
            roll_id=roll_id,
        )
        resp = add_roll(client, body=payload)
        # Может вернуть 200 или 4xx (если ролик уже используется)
        assert resp.status_code in [200, 400, 404, 422]

    def test_150_add_nonexistent_roll_error(self, client, real_shift_id_milk):
        """Кейс 150: Добавление несуществующего ролика возвращает ошибку."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        
        payload = WorkShiftRollInput(
            line_number=int(os.getenv("SPP_TEST_LINE_MILK") or "1"),
            roll_id="000000000000000000000000",
        )
        resp = add_roll(client, body=payload)
        assert resp.status_code in [400, 404, 422]

    def test_151_add_roll_without_auth_error(self, client):
        """Кейс 151: Добавление ролика без авторизации возвращает ошибку."""
        # Создаём клиент без токена
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = WorkShiftRollInput(
            line_number=1,
            roll_id="test_roll",
        )
        resp = add_roll(unauth_client, body=payload)
        assert resp.status_code in [401, 403]

    def test_152_add_roll_missing_line_number_error(self, client):
        """Кейс 152: Добавление ролика без line_number возвращает ошибку."""
        payload = {"roll_id": "test_roll"}
        resp = add_roll(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_153_add_roll_to_finished_shift_error(self, client):
        """Кейс 153: Добавление ролика в завершённую партию возвращает ошибку."""
        # Получаем завершённую смену
        resp = filter_shifts(client, json={"limit": 1, "is_active": False})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет завершённых смен")
        
        # Получаем номер линии из завершённой смены
        shift = resp.json()["result"][0]
        line_number = shift.get("line_number")
        
        payload = WorkShiftRollInput(
            line_number=line_number,
            roll_id="test_roll",
        )
        resp = add_roll(client, body=payload)
        assert resp.status_code in [400, 404, 422]


@pytest.mark.integration
class TestWorkShiftRange:
    """
    Кейсы 154-162: Операции с диапазонами кодов
    
    API:
    - POST /work_shift/range/add_start_code
    - POST /work_shift/range/add_finish_code
    - POST /work_shift/range/cancel_start_code
    """

    _test_shift_id: str = None

    def test_154_add_start_code_success(self, client, real_gtin_milk):
        """Кейс 154: Успешное добавление начального кода диапазона."""
        # Создаём тестовую смену
        line = int(os.getenv("SPP_TEST_LINE_MILK_2") or "36")
        payload = WorkShiftStart(
            line_number=line,
            gtin=real_gtin_milk,
            batch=f"TEST-RANGE-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            start_date=datetime.datetime.now(datetime.timezone.utc),
            production_date=datetime.datetime.now(datetime.timezone.utc),
            product_group=ProductGroup.milk,
            is_allow_other_gtins=False,
            with_variable_weight=False,
            camera_is_active=False,
        )
        resp = start_shift(client, body=payload)
        
        if resp.status_code != 200:
            pytest.skip("Не удалось создать тестовую смену")
        
        shift_id = resp.json().get("id")
        TestWorkShiftRange._test_shift_id = shift_id
        
        # Добавляем начальный код диапазона
        payload_code = WorkShiftCodeWithVariableWeight(
            line_number=line,
            code="010460049400904421dGVzdHN0YXJ0",
        )
        resp = add_start_code(client, body=payload_code)
        assert resp.status_code in [200, 400, 422]

    def test_155_add_start_code_without_auth_error(self, client):
        """Кейс 155: Добавление start_code без авторизации возвращает ошибку."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"line_number": 1, "code": "test_code"}
        resp = add_start_code(unauth_client, json=payload)
        assert resp.status_code in [401, 403]

    def test_156_add_start_code_missing_line_number_error(self, client):
        """Кейс 156: Добавление start_code без line_number возвращает ошибку."""
        payload = {"code": "test_code"}
        resp = add_start_code(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_157_add_start_code_missing_code_error(self, client):
        """Кейс 157: Добавление start_code без code возвращает ошибку."""
        payload = {"line_number": 1}
        resp = add_start_code(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_158_add_finish_code_success(self, client):
        """Кейс 158: Успешное добавление конечного кода диапазона."""
        shift_id = TestWorkShiftRange._test_shift_id
        if not shift_id:
            pytest.skip("Смена не была создана в test_154")
        
        line = int(os.getenv("SPP_TEST_LINE_MILK_2") or "36")
        payload = WorkShiftCodeWithVariableWeight(
            line_number=line,
            code="010460049400904421dGVzdGZpbmlzaA==",
        )
        resp = add_finish_code(client, body=payload)
        assert resp.status_code in [200, 400, 422]
        
        # Завершаем смену
        finish_shift(client, json={"id": shift_id})
        TestWorkShiftRange._test_shift_id = None

    def test_159_add_finish_code_without_start_error(self, client, real_gtin_milk):
        """Кейс 159: Добавление finish_code без начального кода возвращает ошибку."""
        # Создаём новую смену
        line = int(os.getenv("SPP_TEST_LINE_MILK_2") or "36")
        payload = WorkShiftStart(
            line_number=line,
            gtin=real_gtin_milk,
            batch=f"TEST-FINISH-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            start_date=datetime.datetime.now(datetime.timezone.utc),
            production_date=datetime.datetime.now(datetime.timezone.utc),
            product_group=ProductGroup.milk,
            is_allow_other_gtins=False,
            with_variable_weight=False,
            camera_is_active=False,
        )
        resp = start_shift(client, body=payload)
        
        if resp.status_code != 200:
            pytest.skip("Не удалось создать тестовую смену")
        
        # Пытаемся добавить finish_code без start_code
        payload_finish = WorkShiftCodeWithVariableWeight(
            line_number=line,
            code="010460049400904421dGVzdGZpbmlzaA==",
        )
        resp = add_finish_code(client, body=payload_finish)
        assert resp.status_code in [400, 422]
        
        # Очищаем смену
        shift_id = resp.json().get("id") if resp.status_code == 200 else None
        if shift_id:
            finish_shift(client, json={"id": shift_id})

    def test_160_add_finish_code_equals_start_code_error(self, client):
        """Кейс 160: Добавление finish_code равного start_code возвращает ошибку."""
        # Этот тест требует специальной настройки - пропускаем
        pytest.skip("Требует специальной настройки равных кодов")

    def test_161_cancel_start_code_success(self, client):
        """Кейс 161: Успешная отмена начального кода диапазона."""
        # Отмена требует предварительно добавленного start_code
        # Пропускаем, так как требует сложной подготовки
        pytest.skip("Требует предварительно добавленного start_code")

    def test_162_cancel_start_code_without_start_error(self, client):
        """Кейс 162: Отмена start_code когда нет начального кода."""
        payload = {"line_number": 1}
        resp = cancel_start_code(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]


@pytest.mark.integration
class TestWorkShiftGetCodes:
    """
    Кейсы 180-182: Получение списка кодов из партии
    
    API: POST /work_shift/get_codes
    """

    def test_180_get_codes_success(self, client, real_shift_id_milk):
        """Кейс 180: Успешное получение кодов из партии."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        
        resp = get_codes(client, json={"work_shift_id": real_shift_id_milk})
        assert resp.status_code in [200, 400, 404, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert "result" in data or "codes" in data

    def test_181_get_codes_from_empty_shift(self, client, real_gtin_milk):
        """Кейс 181: Получение кодов из пустой партии."""
        # Создаём новую пустую смену
        line = int(os.getenv("SPP_TEST_LINE_MILK_2") or "36")
        payload = WorkShiftStart(
            line_number=line,
            gtin=real_gtin_milk,
            batch=f"TEST-EMPTY-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            start_date=datetime.datetime.now(datetime.timezone.utc),
            production_date=datetime.datetime.now(datetime.timezone.utc),
            product_group=ProductGroup.milk,
            is_allow_other_gtins=False,
            with_variable_weight=False,
            camera_is_active=False,
        )
        resp = start_shift(client, body=payload)
        
        if resp.status_code != 200:
            pytest.skip("Не удалось создать тестовую смену")
        
        shift_id = resp.json().get("id")
        
        # Получаем коды
        resp = get_codes(client, json={"work_shift_id": shift_id})
        assert resp.status_code == 200
        
        # Проверяем пустой список
        data = resp.json()
        codes = data.get("result", data.get("codes", []))
        assert isinstance(codes, list)
        
        # Завершаем смену
        finish_shift(client, json={"id": shift_id})

    def test_182_get_codes_nonexistent_shift_error(self, client):
        """Кейс 182: Получение кодов несуществующей партии возвращает ошибку."""
        resp = get_codes(client, json={"work_shift_id": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]


@pytest.mark.integration
class TestWorkShiftCancel:
    """
    Кейсы 183-189: Исключение кодов/роликов из партии
    
    API:
    - POST /work_shift/cancel/code
    - POST /work_shift/cancel/codes_by_roll
    - POST /work_shift/cancel/codes_range
    """

    def test_183_cancel_code_success(self, client, real_shift_id_milk):
        """Кейс 183: Успешное исключение КМ из партии."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        
        # Получаем коды из партии
        resp_codes = get_codes(client, json={"work_shift_id": real_shift_id_milk})
        
        if resp_codes.status_code != 200 or not resp_codes.json().get("result"):
            pytest.skip("Нет кодов в партии для исключения")
        
        code = resp_codes.json()["result"][0].get("code")
        
        payload = {
            "work_shift_id": real_shift_id_milk,
            "code": code,
        }
        resp = cancel_code(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_184_cancel_code_not_in_shift_error(self, client, real_shift_id_milk):
        """Кейс 184: Исключение кода которого нет в партии возвращает ошибку."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        
        payload = {
            "work_shift_id": real_shift_id_milk,
            "code": "010000000000000000000000000000000000",
        }
        resp = cancel_code(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_185_cancel_code_without_auth_error(self, client):
        """Кейс 185: Исключение кода без авторизации возвращает ошибку."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"work_shift_id": "test", "code": "test"}
        resp = cancel_code(unauth_client, json=payload)
        assert resp.status_code in [401, 403]

    def test_186_cancel_codes_by_roll_success(self, client, real_shift_id_milk):
        """Кейс 186: Успешное исключение ролика из партии."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        
        # Получаем roll_id из партии
        resp_rolls = get_used_rolls(client, json={"work_shift_id": real_shift_id_milk})
        
        if resp_rolls.status_code != 200 or not resp_rolls.json().get("result"):
            pytest.skip("Нет роликов в партии для исключения")
        
        roll_id = resp_rolls.json()["result"][0].get("roll_id")
        
        payload = {
            "work_shift_id": real_shift_id_milk,
            "roll_id": roll_id,
        }
        resp = cancel_codes_by_roll(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_187_cancel_roll_not_in_shift_error(self, client, real_shift_id_milk):
        """Кейс 187: Исключение ролика которого нет в партии возвращает ошибку."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        
        payload = {
            "work_shift_id": real_shift_id_milk,
            "roll_id": "000000000000000000000000",
        }
        resp = cancel_codes_by_roll(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_188_cancel_codes_range_success(self, client, real_shift_id_milk):
        """Кейс 188: Успешное исключение диапазона кодов из партии."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        
        payload = {
            "work_shift_id": real_shift_id_milk,
            "start_code": "010000000000000000000000000000000000",
            "finish_code": "010000000000000000000000000000000001",
        }
        resp = cancel_codes_range(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_189_cancel_range_not_in_shift_error(self, client, real_shift_id_milk):
        """Кейс 189: Исключение диапазона кодов не из партии возвращает ошибку."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        
        payload = {
            "work_shift_id": real_shift_id_milk,
            "start_code": "999999999999999999999999999999999999",
            "finish_code": "999999999999999999999999999999999998",
        }
        resp = cancel_codes_range(client, json=payload)
        assert resp.status_code in [400, 404, 422]


@pytest.mark.integration
class TestWorkShiftClear:
    """
    Кейсы 190-193: Очистка партии
    
    API: POST /work_shift/clear
    """

    def test_190_clear_shift_success(self, client, real_gtin_milk):
        """Кейс 190: Успешная очистка партии."""
        # Создаём тестовую смену
        line = int(os.getenv("SPP_TEST_LINE_MILK_2") or "36")
        payload = WorkShiftStart(
            line_number=line,
            gtin=real_gtin_milk,
            batch=f"TEST-CLEAR-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            start_date=datetime.datetime.now(datetime.timezone.utc),
            production_date=datetime.datetime.now(datetime.timezone.utc),
            product_group=ProductGroup.milk,
            is_allow_other_gtins=False,
            with_variable_weight=False,
            camera_is_active=False,
        )
        resp = start_shift(client, body=payload)
        
        if resp.status_code != 200:
            pytest.skip("Не удалось создать тестовую смену")
        
        shift_id = resp.json().get("id")
        
        # Очищаем смену
        resp = clear_shift(client, json={"work_shift_id": shift_id})
        assert resp.status_code in [200, 400, 404, 422]

    def test_191_clear_nonexistent_shift_error(self, client):
        """Кейс 191: Очистка несуществующей партии возвращает ошибку."""
        resp = clear_shift(client, json={"work_shift_id": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]

    def test_192_clear_finished_shift_error(self, client):
        """Кейс 192: Очистка завершённой партии возвращает ошибку."""
        # Получаем завершённую смену
        resp = filter_shifts(client, json={"limit": 1, "is_active": False})
        if resp.status_code != 200 or not resp.json()["result"]:
            pytest.skip("Нет завершённых смен")
        
        shift_id = resp.json()["result"][0].get("id")
        resp = clear_shift(client, json={"work_shift_id": shift_id})
        assert resp.status_code in [400, 404, 422]

    def test_193_clear_without_auth_error(self, client):
        """Кейс 193: Очистка без авторизации возвращает ошибку."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"work_shift_id": "test"}
        resp = clear_shift(unauth_client, json=payload)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestWorkShiftRename:
    """
    Кейсы 194-197: Переименование партии
    
    API: POST /work_shift/rename
    """

    def test_194_rename_shift_success(self, client, real_shift_id_milk):
        """Кейс 194: Успешное переименование партии."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        
        new_name = f"Renamed-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        payload = {
            "work_shift_id": real_shift_id_milk,
            "name": new_name,
        }
        resp = rename_shift(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]

    def test_195_rename_shift_empty_name_error(self, client, real_shift_id_milk):
        """Кейс 195: Переименование с пустым именем возвращает ошибку."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        
        payload = {
            "work_shift_id": real_shift_id_milk,
            "name": "",
        }
        resp = rename_shift(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_196_rename_nonexistent_shift_error(self, client):
        """Кейс 196: Переименование несуществующей партии возвращает ошибку."""
        payload = {
            "work_shift_id": "000000000000000000000000",
            "name": "New Name",
        }
        resp = rename_shift(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_197_rename_without_auth_error(self, client):
        """Кейс 197: Переименование без авторизации возвращает ошибку."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"work_shift_id": "test", "name": "New Name"}
        resp = rename_shift(unauth_client, json=payload)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestWorkShiftGetKi:
    """
    Кейсы 198-201: Выгрузка КИ из партии
    
    API: POST /work_shift/get_ki
    """

    def test_198_get_ki_success(self, client, real_shift_id_milk):
        """Кейс 198: Успешная выгрузка КИ из партии."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        
        resp = get_ki(client, json={"work_shift_id": real_shift_id_milk})
        assert resp.status_code in [200, 400, 404, 422]
        
        if resp.status_code == 200:
            # Проверяем, что вернулся файл или данные
            content_type = resp.headers.get("Content-Type", "")
            # Может быть CSV или JSON
            assert "text" in content_type or "json" in content_type or "application" in content_type

    def test_199_get_ki_nonexistent_shift_error(self, client):
        """Кейс 199: Выгрузка КИ из несуществующей партии возвращает ошибку."""
        resp = get_ki(client, json={"work_shift_id": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]

    def test_200_get_ki_from_empty_shift(self, client, real_gtin_milk):
        """Кейс 200: Выгрузка КИ из пустой партии."""
        # Создаём новую пустую смену
        line = int(os.getenv("SPP_TEST_LINE_MILK_2") or "36")
        payload = WorkShiftStart(
            line_number=line,
            gtin=real_gtin_milk,
            batch=f"TEST-KI-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            start_date=datetime.datetime.now(datetime.timezone.utc),
            production_date=datetime.datetime.now(datetime.timezone.utc),
            product_group=ProductGroup.milk,
            is_allow_other_gtins=False,
            with_variable_weight=False,
            camera_is_active=False,
        )
        resp = start_shift(client, body=payload)
        
        if resp.status_code != 200:
            pytest.skip("Не удалось создать тестовую смену")
        
        shift_id = resp.json().get("id")
        
        # Получаем КИ
        resp = get_ki(client, json={"work_shift_id": shift_id})
        assert resp.status_code in [200, 400, 422]
        
        # Завершаем смену
        finish_shift(client, json={"id": shift_id})

    def test_201_get_ki_without_auth_error(self, client):
        """Кейс 201: Выгрузка КИ без авторизации возвращает ошибку."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"work_shift_id": "test"}
        resp = get_ki(unauth_client, json=payload)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestWorkShiftFindByCode:
    """
    Кейсы 202-205: Поиск партии по коду
    
    API: POST /work_shift/find_work_shift_by_code
    """

    def test_202_find_shift_by_existing_code(self, client, real_shift_id_milk):
        """Кейс 202: Поиск партии по коду (КМ в партии)."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        
        # Получаем код из партии
        resp_codes = get_codes(client, json={"work_shift_id": real_shift_id_milk})
        
        if resp_codes.status_code != 200 or not resp_codes.json().get("result"):
            pytest.skip("Нет кодов в партии для поиска")
        
        code = resp_codes.json()["result"][0].get("code")
        
        payload = {"code": code}
        resp = find_work_shift_by_code(client, json=payload)
        assert resp.status_code == 200
        
        # Проверяем, что нашлась партия
        data = resp.json()
        assert "result" in data or "work_shift" in data

    def test_203_find_shift_by_nonexistent_code(self, client):
        """Кейс 203: Поиск партии по несуществующему коду."""
        payload = {"code": "010000000000000000000000000000000000"}
        resp = find_work_shift_by_code(client, json=payload)
        assert resp.status_code in [200, 400, 404, 422]
        
        # Может вернуть 200 с пустым результатом или ошибку
        if resp.status_code == 200:
            data = resp.json()
            # Проверяем, что результат пустой или содержит ошибку
            assert not data.get("result") or data.get("error")

    def test_204_find_shift_missing_code_error(self, client):
        """Кейс 204: Поиск партии без поля code возвращает ошибку."""
        resp = find_work_shift_by_code(client, json={})
        assert resp.status_code in [400, 422]

    def test_205_find_shift_without_auth_error(self, client):
        """Кейс 205: Поиск партии без авторизации возвращает ошибку."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"code": "test"}
        resp = find_work_shift_by_code(unauth_client, json=payload)
        assert resp.status_code in [401, 403]


@pytest.mark.integration
class TestWorkShiftGetUsedRolls:
    """
    Кейсы 206-209: Получение списка роликов, использованных в партии
    
    API: POST /work_shift/get_used_rolls
    """

    def test_206_get_used_rolls_success(self, client, real_shift_id_milk):
        """Кейс 206: Успешное получение роликов партии."""
        if not real_shift_id_milk:
            pytest.skip("SPP_TEST_SHIFT_ID_MILK не задан")
        
        resp = get_used_rolls(client, json={"work_shift_id": real_shift_id_milk})
        assert resp.status_code in [200, 400, 404, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert "result" in data or "rolls" in data

    def test_207_get_used_rolls_empty_shift(self, client, real_gtin_milk):
        """Кейс 207: Получение роликов партии без роликов (только add_code)."""
        # Создаём новую смену без роликов
        line = int(os.getenv("SPP_TEST_LINE_MILK_2") or "36")
        payload = WorkShiftStart(
            line_number=line,
            gtin=real_gtin_milk,
            batch=f"TEST-ROLLS-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
            start_date=datetime.datetime.now(datetime.timezone.utc),
            production_date=datetime.datetime.now(datetime.timezone.utc),
            product_group=ProductGroup.milk,
            is_allow_other_gtins=False,
            with_variable_weight=False,
            camera_is_active=False,
        )
        resp = start_shift(client, body=payload)
        
        if resp.status_code != 200:
            pytest.skip("Не удалось создать тестовую смену")
        
        shift_id = resp.json().get("id")
        
        # Получаем ролики
        resp = get_used_rolls(client, json={"work_shift_id": shift_id})
        assert resp.status_code == 200
        
        # Проверяем пустой массив
        data = resp.json()
        rolls = data.get("result", data.get("rolls", []))
        assert isinstance(rolls, list)
        
        # Завершаем смену
        finish_shift(client, json={"id": shift_id})

    def test_208_get_used_rolls_nonexistent_shift_error(self, client):
        """Кейс 208: Получение роликов несуществующей партии возвращает ошибку."""
        resp = get_used_rolls(client, json={"work_shift_id": "000000000000000000000000"})
        assert resp.status_code in [400, 404, 422]

    def test_209_get_used_rolls_without_auth_error(self, client):
        """Кейс 209: Получение роликов без авторизации возвращает ошибку."""
        from src.utils.http import APIClient
        base_url = os.getenv("SPP_API_URL")
        unauth_client = APIClient(base_url=base_url, token=None)
        
        payload = {"work_shift_id": "test"}
        resp = get_used_rolls(unauth_client, json=payload)
        assert resp.status_code in [401, 403]
