"""
E2E Сценарии: Расширенная функциональность агрегации.
Покрывает: пресеты, паллеты, техническое зрение, расформирование.
"""
import uuid
import responses


class TestAggregationAdvanced:
    """
    E2E Сценарии: Сложная логика агрегационных сессий.
    """

    def test_01_create_and_save_preset(self, client, test_context, mock_api):
        """Шаг 1: Создание и сохранение пресета (Case 32)."""
        preset_name = "Auto Test Preset Box"
        preset_id = str(uuid.uuid4())
        test_context.add("agg_preset_id", preset_id)

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/preset/add",
                json={
                    "id": preset_id,
                    "name": preset_name,
                    "package_type": "box",
                    "pallet_type": "none",
                    "status": "created"
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/preset/add",
            json={
                "name": preset_name,
                "package_type": "box",
                "pallet_type": "none",
                "package_size": 10
            }
        )
        assert resp.status_code == 200
        print(f"[E2E-AGG-ADV] Пресет создан: {preset_id}")

    def test_02_filter_presets(self, client, test_context, mock_api):
        """Шаг 2: Фильтрация пресетов."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/preset/filter",
                json={
                    "total_count": 1,
                    "result": [
                        {
                            "id": test_context.get_last("agg_preset_id"),
                            "name": "Auto Test Preset Box",
                            "package_type": "box"
                        }
                    ]
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/preset/filter",
            json={"limit": 10, "offset": 0}
        )
        assert resp.status_code == 200
        print(f"[E2E-AGG-ADV] Пресеты получены")

    def test_03_start_session_with_preset(self, client, test_context, mock_api):
        """Шаг 3: Запуск сессии с использованием пресета (Case 33)."""
        session_id = str(uuid.uuid4())
        line_id = 1
        test_context.add("adv_agg_session_id", session_id)

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/start",
                json={
                    "id": session_id,
                    "line_id": line_id,
                    "status": "active",
                    "preset_id": test_context.get_last("agg_preset_id")
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/start",
            json={
                "line_id": line_id,
                "preset_id": test_context.get_last("agg_preset_id"),
                "name": "Session with Preset"
            }
        )
        assert resp.status_code == 200
        print(f"[E2E-AGG-ADV] Сессия запущена с пресетом: {session_id}")

    def test_04_add_codes_to_session(self, client, test_context, mock_api):
        """Шаг 4: Добавление КМ в сессию (2D сканер, печать на линии)."""
        session_id = test_context.get_last("adv_agg_session_id")

        for i in range(5):
            code = f"0104600494009044215Agg{i:03d}93dGVzdA=="
            if mock_api:
                mock_api.add(
                    responses.POST,
                    f"{client.base_url}/api/web/v1/aggregation_session/add_code",
                    json={
                        "status": "ok",
                        "code": code,
                        "codes_in_package": i + 1
                    },
                    status=200,
                )

            resp = client.post(
                "/api/web/v1/aggregation_session/add_code",
                json={"id": session_id, "code": code}
            )
            assert resp.status_code == 200

        print(f"[E2E-AGG-ADV] 5 КМ добавлено в сессию")

    def test_05_add_package(self, client, test_context, mock_api):
        """Шаг 5: Добавление упаковки."""
        session_id = test_context.get_last("adv_agg_session_id")
        package_scc = "037123456789012340"

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/add_package",
                json={
                    "status": "package_added",
                    "sscc": package_scc,
                    "codes_count": 5
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/add_package",
            json={"id": session_id, "sscc": package_scc}
        )
        assert resp.status_code == 200
        test_context.add("agg_package_scc", package_scc)
        print(f"[E2E-AGG-ADV] Упаковка добавлена: {package_scc}")

    def test_06_add_pallet(self, client, test_context, mock_api):
        """Шаг 6: Паллетная агрегация - добавление палеты (Case 48)."""
        session_id = test_context.get_last("adv_agg_session_id")
        pallet_scc = "037123456789012341"

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/add_pallet",
                json={
                    "status": "pallet_added",
                    "sscc": pallet_scc,
                    "packages": []
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/add_pallet",
            json={"id": session_id, "sscc": pallet_scc}
        )
        assert resp.status_code == 200
        test_context.add("agg_pallet_scc", pallet_scc)
        print(f"[E2E-AGG-ADV] Палета добавлена: {pallet_scc}")

    def test_07_add_package_to_pallet(self, client, test_context, mock_api):
        """Шаг 7: Добавление упаковки в палету."""
        session_id = test_context.get_last("adv_agg_session_id")
        package_scc = test_context.get_last("agg_package_scc")
        pallet_scc = test_context.get_last("agg_pallet_scc")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/add_code_to_package",
                json={
                    "status": "added_to_pallet",
                    "package_sscc": package_scc,
                    "pallet_sscc": pallet_scc
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/add_code_to_package",
            json={
                "id": session_id,
                "code": package_scc,
                "pallet_sscc": pallet_scc
            }
        )
        assert resp.status_code == 200
        print(f"[E2E-AGG-ADV] Упаковка добавлена в палету")

    def test_08_close_pallet(self, client, test_context, mock_api):
        """Шаг 8: Закрытие палеты."""
        session_id = test_context.get_last("adv_agg_session_id")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/close_pallet",
                json={
                    "status": "pallet_closed",
                    "packages_count": 1,
                    "pallet_sscc": test_context.get_last("agg_pallet_scc")
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/close_pallet",
            json={"id": session_id}
        )
        assert resp.status_code == 200
        print(f"[E2E-AGG-ADV] Палета закрыта")

    def test_09_vision_mode_add_codes(self, client, test_context, mock_api):
        """Шаг 9: Наполнение сессии через 'Техническое зрение' (Case 37-38)."""
        session_id = test_context.get_last("adv_agg_session_id")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/vision/add_codes",
                json={
                    "status": "processed",
                    "added_codes": 10,
                    "errors": []
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/vision/add_codes",
            json={
                "id": session_id,
                "codes": [f"code{i}" for i in range(10)],
                "timestamp": "2024-01-15T10:30:00Z"
            }
        )
        assert resp.status_code == 200
        print(f"[E2E-AGG-ADV] КМ добавлены через Vision API")

    def test_10_package_info(self, client, test_context, mock_api):
        """Шаг 10: Получение информации об упаковке (Case 51)."""
        session_id = test_context.get_last("adv_agg_session_id")
        package_scc = test_context.get_last("agg_package_scc")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/package_info",
                json={
                    "sscc": package_scc,
                    "type": "package",
                    "codes_count": 5,
                    "status": "active"
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/package_info",
            json={"id": session_id, "code": package_scc}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("type") == "package"
        print(f"[E2E-AGG-ADV] Информация об упаковке получена")

    def test_11_withdrawal_code(self, client, test_context, mock_api):
        """Шаг 11: Изъятие кода из агрегата (редактирование)."""
        session_id = test_context.get_last("adv_agg_session_id")
        code_to_withdraw = "0104600494009044215Withdraw93dGVzdA=="

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/withdrawal_code",
                json={
                    "status": "withdrawn",
                    "code": code_to_withdraw,
                    "previous_parent": test_context.get_last("agg_package_scc")
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/withdrawal_code",
            json={"id": session_id, "code": code_to_withdraw}
        )
        assert resp.status_code == 200
        print(f"[E2E-AGG-ADV] Код изъят из агрегата")

    def test_12_disband_package(self, client, test_context, mock_api):
        """Шаг 12: Расформирование упаковки (Case 53)."""
        session_id = test_context.get_last("adv_agg_session_id")
        package_scc = test_context.get_last("agg_package_scc")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/disbandment_package",
                json={
                    "status": "disbanded",
                    "sscc": package_scc,
                    "released_codes": 5
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/disbandment_package",
            json={"id": session_id, "sscc": package_scc}
        )
        assert resp.status_code == 200
        print(f"[E2E-AGG-ADV] Упаковка расформирована: {package_scc}")

    def test_13_finish_session(self, client, test_context, mock_api):
        """Шаг 13: Завершение сессии (Case 40)."""
        session_id = test_context.get_last("adv_agg_session_id")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/finish",
                json={
                    "id": session_id,
                    "status": "finished",
                    "total_codes": 15,
                    "packages": 1,
                    "pallets": 1
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/finish",
            json={"id": session_id}
        )
        assert resp.status_code == 200
        print(f"[E2E-AGG-ADV] Сессия завершена: {session_id}")

    def test_14_delete_preset(self, client, test_context, mock_api):
        """Шаг 14: Удаление пресета (Case 34)."""
        preset_id = test_context.get_last("agg_preset_id")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/preset/delete",
                json={"id": preset_id, "status": "deleted"},
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/preset/delete",
            json={"id": preset_id}
        )
        assert resp.status_code == 200
        print(f"[E2E-AGG-ADV] Пресет удален: {preset_id}")
