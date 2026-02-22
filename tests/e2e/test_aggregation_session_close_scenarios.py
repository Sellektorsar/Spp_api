"""
E2E Сценарии: Закрытие агрегационных сессий с неполными упаковками/палетами.
Покрывает UI Cases: 41-46

Комбинации:
- Case 41: Неполная упаковка + Полная палета (печать на линии)
- Case 42: Неполная упаковка + Полная палета (преднанесенный стикер)
- Case 43: Полная упаковка + Неполная палета (печать на линии)
- Case 44: Полная упаковка + Неполная палета (преднанесенный стикер)
- Case 45: Неполная упаковка + Неполная палета (печать на линии)
- Case 46: Неполная упаковка + Неполная палета (преднанесенный стикер)
"""
import uuid
import pytest
import responses


class TestAggregationSessionCloseScenarios:
    """
    E2E Сценарии: Закрытие сессий с различными комбинациями заполненности.
    """

    @pytest.fixture
    def base_session_data(self):
        """Базовые данные для сессии."""
        return {
            "session_id": str(uuid.uuid4()),
            "line_id": 1,
            "package_scc": "037123456789012340",
            "pallet_scc": "037123456789012341",
            "partial_package_scc": "037123456789012342",
            "partial_pallet_scc": "037123456789012343",
        }

    def _mock_finish_response(self, mock_api, base_url, session_id, status="finished", 
                              printed_packages=None, printed_pallet=None, requires_confirmation=False):
        """Вспомогательный метод для мока ответа finish."""
        response_data = {
            "id": session_id,
            "status": status,
            "finished_at": "2024-01-15T10:30:00Z",
        }
        
        if printed_packages:
            response_data["printed_packages"] = printed_packages
        if printed_pallet:
            response_data["printed_pallet"] = printed_pallet
        if requires_confirmation:
            response_data["requires_confirmation"] = True
            response_data["confirmation_reason"] = "partial_container"
            
        mock_api.add(
            responses.POST,
            f"{base_url}/api/web/v1/aggregation_session/finish",
            json=response_data,
            status=200,
        )

    # ============ CASE 41: Неполная упаковка + Полная палета (печать на линии) ============
    def test_41_close_partial_package_full_pallet_print_line(
        self, client, test_context, mock_api, base_session_data
    ):
        """
        Case 41: Закрытие сессии с незаполненной упаковкой и полной палетой.
        Режим: Печать на линии.
        Ожидается: Подтверждение неполной упаковки, печать кодов упаковки и палеты.
        """
        session_id = base_session_data["session_id"]
        test_context.add("case41_session_id", session_id)

        # 1. Запуск сессии с печатью на линии
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/start",
                json={
                    "id": session_id,
                    "line_id": base_session_data["line_id"],
                    "mode": "print_on_line",
                    "status": "active"
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/start",
            json={
                "line_id": base_session_data["line_id"],
                "name": "Case 41 - Partial Package + Full Pallet",
                "mode": "print_on_line",
                "collect_pallets": True
            }
        )
        assert resp.status_code == 200

        # 2. Добавляем неполную упаковку (3 из 10 КМ)
        partial_package = base_session_data["partial_package_scc"]
        for i in range(3):
            if mock_api:
                mock_api.add(
                    responses.POST,
                    f"{client.base_url}/api/web/v1/aggregation_session/add_code",
                    json={"status": "ok", "code_count": i + 1},
                    status=200,
                )
            resp = client.post(
                "/api/web/v1/aggregation_session/add_code",
                json={"id": session_id, "code": f"0104600494009044215C41{i}93dGVzdA=="}
            )
            assert resp.status_code == 200

        # 3. Добавляем полную палету (закрытая)
        full_pallet = base_session_data["pallet_scc"]
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/add_pallet",
                json={"status": "pallet_added", "sscc": full_pallet},
                status=200,
            )
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/close_pallet",
                json={"status": "pallet_closed", "sscc": full_pallet, "packages_count": 5},
                status=200,
            )

        # Добавляем палету и закрываем
        resp = client.post(
            "/api/web/v1/aggregation_session/add_pallet",
            json={"id": session_id, "sscc": full_pallet}
        )
        assert resp.status_code == 200

        resp = client.post(
            "/api/web/v1/aggregation_session/close_pallet",
            json={"id": session_id, "sscc": full_pallet}
        )
        assert resp.status_code == 200

        # 4. Пытаемся закрыть сессию - требуется подтверждение неполной упаковки
        if mock_api:
            # Первый вызов - требует подтверждения
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/finish",
                json={
                    "id": session_id,
                    "status": "requires_confirmation",
                    "reason": "partial_package",
                    "partial_package_sscc": partial_package,
                    "message": "Упаковка заполнена не полностью (3/10). Закрыть сессию?"
                },
                status=200,
            )
            # Повторный вызов с подтверждением - успех
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/finish",
                json={
                    "id": session_id,
                    "status": "finished",
                    "printed_packages": [partial_package],
                    "printed_pallet": full_pallet,
                    "partial_package_closed": True
                },
                status=200,
            )

        # Первый вызов без подтверждения
        resp = client.post(
            "/api/web/v1/aggregation_session/finish",
            json={"id": session_id}
        )
        assert resp.status_code == 200
        data = resp.json()
        
        # Если требуется подтверждение - подтверждаем
        if data.get("status") == "requires_confirmation":
            resp = client.post(
                "/api/web/v1/aggregation_session/finish",
                json={
                    "id": session_id,
                    "confirm_partial": True,
                    "close_partial_package": True
                }
            )
            assert resp.status_code == 200
            data = resp.json()

        assert data["status"] == "finished"
        print(f"[E2E-CASE41] Сессия закрыта: неполная упаковка + полная палета (печать на линии)")

    # ============ CASE 42: Неполная упаковка + Полная палета (преднанесенный стикер) ============
    def test_42_close_partial_package_full_pallet_pre_printed(
        self, client, test_context, mock_api, base_session_data
    ):
        """
        Case 42: Закрытие сессии с незаполненной упаковкой и полной палетой.
        Режим: Преднанесенный стикер.
        Ожидается: Ввод кода палеты для закрытия.
        """
        session_id = str(uuid.uuid4())
        test_context.add("case42_session_id", session_id)

        # Запуск с преднанесенными стикерами
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/start",
                json={
                    "id": session_id,
                    "line_id": base_session_data["line_id"],
                    "mode": "pre_printed",
                    "status": "active"
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/start",
            json={
                "line_id": base_session_data["line_id"],
                "name": "Case 42 - Partial Package + Full Pallet (Pre-printed)",
                "mode": "pre_printed",
                "collect_pallets": True
            }
        )
        assert resp.status_code == 200

        # Добавляем неполную упаковку через преднанесенный стикер
        partial_package = base_session_data["partial_package_scc"]
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/add_package",
                json={"status": "package_added", "sscc": partial_package, "codes_count": 4},
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/add_package",
            json={"id": session_id, "sscc": partial_package}
        )
        assert resp.status_code == 200

        # Добавляем палету
        full_pallet = base_session_data["pallet_scc"]
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/close_pallet",
                json={"status": "pallet_closed", "sscc": full_pallet},
                status=200,
            )

        # Закрытие с вводом кода палеты
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/finish",
                json={
                    "id": session_id,
                    "status": "finished",
                    "pallet_sscc": full_pallet,
                    "partial_package_handled": True
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/finish",
            json={
                "id": session_id,
                "pallet_sscc": full_pallet,  # Для преднанесенного стикера требуется SSCC
                "confirm_partial": True
            }
        )
        assert resp.status_code == 200
        print(f"[E2E-CASE42] Сессия закрыта: неполная упаковка + полная палета (преднанесенный)")

    # ============ CASE 43: Полная упаковка + Неполная палета (печать на линии) ============
    def test_43_close_full_package_partial_pallet_print_line(
        self, client, test_context, mock_api, base_session_data
    ):
        """
        Case 43: Закрытие сессии с полной упаковкой и неполной палетой.
        Режим: Печать на линии.
        Ожидается: Подтверждение неполной палеты, печать кода палеты.
        """
        session_id = str(uuid.uuid4())
        test_context.add("case43_session_id", session_id)

        # Запуск с печатью на линии
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/start",
                json={
                    "id": session_id,
                    "line_id": base_session_data["line_id"],
                    "mode": "print_on_line",
                    "status": "active"
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/start",
            json={
                "line_id": base_session_data["line_id"],
                "name": "Case 43 - Full Package + Partial Pallet",
                "mode": "print_on_line",
                "collect_pallets": True,
                "pallet_size": 5  # Палета на 5 упаковок
            }
        )
        assert resp.status_code == 200

        # Добавляем полную упаковку (полностью заполнена)
        full_package = base_session_data["package_scc"]
        for i in range(10):  # Полная упаковка
            if mock_api:
                mock_api.add(
                    responses.POST,
                    f"{client.base_url}/api/web/v1/aggregation_session/add_code",
                    json={"status": "ok", "package_full": i == 9},
                    status=200,
                )
            resp = client.post(
                "/api/web/v1/aggregation_session/add_code",
                json={"id": session_id, "code": f"0104600494009044215C43{i}93dGVzdA=="}
            )
            assert resp.status_code == 200

        # Добавляем палету (незаполненная - только 1 упаковка из 5)
        partial_pallet = base_session_data["partial_pallet_scc"]
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/add_pallet",
                json={"status": "pallet_added", "sscc": partial_pallet, "fill_ratio": 0.2},
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/add_pallet",
            json={"id": session_id, "sscc": partial_pallet}
        )
        assert resp.status_code == 200

        # Закрытие с подтверждением неполной палеты
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/finish",
                json={
                    "id": session_id,
                    "status": "finished",
                    "partial_pallet_closed": True,
                    "pallet_sscc": partial_pallet,
                    "packages_in_pallet": 1,
                    "printed_pallet": partial_pallet
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/finish",
            json={
                "id": session_id,
                "confirm_partial": True,
                "close_partial_pallet": True
            }
        )
        assert resp.status_code == 200
        print(f"[E2E-CASE43] Сессия закрыта: полная упаковка + неполная палета (печать на линии)")

    # ============ CASE 44: Полная упаковка + Неполная палета (преднанесенный стикер) ============
    def test_44_close_full_package_partial_pallet_pre_printed(
        self, client, test_context, mock_api, base_session_data
    ):
        """
        Case 44: Закрытие сессии с полной упаковкой и неполной палетой.
        Режим: Преднанесенный стикер.
        Ожидается: Ввод кода палеты для закрытия.
        """
        session_id = str(uuid.uuid4())
        test_context.add("case44_session_id", session_id)

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/start",
                json={
                    "id": session_id,
                    "line_id": base_session_data["line_id"],
                    "mode": "pre_printed",
                    "status": "active"
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/start",
            json={
                "line_id": base_session_data["line_id"],
                "name": "Case 44 - Full Package + Partial Pallet (Pre-printed)",
                "mode": "pre_printed",
                "collect_pallets": True
            }
        )
        assert resp.status_code == 200

        # Добавляем полную упаковку
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/add_package",
                json={"status": "package_added", "sscc": base_session_data["package_scc"]},
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/add_package",
            json={"id": session_id, "sscc": base_session_data["package_scc"]}
        )
        assert resp.status_code == 200

        # Закрытие с вводом кода неполной палеты
        partial_pallet = base_session_data["partial_pallet_scc"]
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/finish",
                json={
                    "id": session_id,
                    "status": "finished",
                    "pallet_sscc": partial_pallet,
                    "partial_pallet_handled": True
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/finish",
            json={
                "id": session_id,
                "pallet_sscc": partial_pallet,
                "confirm_partial": True
            }
        )
        assert resp.status_code == 200
        print(f"[E2E-CASE44] Сессия закрыта: полная упаковка + неполная палета (преднанесенный)")

    # ============ CASE 45: Неполная упаковка + Неполная палета (печать на линии) ============
    def test_45_close_partial_package_partial_pallet_print_line(
        self, client, test_context, mock_api, base_session_data
    ):
        """
        Case 45: Закрытие сессии с незаполненной упаковкой и неполной палетой.
        Режим: Печать на линии.
        Ожидается: Двойное подтверждение (упаковка и палета), печать обоих кодов.
        """
        session_id = str(uuid.uuid4())
        test_context.add("case45_session_id", session_id)

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/start",
                json={
                    "id": session_id,
                    "line_id": base_session_data["line_id"],
                    "mode": "print_on_line",
                    "status": "active"
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/start",
            json={
                "line_id": base_session_data["line_id"],
                "name": "Case 45 - Partial Package + Partial Pallet",
                "mode": "print_on_line",
                "collect_pallets": True
            }
        )
        assert resp.status_code == 200

        # Неполная упаковка (2 КМ)
        partial_package = base_session_data["partial_package_scc"]
        for i in range(2):
            if mock_api:
                mock_api.add(
                    responses.POST,
                    f"{client.base_url}/api/web/v1/aggregation_session/add_code",
                    json={"status": "ok"},
                    status=200,
                )
            resp = client.post(
                "/api/web/v1/aggregation_session/add_code",
                json={"id": session_id, "code": f"0104600494009044215C45{i}93dGVzdA=="}
            )
            assert resp.status_code == 200

        # Неполная палета
        partial_pallet = base_session_data["partial_pallet_scc"]
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/add_pallet",
                json={"status": "pallet_added", "sscc": partial_pallet},
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/add_pallet",
            json={"id": session_id, "sscc": partial_pallet}
        )
        assert resp.status_code == 200

        # Закрытие с двойным подтверждением
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/finish",
                json={
                    "id": session_id,
                    "status": "finished",
                    "partial_package_closed": True,
                    "partial_pallet_closed": True,
                    "printed_packages": [partial_package],
                    "printed_pallet": partial_pallet
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/finish",
            json={
                "id": session_id,
                "confirm_partial": True,
                "close_partial_package": True,
                "close_partial_pallet": True
            }
        )
        assert resp.status_code == 200
        print(f"[E2E-CASE45] Сессия закрыта: неполная упаковка + неполная палета (печать на линии)")

    # ============ CASE 46: Неполная упаковка + Неполная палета (преднанесенный стикер) ============
    def test_46_close_partial_package_partial_pallet_pre_printed(
        self, client, test_context, mock_api, base_session_data
    ):
        """
        Case 46: Закрытие сессии с незаполненной упаковкой и неполной палетой.
        Режим: Преднанесенный стикер.
        Ожидается: Подтверждение и ввод кода палеты.
        """
        session_id = str(uuid.uuid4())
        test_context.add("case46_session_id", session_id)

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/start",
                json={
                    "id": session_id,
                    "line_id": base_session_data["line_id"],
                    "mode": "pre_printed",
                    "status": "active"
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/start",
            json={
                "line_id": base_session_data["line_id"],
                "name": "Case 46 - Partial Package + Partial Pallet (Pre-printed)",
                "mode": "pre_printed",
                "collect_pallets": True
            }
        )
        assert resp.status_code == 200

        # Неполная упаковка
        partial_package = base_session_data["partial_package_scc"]
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/add_package",
                json={"status": "package_added", "sscc": partial_package, "codes_count": 3},
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/add_package",
            json={"id": session_id, "sscc": partial_package}
        )
        assert resp.status_code == 200

        # Закрытие с вводом кода палеты
        partial_pallet = base_session_data["partial_pallet_scc"]
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/finish",
                json={
                    "id": session_id,
                    "status": "finished",
                    "pallet_sscc": partial_pallet,
                    "partial_package_handled": True,
                    "partial_pallet_handled": True
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/aggregation_session/finish",
            json={
                "id": session_id,
                "pallet_sscc": partial_pallet,
                "confirm_partial": True,
                "close_partial_package": True
            }
        )
        assert resp.status_code == 200
        print(f"[E2E-CASE46] Сессия закрыта: неполная упаковка + неполная палета (преднанесенный)")

    # ============ Дополнительный тест: Пин-код при закрытии ============
    def test_close_with_pin_code(self, client, test_context, mock_api, base_session_data):
        """
        Проверка закрытия сессии с вводом пин-кода (use_line_pin_code).
        """
        session_id = str(uuid.uuid4())

        if mock_api:
            # Первая попытка - требует пин-код
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/finish",
                json={
                    "id": session_id,
                    "status": "pin_required",
                    "message": "Требуется ввод пин-кода для закрытия сессии"
                },
                status=200,
            )
            # Вторая попытка с пин-кодом - успех
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/aggregation_session/finish",
                json={
                    "id": session_id,
                    "status": "finished",
                    "pin_verified": True
                },
                status=200,
            )

        # Первая попытка без пин-кода
        resp = client.post(
            "/api/web/v1/aggregation_session/finish",
            json={"id": session_id}
        )
        assert resp.status_code == 200
        data = resp.json()

        # Если требуется пин - отправляем с пином
        if data.get("status") == "pin_required":
            resp = client.post(
                "/api/web/v1/aggregation_session/finish",
                json={
                    "id": session_id,
                    "pin_code": "1234"
                }
            )
            assert resp.status_code == 200
            data = resp.json()

        assert data["status"] == "finished"
        print(f"[E2E-PIN] Сессия закрыта с пин-кодом")
