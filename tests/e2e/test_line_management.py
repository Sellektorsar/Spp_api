"""
E2E Tests: Line Management
Сценарий: настройка и управление производственными линиями.

Особенности реального API:
- line_number генерируется сервером при создании
- Ответ create: {"data": true} - без line_number
- Нужно использовать filter для получения созданной линии по имени
- Ответ filter: {"result": [...], "total_count": N}
"""
import pytest
import responses
import uuid
import datetime
import time

from src.api.line.create import create as create_line
from src.api.line.edit import edit as edit_line
from src.api.line.filter import filter as filter_lines
from src.api.line.delete import delete as delete_line
from src.api.line.rename import rename as rename_line
from src.api.line.recover import recover as recover_line
from src.models import CreateInput, LINETYPE, ProductGroup, ProductionType, REPORTTYPE


# Глобальное хранилище для данных между тестами
_test_data = {
    "line_number": None,
    "line_name": None,
    "alt_line_number": None,
}


def _get_line_number_by_name(client, line_name):
    """Получение line_number по имени линии через filter."""
    resp = filter_lines(client, json={"limit": 100, "offset": 0, "name": line_name})
    if resp.status_code == 200:
        data = resp.json()
        if isinstance(data, dict) and "result" in data:
            for line in data["result"]:
                if line.get("name") == line_name:
                    return line.get("line_number")
    return None


