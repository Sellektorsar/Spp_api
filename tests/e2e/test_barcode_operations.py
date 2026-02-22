"""
E2E Сценарий: Генерация штрихкодов и этикеток.
"""
import uuid
import responses


class TestBarcodeOperations:
    """
    E2E Сценарий: Генерация PDF с кодами маркировки.
    """

    def test_01_generate_barcodes_by_codes(self, client, test_context, mock_api):
        """Шаг 1: Генерация PDF по списку кодов."""
        codes = ["010460049400904421k1", "010460049400904421k2"]
        layout_id = str(uuid.uuid4())

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/barcodes/generate_by_codes",
                body=b"%PDF-1.4 fake pdf content...",
                status=200,
                content_type="application/pdf",
            )

        resp = client.post(
            "/api/web/v1/barcodes/generate_by_codes",
            json={"codes": codes, "layout_id": layout_id}
        )

        assert resp.status_code == 200
        assert resp.headers.get("content-type") == "application/pdf"
        print(f"[E2E-BARCODE] PDF сгенерирован для {len(codes)} кодов")

    def test_02_generate_barcodes_by_gtin(self, client, test_context, mock_api):
        """Шаг 2: Генерация PDF по GTIN."""
        gtin = "04600494009044"
        layout_id = str(uuid.uuid4())

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/barcodes/generate_by_gtin",
                body=b"%PDF-1.4 fake pdf content...",
                status=200,
                content_type="application/pdf",
            )

        resp = client.post(
            "/api/web/v1/barcodes/generate_by_gtin",
            json={"gtin": gtin, "layout_id": layout_id, "quantity": 10}
        )

        assert resp.status_code == 200
        assert resp.headers.get("content-type") == "application/pdf"
        print(f"[E2E-BARCODE] PDF сгенерирован для GTIN {gtin}")

    def test_03_generate_barcodes_to_file(self, client, test_context, mock_api):
        """Шаг 3: Генерация и сохранение файла штрихкодов."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/barcodes/generate_to_file",
                json={"file_path": "/tmp/barcodes/job_123.pdf", "status": "ready", "download_url": "/download/job_123.pdf"},
                status=200,
            )

        resp = client.post(
            "/api/web/v1/barcodes/generate_to_file",
            json={"codes": ["010460049400904421k1"], "filename": "job_123.pdf"}
        )

        assert resp.status_code == 200
        print(f"[E2E-BARCODE] Файл сохранен: {resp.json().get('file_path')}")

    def test_04_filter_generated_barcodes(self, client, test_context, mock_api):
        """Шаг 4: Фильтрация сгенерированных штрихкодов."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/barcodes/generated/filter",
                json={
                    "total_count": 2,
                    "result": [
                        {"id": str(uuid.uuid4()), "gtin": "04600494009044", "status": "generated"},
                        {"id": str(uuid.uuid4()), "gtin": "04600494009044", "status": "generated"}
                    ]
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/barcodes/generated/filter",
            json={"gtin": "04600494009044", "limit": 10, "offset": 0}
        )

        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        print(f"[E2E-BARCODE] Найдено сгенерированных: {data.get('total_count')}")
