"""
E2E Сценарий: Проверка кода маркировки (Case 64).
Покрывает UI Case 64: Доступ к разделу "Проверить код".

Пользователь имеет доступ к разделу "Проверить код", при вводе КМ получает по нему данные:
- Статус кода в ГИС МТ
- Информация о продукте (GTIN, наименование)
- История движения (партия, дата производства)
- Текущее местоположение (склад, агрегат)
- Срок годности
"""
import uuid
import responses


class TestCodeVerification:
    """
    E2E Сценарий: Проверка произвольного кода маркировки.
    """

    def test_01_verify_valid_code_in_gis(self, client, test_context, mock_api, real_gtin):
        """
        Шаг 1: Проверка валидного КМ в ГИС МТ.
        Ожидается: Полная информация о коде со статусом "В обороте".
        """
        test_code = f"01{real_gtin}215ABC12345678901234567890123456789"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/check_gis_code",
                json={
                    "code": test_code,
                    "status": "ok",
                    "gis_status": "introduced",  # Введен в оборот
                    "product_name": "Молоко пастеризованное 2.5%",
                    "gtin": real_gtin,
                    "batch": "LOT20240115",
                    "exp_date": "2024-02-15",
                    "production_date": "2024-01-15",
                    "owner": "ООО Тестовый производитель",
                    "inn": "1234567890",
                    "last_operation": {
                        "type": "commissioning",
                        "date": "2024-01-15T10:30:00Z",
                        "location": "Склад №1"
                    }
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/check_gis_code",
            json={"code": test_code}
        )
        
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["gis_status"] == "introduced"
        assert "product_name" in data
        assert "gtin" in data
        print(f"[E2E-CODE-64] Код проверен в ГИС: {data.get('gis_status')}")

    def test_02_verify_code_not_found(self, client, test_context, mock_api):
        """
        Шаг 2: Проверка несуществующего КМ.
        Ожидается: Сообщение о том, что код не найден в ГИС.
        """
        invalid_code = "0104600000000000215INVALID93dGVzdA=="
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/check_gis_code",
                json={
                    "code": invalid_code,
                    "status": "not_found",
                    "gis_status": "unknown",
                    "message": "Код маркировки не найден в системе ГИС МТ"
                },
                status=200,  # Или 404 в зависимости от реализации
            )

        resp = client.post(
            "/api/web/v1/check_gis_code",
            json={"code": invalid_code}
        )
        
        # API может вернуть 200 с ошибкой или 404
        assert resp.status_code in [200, 404]
        if resp.status_code == 200:
            data = resp.json()
            assert data["status"] in ["not_found", "error"]
        print(f"[E2E-CODE-64] Несуществующий код корректно обработан")

    def test_03_verify_code_withdrawn(self, client, test_context, mock_api, real_gtin):
        """
        Шаг 3: Проверка выбывшего кода (списан/выбытие).
        Ожидается: Информация о статусе "Выбыл".
        """
        withdrawn_code = f"01{real_gtin}215WITHDRAWN93dGVzdA=="
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/check_gis_code",
                json={
                    "code": withdrawn_code,
                    "status": "ok",
                    "gis_status": "withdrawn",  # Выбыл
                    "product_name": "Молоко пастеризованное 2.5%",
                    "gtin": real_gtin,
                    "last_operation": {
                        "type": "withdrawal",
                        "date": "2024-01-20T14:15:00Z",
                        "reason": "product_damage"
                    },
                    "message": "Код выбыл из оборота"
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/check_gis_code",
            json={"code": withdrawn_code}
        )
        
        assert resp.status_code == 200
        data = resp.json()
        assert data["gis_status"] == "withdrawn"
        print(f"[E2E-CODE-64] Выбывший код проверен: {data.get('gis_status')}")

    def test_04_verify_code_in_warehouse(self, client, test_context, mock_api, real_gtin):
        """
        Шаг 4: Проверка кода с указанием местоположения на складе.
        Ожидается: Информация о ролике/паллете где находится код.
        """
        warehouse_code = f"01{real_gtin}215WAREHOUSE93dGVzdA=="
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/warehouse/get_roll_by_code",
                json={
                    "code": warehouse_code,
                    "found": True,
                    "location": {
                        "type": "roll",
                        "roll_id": str(uuid.uuid4()),
                        "roll_name": "Ролик #12345",
                        "warehouse_location": "Склад основной"
                    },
                    "product": {
                        "gtin": real_gtin,
                        "name": "Молоко пастеризованное 2.5%"
                    },
                    "status": "available"  # Доступен для использования
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/warehouse/get_roll_by_code",
            json={"code": warehouse_code}
        )
        
        assert resp.status_code == 200
        data = resp.json()
        assert data["found"] is True
        assert "location" in data
        print(f"[E2E-CODE-64] Код найден на складе: {data.get('location', {}).get('type')}")

    def test_05_verify_code_in_aggregation(self, client, test_context, mock_api, real_gtin):
        """
        Шаг 5: Проверка кода в составе агрегата.
        Ожидается: Информация об упаковке/палете где агрегирован код.
        """
        aggregated_code = f"01{real_gtin}215AGGREGATED93dGVzdA=="
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/check_code",
                json={
                    "code": aggregated_code,
                    "found": True,
                    "aggregation_info": {
                        "session_id": str(uuid.uuid4()),
                        "package_sscc": "037123456789012345",
                        "pallet_sscc": "037123456789012346",
                        "hierarchy": [
                            {"level": 0, "type": "code", "value": aggregated_code},
                            {"level": 1, "type": "package", "value": "037123456789012345"},
                            {"level": 2, "type": "pallet", "value": "037123456789012346"}
                        ]
                    },
                    "status": "aggregated"
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/check_code",
            json={"code": aggregated_code}
        )
        
        assert resp.status_code == 200
        data = resp.json()
        assert data["found"] is True
        assert data["status"] == "aggregated"
        assert "aggregation_info" in data
        print(f"[E2E-CODE-64] Код найден в агрегате: упаковка + палета")

    def test_06_verify_code_in_work_shift(self, client, test_context, mock_api, real_gtin):
        """
        Шаг 6: Проверка кода в производственной партии.
        Ожидается: Информация о партии где код был использован.
        """
        shift_code = f"01{real_gtin}215INSHIFT93dGVzdA=="
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/find_work_shift_by_code",
                json={
                    "code": shift_code,
                    "found": True,
                    "work_shift": {
                        "id": str(uuid.uuid4()),
                        "name": "Партия #789",
                        "line_number": 3,
                        "status": "finished",
                        "created_at": "2024-01-10T08:00:00Z",
                        "finished_at": "2024-01-10T16:00:00Z"
                    },
                    "code_status": "utilized",  # Нанесен
                    "reports": [
                        {"type": "utilisation", "status": "sent"},
                        {"type": "circulation", "status": "sent"}
                    ]
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/work_shift/find_work_shift_by_code",
            json={"code": shift_code}
        )
        
        assert resp.status_code == 200
        data = resp.json()
        assert data["found"] is True
        assert "work_shift" in data
        print(f"[E2E-CODE-64] Код найден в партии: {data.get('work_shift', {}).get('name')}")

    def test_07_verify_invalid_code_format(self, client, test_context, mock_api):
        """
        Шаг 7: Проверка кода с невалидным форматом.
        Ожидается: Ошибка валидации формата.
        """
        invalid_format_code = "NOT_A_VALID_CODE_FORMAT"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/check_gis_code",
                json={
                    "code": invalid_format_code,
                    "status": "error",
                    "error_type": "invalid_format",
                    "message": "Неверный формат кода маркировки"
                },
                status=422,
            )

        resp = client.post(
            "/api/web/v1/check_gis_code",
            json={"code": invalid_format_code}
        )
        
        assert resp.status_code in [400, 422]
        print(f"[E2E-CODE-64] Невалидный формат корректно отклонен")

    def test_08_verify_code_without_gtin(self, client, test_context, mock_api):
        """
        Шаг 8: Проверка кода без GTIN (некорректный Data Matrix).
        Ожидается: Ошибка о недостающих данных.
        """
        incomplete_code = "93dGVzdA=="  # Только криптоподпись без GTIN
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/check_gis_code",
                json={
                    "code": incomplete_code,
                    "status": "error",
                    "error_type": "incomplete_data",
                    "message": "Код не содержит GTIN"
                },
                status=422,
            )

        resp = client.post(
            "/api/web/v1/check_gis_code",
            json={"code": incomplete_code}
        )
        
        assert resp.status_code in [400, 422]
        print(f"[E2E-CODE-64] Неполный код корректно отклонен")