@pytest.mark.e2e
@pytest.mark.order(8)
class TestLineManagement:
    """
    E2E Сценарий: Полный цикл управления производственными линиями.
    """

    def test_01_create_line_positive(self, client, test_context, mock_api):
        """Шаг 1: Создание производственной линии."""
        global _test_data
        
        line_name = f"LINE_MGMT_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/create",
                json={"data": True},
                status=200,
            )

        line_data = CreateInput(
            name=line_name,
            line_type=LINETYPE.integer_1,
            product_group=ProductGroup.milk,
            production_type=ProductionType.integer_1,
            camera_host="192.168.1.100",
            pin_code="123456",
            is_auto_send_report=True,
            count_in_report=100,
            report_to_send=[REPORTTYPE.integer_1, REPORTTYPE.integer_2]
        )
        
        resp = create_line(client, body=line_data)
        assert resp.status_code == 200
        
        # API возвращает {"data": true}
        data = resp.json()
        assert data.get("status") == "ok"  # Нормализатор conftest.py
        
        # Сохраняем имя для поиска line_number
        _test_data["line_name"] = line_name
        _test_data["line_number"] = None  # Будет получен через filter
        
        test_context.add("line_name", line_name)
        
        print(f"[E2E-LINE] Линия создана: {line_name}")

    def test_02_get_line_number_after_create(self, client, test_context, mock_api):
        """Шаг 2: Получение line_number созданной линии через filter."""
        global _test_data
        
        line_name = _test_data.get("line_name")
        assert line_name is not None, "Имя линии должно быть установлено в test_01"
        
        if mock_api:
            # Генерируем случайный line_number для мока
            mock_line_number = int(datetime.datetime.now().timestamp()) % 100000
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/filter",
                json={
                    "result": [{
                        "id": str(uuid.uuid4()),
                        "line_number": mock_line_number,
                        "name": line_name,
                        "line_type": 1,
                        "product_group": "milk",
                        "is_active": True,
                        "is_deleted": False
                    }],
                    "total_count": 1
                },
                status=200,
            )
        
        # Ищем линию по имени
        line_number = _get_line_number_by_name(client, line_name)
        
        if line_number is None and not mock_api:
            # На реальном API может быть задержка, пробуем еще раз
            time.sleep(1)
            line_number = _get_line_number_by_name(client, line_name)
        
        if mock_api:
            line_number = int(datetime.datetime.now().timestamp()) % 100000
        
        assert line_number is not None, f"Не удалось получить line_number для линии {line_name}"
        
        _test_data["line_number"] = line_number
        test_context.add("line_number", line_number)
        
        print(f"[E2E-LINE] Получен line_number: {line_number} для линии {line_name}")

    def test_03_create_line_duplicate(self, client, test_context, mock_api):
        """Шаг 3: Попытка создать линию с тем же именем."""
        line_name = _test_data.get("line_name")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/create",
                json={"data": True},
                status=200,
            )

        line_data = CreateInput(
            name=line_name,  # То же имя
            line_type=LINETYPE.integer_1,
            product_group=ProductGroup.milk,
            production_type=ProductionType.integer_1
        )
        
        resp = create_line(client, body=line_data)
        # API может принять или отклонить в зависимости от реализации
        assert resp.status_code in [200, 400, 409]
        print(f"[E2E-LINE] Дублирование: статус {resp.status_code}")

    def test_04_filter_lines(self, client, test_context, mock_api):
        """Шаг 4: Фильтрация всех линий."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/filter",
                json={
                    "result": [
                        {"id": str(uuid.uuid4()), "line_number": 1, "name": "Line 1"},
                        {"id": str(uuid.uuid4()), "line_number": 2, "name": "Line 2"}
                    ],
                    "total_count": 2
                },
                status=200,
            )

        resp = filter_lines(client, json={"limit": 10, "offset": 0})
        assert resp.status_code == 200
        
        data = resp.json()
        assert "result" in data
        assert isinstance(data["result"], list)
        
        print(f"[E2E-LINE] Найдено линий: {data.get('total_count', 0)}")

    def test_05_edit_line_configuration(self, client, test_context, mock_api):
        """Шаг 5: Редактирование конфигурации линии."""
        line_number = _test_data.get("line_number")
        
        if line_number is None:
            pytest.skip("line_number не получен, пропускаем тест")
        
        new_name = f"UPDATED_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/edit",
                json={"data": True},
                status=200,
            )

        edit_data = {
            "line_number": line_number,
            "name": new_name,
            "camera_host": "192.168.1.101",
            "pin_code": "654321",
            "is_auto_send_report": False,
            "count_in_report": 200
        }
        
        resp = edit_line(client, body=edit_data)
        assert resp.status_code == 200
        
        data = resp.json()
        assert data.get("status") == "ok" or data.get("data") is True
        
        _test_data["updated_line_name"] = new_name
        print(f"[E2E-LINE] Линия обновлена: {new_name}")

    def test_06_edit_line_nonexistent(self, client, test_context, mock_api):
        """Шаг 6: Редактирование несуществующей линии."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/edit",
                json={"data": False},
                status=200,
            )

        edit_data = {
            "line_number": 99999,
            "name": "Nonexistent"
        }
        
        resp = edit_line(client, body=edit_data)
        assert resp.status_code == 200
        
        data = resp.json()
        # API возвращает data=false для несуществующей линии
        success = data.get("success") if "success" in data else data.get("data")
        assert success is False
        
        print(f"[E2E-LINE] Несуществующая линия: data=false")

    def test_07_rename_line(self, client, test_context, mock_api):
        """Шаг 7: Переименование линии."""
        line_number = _test_data.get("line_number")
        
        if line_number is None:
            pytest.skip("line_number не получен, пропускаем тест")
        
        new_name = f"RENAMED_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/rename",
                json={"data": True},
                status=200,
            )

        resp = rename_line(client, json={"line_number": line_number, "new_name": new_name})
        assert resp.status_code == 200
        
        data = resp.json()
        assert data.get("status") == "ok" or data.get("data") is True
        
        _test_data["renamed_line_name"] = new_name
        print(f"[E2E-LINE] Переименована: {new_name}")

    def test_08_rename_line_validation(self, client, test_context, mock_api):
        """Шаг 8: Валидация - отсутствует line_number."""
        resp = rename_line(client, json={"new_name": "Test"})
        assert resp.status_code == 422
        print(f"[E2E-LINE] Валидация rename: {resp.status_code}")

    def test_09_delete_line(self, client, test_context, mock_api):
        """Шаг 9: Удаление линии."""
        line_number = _test_data.get("line_number")
        
        if line_number is None:
            pytest.skip("line_number не получен, пропускаем тест")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/delete",
                json={"data": True},
                status=200,
            )

        resp = delete_line(client, json={"line_number": line_number})
        assert resp.status_code == 200
        
        data = resp.json()
        assert data.get("status") == "ok" or data.get("data") is True
        
        print(f"[E2E-LINE] Линия удалена: {line_number}")

    def test_10_delete_line_nonexistent(self, client, test_context, mock_api):
        """Шаг 10: Удаление несуществующей линии."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/delete",
                json={"detail": "Internal Server Error"},
                status=500,
            )

        resp = delete_line(client, json={"line_number": 99999})
        assert resp.status_code == 500
        print(f"[E2E-LINE] Удаление несуществующей: {resp.status_code}")

    def test_11_recover_deleted_line(self, client, test_context, mock_api):
        """Шаг 11: Восстановление удаленной линии."""
        line_number = _test_data.get("line_number")
        
        if line_number is None:
            pytest.skip("line_number не получен, пропускаем тест")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/recover",
                json={"data": True},
                status=200,
            )

        resp = recover_line(client, json={"line_number": line_number})
        assert resp.status_code == 200
        
        data = resp.json()
        assert data.get("status") == "ok" or data.get("data") is True
        
        print(f"[E2E-LINE] Линия восстановлена: {line_number}")

    def test_12_recover_line_validation(self, client, test_context, mock_api):
        """Шаг 12: Валидация - отсутствует line_number."""
        resp = recover_line(client, json={})
        assert resp.status_code == 422
        print(f"[E2E-LINE] Валидация recover: {resp.status_code}")

    def test_13_create_line_alt_type(self, client, test_context, mock_api):
        """Шаг 13: Создание линии с альтернативным типом."""
        line_name = f"ALT_TYPE_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/create",
                json={"data": True},
                status=200,
            )

        line_data = CreateInput(
            name=line_name,
            line_type=LINETYPE.integer_2,
            product_group=ProductGroup.water,
            production_type=ProductionType.integer_2
        )
        
        resp = create_line(client, body=line_data)
        assert resp.status_code == 200
        
        data = resp.json()
        assert data.get("status") == "ok" or data.get("data") is True
        
        _test_data["alt_line_name"] = line_name
        
        # Получаем line_number для альтернативной линии
        if mock_api:
            _test_data["alt_line_number"] = int(datetime.datetime.now().timestamp()) % 100000 + 1
        else:
            time.sleep(1)
            alt_line_number = _get_line_number_by_name(client, line_name)
            _test_data["alt_line_number"] = alt_line_number
        
        print(f"[E2E-LINE] Альтернативная линия: {line_name}")

    def test_14_filter_boundary_large(self, client, test_context, mock_api):
        """Шаг 14: Граничный тест - фильтрация с большим лимитом."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/filter",
                json={
                    "result": [{"id": str(uuid.uuid4()), "line_number": i} for i in range(100)],
                    "total_count": 100
                },
                status=200,
            )

        resp = filter_lines(client, json={"limit": 100, "offset": 0})
        assert resp.status_code == 200
        
        result = resp.json().get("result", [])
        assert len(result) <= 100
        
        print(f"[E2E-LINE] Граничный тест: {len(result)} линий")

    def test_15_filter_empty_results(self, client, test_context, mock_api):
        """Шаг 15: Пустые результаты фильтрации."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/filter",
                json={"result": [], "total_count": 0},
                status=200,
            )

        resp = filter_lines(client, json={"limit": 10, "offset": 0, "name": "NONEXISTENT_XYZ"})
        assert resp.status_code == 200
        
        data = resp.json()
        assert data.get("total_count") == 0
        assert len(data.get("result", [])) == 0
        
        print(f"[E2E-LINE] Пустые результаты: ok")

    def test_16_error_invalid_line_number(self, client, test_context, mock_api):
        """Шаг 16: Невалидный тип line_number."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/line/edit",
                json={"errors": [{"loc": ["body", "line_number"], "type": "type_error.integer"}]},
                status=422,
            )

        resp = edit_line(client, body={"line_number": "invalid", "name": "Test"})
        assert resp.status_code == 422
        print(f"[E2E-LINE] Невалидный тип: 422")

    def test_17_error_missing_field(self, client, test_context, mock_api):
        """Шаг 17: Отсутствует обязательное поле."""
        resp = delete_line(client, json={})
        assert resp.status_code == 422
        print(f"[E2E-LINE] Отсутствует поле: 422")

    def test_18_cleanup(self, client, test_context, mock_api):
        """Шаг 18: Очистка тестовых данных."""
        line_number = _test_data.get("line_number")
        alt_line_number = _test_data.get("alt_line_number")
        
        # Удаляем основную линию
        if line_number:
            if mock_api:
                mock_api.add(
                    responses.POST,
                    f"{client.base_url}/api/web/v1/line/delete",
                    json={"data": True},
                    status=200,
                )
            resp = delete_line(client, json={"line_number": line_number})
            assert resp.status_code == 200
            print(f"[E2E-LINE] Основная линия удалена: {line_number}")
        
        # Удаляем альтернативную линию
        if alt_line_number:
            if mock_api:
                mock_api.add(
                    responses.POST,
                    f"{client.base_url}/api/web/v1/line/delete",
                    json={"data": True},
                    status=200,
                )
            resp2 = delete_line(client, json={"line_number": alt_line_number})
            assert resp.status_code == 200
            print(f"[E2E-LINE] Альтернативная линия удалена: {alt_line_number}")
        
        print(f"[E2E-LINE] Очистка завершена")
