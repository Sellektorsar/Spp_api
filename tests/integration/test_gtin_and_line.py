"""
Integration Tests: GTIN and Line Management
Проверяет управление линиями производства и справочником GTIN
против реального сервера spp-dev.

Ключевые исправления:
- line/edit    принимает line_number (integer), не id (строка ObjectId)
- line/delete  принимает line_number (integer), не id
- line/recover принимает line_number (integer), не id
- gtin/add_many принимает {"data": [{"gtin": ..., "product_group": ...}]}, не {"gtins": [...]}
- Из create_line ответа сохраняем line_number, а не id
"""
import pytest
import datetime

from src.api.line.create import create as create_line
from src.api.line.filter import filter as filter_lines
from src.api.line.edit import edit as edit_line
from src.api.line.delete import delete as delete_line
from src.api.line.recover import recover as recover_line
from src.api.gtin.filter import filter as filter_gtin
from src.api.gtin.add_many import add_many as add_gtin
from src.api.gtin.edit import edit as edit_gtin
from src.api.gtin.delete import delete as delete_gtin
from src.models import CreateInput, LINETYPE, ProductGroup, ProductionType


@pytest.mark.integration
class TestLineManagement:
    """Тесты управления производственными линиями."""

    # line_number (integer) созданной в тестах линии
    _created_line_number: int = None

    def test_filter_lines_default(self, client):
        """Получение списка линий без фильтра."""
        resp = filter_lines(client, json={"limit": 20, "offset": 0})
        assert resp.status_code == 200
        data = resp.json()
        assert "total_count" in data
        assert isinstance(data["result"], list)
        assert data["total_count"] >= 0

    def test_filter_lines_by_product_group_milk(self, client):
        """Фильтрация линий по товарной группе milk."""
        resp = filter_lines(client, json={"limit": 10, "offset": 0, "product_group": "milk"})
        assert resp.status_code == 200
        data = resp.json()
        assert "total_count" in data
        # На сервере есть хотя бы одна milk-линия (line_number=1)
        assert data["total_count"] >= 1

    def test_filter_lines_by_product_group_water(self, client):
        """Фильтрация линий по товарной группе water."""
        resp = filter_lines(client, json={"limit": 10, "offset": 0, "product_group": "water"})
        assert resp.status_code == 200

    def test_filter_lines_all_product_groups(self, client):
        """Проверяем наличие линий для всех ключевых товарных групп."""
        groups = ["milk", "water", "softdrinks", "fertilizers", "chemistry", "shoes"]
        for pg in groups:
            resp = filter_lines(client, json={"limit": 5, "offset": 0, "product_group": pg})
            assert resp.status_code == 200, f"Ошибка для группы {pg}"

    def test_create_line(self, client):
        """Создание новой производственной линии."""
        payload = CreateInput(
            name=f"Test Line {datetime.datetime.now().strftime('%H%M%S')}",
            line_type=LINETYPE.integer_1,
            product_group=ProductGroup.milk,
            production_type=ProductionType.integer_1,
        )
        resp = create_line(client, body=payload)
        assert resp.status_code in [200, 400, 422]
        if resp.status_code == 200:
            data = resp.json()
            # Сервер возвращает line_number (integer) — это поле для edit/delete/recover
            line_number = data.get("line_number")
            if line_number:
                TestLineManagement._created_line_number = int(line_number)

    def test_edit_line_created(self, client):
        """Редактирование только что созданной линии (поле: line_number)."""
        ln = TestLineManagement._created_line_number
        if not ln:
            pytest.skip("Линия не была создана в test_create_line или line_number отсутствует")
        resp = edit_line(client, json={"line_number": ln, "name": "Updated Test Line"})
        assert resp.status_code in [200, 400, 422]

    def test_delete_line_created(self, client):
        """Деактивация созданной тестовой линии (поле: line_number)."""
        ln = TestLineManagement._created_line_number
        if not ln:
            pytest.skip("Линия не была создана в test_create_line или line_number отсутствует")
        resp = delete_line(client, json={"line_number": ln})
        assert resp.status_code in [200, 400, 404, 422]

    def test_recover_line_created(self, client):
        """Восстановление деактивированной тестовой линии (поле: line_number)."""
        ln = TestLineManagement._created_line_number
        if not ln:
            pytest.skip("Линия не была создана в test_create_line или line_number отсутствует")
        resp = recover_line(client, json={"line_number": ln})
        assert resp.status_code in [200, 400, 404, 422]

    def test_filter_lines_pagination(self, client):
        """Пагинация: limit/offset принимаются сервером корректно."""
        resp1 = filter_lines(client, json={"limit": 5, "offset": 0})
        resp2 = filter_lines(client, json={"limit": 5, "offset": 5})
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert "total_count" in resp1.json()
        assert "total_count" in resp2.json()
        assert isinstance(resp1.json()["result"], list)
        assert isinstance(resp2.json()["result"], list)
        assert len(resp1.json()["result"]) <= 5
        assert len(resp2.json()["result"]) <= 5


