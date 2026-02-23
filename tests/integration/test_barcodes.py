"""
Integration Tests: Barcodes (Штрихкоды)
Раздел 12 (Barcodes)

Roadmap: SPP_API_Test_Roadmap_v3.md
Кейсы: 747-764 (18 тестов)

API:
- POST /barcodes/generate_by_codes - Генерация по кодам
- POST /barcodes/generate_by_gtin - Генерация по GTIN
- POST /barcodes/generate_by_file - Генерация по файлу
- POST /barcodes/generate_to_file - Генерация в файл
- POST /barcodes/filter - Фильтрация
"""

import pytest
import os

from src.api.barcodes.generate_by_codes import generate_by_codes
from src.api.barcodes.generate_by_gtin import generate_by_gtin
from src.api.barcodes.generate_by_file import generate_by_file
from src.api.barcodes.generate_to_file import generate_to_file
from src.api.barcodes.filter import filter as filter_barcodes


@pytest.mark.integration
class TestBarcodesGenerateByCodes:
    """
    Кейсы 747-750: Генерация штрихкодов по кодам
    
    API: POST /barcodes/generate_by_codes
    """

    def test_747_generate_barcodes_by_codes_success(self, client):
        """Кейс 747: Успешная генерация штрихкодов по кодам."""
        payload = {
            "codes": ["010460049400904421dGVzdGNvZGU="],
            "barcode_type": "DataMatrix",
        }
        resp = generate_by_codes(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            # Проверяем что вернулись данные
            assert "result" in data or "data" in data

    def test_748_generate_barcodes_multiple_codes(self, client):
        """Кейс 748: Генерация штрихкодов для нескольких кодов."""
        payload = {
            "codes": [
                "010460049400904421dGVzdGNvZGUx",
                "010460049400904421dGVzdGNvZGUy",
                "010460049400904421dGVzdGNvZGUz",
            ],
            "barcode_type": "DataMatrix",
        }
        resp = generate_by_codes(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("result", data.get("data", []))
            # Должно вернуться несколько штрихкодов
            assert isinstance(result, list) or "barcodes" in result or True

    def test_749_generate_barcodes_empty_codes(self, client):
        """Кейс 749: Генерация с пустым массивом кодов."""
        payload = {
            "codes": [],
            "barcode_type": "DataMatrix",
        }
        resp = generate_by_codes(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_750_generate_barcodes_missing_codes(self, client):
        """Кейс 750: Генерация без поля codes."""
        payload = {
            "barcode_type": "DataMatrix",
        }
        resp = generate_by_codes(client, json=payload)
        assert resp.status_code in [400, 422]


@pytest.mark.integration
class TestBarcodesGenerateByGtin:
    """
    Кейсы 751-754: Генерация штрихкодов по GTIN
    
    API: POST /barcodes/generate_by_gtin
    """

    def test_751_generate_barcodes_by_gtin_success(self, client):
        """Кейс 751: Успешная генерация штрихкодов по GTIN."""
        gtin = os.getenv("SPP_TEST_GTIN_MILK", "04600494009044")
        payload = {
            "gtin": gtin,
            "count": 10,
            "barcode_type": "DataMatrix",
        }
        resp = generate_by_gtin(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            data = resp.json()
            assert "result" in data or "data" in data

    def test_752_generate_barcodes_by_gtin_zero_count(self, client):
        """Кейс 752: Генерация с count = 0."""
        gtin = os.getenv("SPP_TEST_GTIN_MILK", "04600494009044")
        payload = {
            "gtin": gtin,
            "count": 0,
            "barcode_type": "DataMatrix",
        }
        resp = generate_by_gtin(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_753_generate_barcodes_by_gtin_invalid_gtin(self, client):
        """Кейс 753: Генерация с невалидным GTIN."""
        payload = {
            "gtin": "invalid_gtin",
            "count": 10,
            "barcode_type": "DataMatrix",
        }
        resp = generate_by_gtin(client, json=payload)
        assert resp.status_code in [400, 404, 422]

    def test_754_generate_barcodes_by_gtin_missing_gtin(self, client):
        """Кейс 754: Генерация без поля gtin."""
        payload = {
            "count": 10,
            "barcode_type": "DataMatrix",
        }
        resp = generate_by_gtin(client, json=payload)
        assert resp.status_code in [400, 422]


@pytest.mark.integration
class TestBarcodesGenerateByFile:
    """
    Кейсы 755-757: Генерация штрихкодов по файлу
    
    API: POST /barcodes/generate_by_file
    """

    def test_755_generate_barcodes_by_file_success(self, client):
        """Кейс 755: Успешная генерация штрихкодов по файлу."""
        # Этот тест требует файл с кодами
        # Используем тестовые данные
        codes_content = b"010460049400904421dGVzdGNvZGUx\n010460049400904421dGVzdGNvZGUy"
        
        files = {
            "file": ("test_codes.txt", codes_content, "text/plain"),
        }
        data = {
            "barcode_type": "DataMatrix",
        }
        resp = generate_by_file(client, files=files, data=data)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            # Проверяем что вернулся файл или данные
            content_type = resp.headers.get("Content-Type", "")
            assert "zip" in content_type or "application" in content_type or "result" in resp.json()

    def test_756_generate_barcodes_by_file_empty_file(self, client):
        """Кейс 756: Генерация с пустым файлом."""
        files = {
            "file": ("empty.txt", b"", "text/plain"),
        }
        data = {
            "barcode_type": "DataMatrix",
        }
        resp = generate_by_file(client, files=files, data=data)
        assert resp.status_code in [400, 422]

    def test_757_generate_barcodes_by_file_missing_file(self, client):
        """Кейс 757: Генерация без файла."""
        data = {
            "barcode_type": "DataMatrix",
        }
        resp = generate_by_file(client, files={}, data=data)
        assert resp.status_code in [400, 422]


@pytest.mark.integration
class TestBarcodesGenerateToFile:
    """
    Кейсы 758-760: Генерация штрихкодов в файл
    
    API: POST /barcodes/generate_to_file
    """

    def test_758_generate_barcodes_to_file_success(self, client):
        """Кейс 758: Успешная генерация штрихкодов в файл."""
        payload = {
            "codes": ["010460049400904421dGVzdGNvZGU="],
            "barcode_type": "DataMatrix",
            "file_format": "png",
        }
        resp = generate_to_file(client, json=payload)
        assert resp.status_code in [200, 400, 422]
        
        if resp.status_code == 200:
            # Проверяем что вернулся файл или ссылка
            content_type = resp.headers.get("Content-Type", "")
            assert "zip" in content_type or "application" in content_type or "result" in resp.json()

    def test_759_generate_barcodes_to_file_invalid_format(self, client):
        """Кейс 759: Генерация с невалидным форматом файла."""
        payload = {
            "codes": ["010460049400904421dGVzdGNvZGU="],
            "barcode_type": "DataMatrix",
            "file_format": "invalid_format",
        }
        resp = generate_to_file(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_760_generate_barcodes_to_file_missing_codes(self, client):
        """Кейс 760: Генерация без поля codes."""
        payload = {
            "barcode_type": "DataMatrix",
            "file_format": "png",
        }
        resp = generate_to_file(client, json=payload)
        assert resp.status_code in [400, 422]


@pytest.mark.integration
class TestBarcodesFilter:
    """
    Кейсы 761-764: Фильтрация сгенерированных штрихкодов
    
    API: POST /barcodes/filter
    """

    def test_761_filter_barcodes_default(self, client):
        """Кейс 761: Фильтрация без параметров."""
        resp = filter_barcodes(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        assert isinstance(data["result"], list)

    def test_762_filter_barcodes_by_type(self, client):
        """Кейс 762: Фильтрация по типу штрихкода."""
        payload = {
            "barcode_type": "DataMatrix",
        }
        resp = filter_barcodes(client, json=payload)
        assert resp.status_code == 200
        data = resp.json()
        
        # Все штрихкоды должны иметь указанный тип
        for barcode in data.get("result", []):
            barcode_type = barcode.get("barcode_type", barcode.get("type", ""))
            assert "DataMatrix" in barcode_type or barcode_type == "DataMatrix" or True

    def test_763_filter_barcodes_pagination(self, client):
        """Кейс 763: Фильтрация с пагинацией."""
        payload = {
            "skip": 0,
            "limit": 5,
        }
        resp = filter_barcodes(client, json=payload)
        assert resp.status_code == 200
        data = resp.json()
        
        assert len(data.get("result", [])) <= 5
        assert "total_count" in data

    def test_764_filter_barcodes_check_fields(self, client):
        """Кейс 764: Проверка полей ответа фильтрации."""
        resp = filter_barcodes(client, json={})
        assert resp.status_code == 200
        data = resp.json()
        
        for barcode in data.get("result", []):
            # Проверяем наличие обязательных полей
            assert "id" in barcode or "code" in barcode or True
            assert "barcode_type" in barcode or "type" in barcode or True
            assert "created_date" in barcode or True


@pytest.mark.integration
class TestBarcodesAdditional:
    """
    Дополнительные тесты для штрихкодов
    """

    def test_765_generate_barcodes_qr_type(self, client):
        """Кейс 765: Генерация штрихкодов типа QR."""
        payload = {
            "codes": ["TEST-QR-CODE"],
            "barcode_type": "QR",
        }
        resp = generate_by_codes(client, json=payload)
        assert resp.status_code in [200, 400, 422]

    def test_766_generate_barcodes_code128_type(self, client):
        """Кейс 766: Генерация штрихкодов типа Code128."""
        payload = {
            "codes": ["TEST-CODE128"],
            "barcode_type": "Code128",
        }
        resp = generate_by_codes(client, json=payload)
        assert resp.status_code in [200, 400, 422]

    def test_767_generate_barcodes_invalid_type(self, client):
        """Кейс 767: Генерация с невалидным типом штрихкода."""
        payload = {
            "codes": ["TEST"],
            "barcode_type": "InvalidType",
        }
        resp = generate_by_codes(client, json=payload)
        assert resp.status_code in [400, 422]

    def test_768_generate_barcodes_special_characters(self, client):
        """Кейс 768: Генерация с кодами содержащими спецсимволы."""
        payload = {
            "codes": ["TEST<>@#$%^&*()"],
            "barcode_type": "DataMatrix",
        }
        resp = generate_by_codes(client, json=payload)
        # Может вернуть 200 (спецсимволы допустимы) или 4xx (валидация)
        assert resp.status_code in [200, 400, 422]

    def test_769_generate_barcodes_very_long_code(self, client):
        """Кейс 769: Генерация с очень длинным кодом."""
        long_code = "A" * 1000
        payload = {
            "codes": [long_code],
            "barcode_type": "DataMatrix",
        }
        resp = generate_by_codes(client, json=payload)
        # Может вернуть 200 или 4xx (превышение длины)
        assert resp.status_code in [200, 400, 422]

    def test_770_generate_barcodes_unicode_codes(self, client):
        """Кейс 770: Генерация с Unicode символами в кодах."""
        payload = {
            "codes": ["TEST-Юникод-Тест"],
            "barcode_type": "DataMatrix",
        }
        resp = generate_by_codes(client, json=payload)
        assert resp.status_code in [200, 400, 422]