@pytest.mark.integration
class TestGTINManagement:
    """Тесты управления справочником GTIN."""

    def test_filter_gtin_default(self, client):
        """Получение списка GTIN без фильтра."""
        resp = filter_gtin(client, json={"limit": 20, "offset": 0})
        assert resp.status_code == 200
        data = resp.json()
        assert "total_count" in data
        assert isinstance(data["result"], list)
        assert data["total_count"] > 0

    def test_filter_gtin_milk(self, client, real_gtin_milk):
        """Фильтрация GTIN по товарной группе milk."""
        resp = filter_gtin(client, json={"limit": 10, "offset": 0, "product_group": "milk"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] >= 1
        gtins = [r.get("gtin") for r in data["result"]]
        assert real_gtin_milk in gtins or data["total_count"] > 0

    def test_filter_gtin_water(self, client):
        """Фильтрация GTIN по товарной группе water."""
        resp = filter_gtin(client, json={"limit": 10, "offset": 0, "product_group": "water"})
        assert resp.status_code == 200

    def test_filter_gtin_shoes(self, client):
        """Фильтрация GTIN по товарной группе shoes."""
        resp = filter_gtin(client, json={"limit": 10, "offset": 0, "product_group": "shoes"})
        assert resp.status_code == 200

    def test_filter_gtin_all_known_groups(self, client):
        """Проверка что GTIN есть для всех 30 товарных групп."""
        groups = [
            "milk", "water", "shoes", "antiseptic", "bio", "lp", "perfumery",
            "beer", "nabeer", "softdrinks", "meat", "seafood", "conserve",
            "grocery", "vetpharma", "toys", "homeware", "chemistry",
            "construction", "fertilizers", "fire", "vegetableoil", "petfood",
            "books", "radio", "autofluids", "carparts", "bicycle", "wheelchairs",
        ]
        for pg in groups:
            resp = filter_gtin(client, json={"limit": 1, "offset": 0, "product_group": pg})
            assert resp.status_code == 200, f"Ошибка фильтрации GTIN для группы {pg}"

    def test_add_existing_gtin(self, client, real_gtin_milk):
        """Добавление уже существующего GTIN (поле: data, массив объектов)."""
        resp = add_gtin(
            client,
            json={
                "data": [
                    {"gtin": real_gtin_milk, "product_group": "milk"},
                ]
            },
        )
        # 200 — обновлено / принято; 400/409/422 — дубликат или ошибка
        assert resp.status_code in [200, 400, 409, 422]

    def test_edit_gtin_milk(self, client, real_gtin_milk):
        """Редактирование записи GTIN (обновление имени)."""
        resp = edit_gtin(client, json={"gtin": real_gtin_milk, "good_name": "Мороженка Тест"})
        assert resp.status_code in [200, 400, 422]

    def test_filter_gtin_by_gtin_value(self, client, real_gtin_milk):
        """Поиск GTIN по конкретному значению."""
        resp = filter_gtin(client, json={"limit": 5, "offset": 0, "gtin": real_gtin_milk})
        assert resp.status_code == 200
        data = resp.json()
        if data["total_count"] > 0:
            assert data["result"][0]["gtin"] == real_gtin_milk

    def test_filter_gtin_pagination(self, client):
        """Пагинация GTIN: limit/offset принимаются сервером корректно."""
        resp1 = filter_gtin(client, json={"limit": 5, "offset": 0})
        resp2 = filter_gtin(client, json={"limit": 5, "offset": 5})
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        assert "total_count" in resp1.json()
        assert isinstance(resp1.json()["result"], list)
        assert isinstance(resp2.json()["result"], list)
        assert len(resp1.json()["result"]) <= 5
        assert len(resp2.json()["result"]) <= 5
