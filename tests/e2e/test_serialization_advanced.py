"""
E2E Сценарии: Расширенная функциональность сериализации.
Покрывает: переменный вес, ввод диапазонами, брак, отмены, возобновление.
"""
import uuid
import responses


class TestSerializationAdvanced:
    """
    E2E Сценарии: Сложные режимы ввода КМ в производственную партию.
    """

    def test_01_start_shift_with_variable_weight(self, client, test_context, mock_api):
        """Шаг 1: Запуск смены с параметром переменного веса (Case 15)."""
        line_number = 1
        shift_id = str(uuid.uuid4())
        test_context.add("adv_shift_id", shift_id)

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/start",
                json={
                    "id": shift_id,
                    "line_number": line_number,
                    "status": "started",
                    "variable_weight": True
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/work_shift/start",
            json={
                "line_number": line_number,
                "name": "Shift Variable Weight",
                "variable_weight": True
            }
        )
        assert resp.status_code == 200
        print(f"[E2E-SER-ADV] Смена с перем. весом запущена: {shift_id}")

    def test_02_add_code_with_weight(self, client, test_context, mock_api):
        """Шаг 2: Добавление КМ с весом (для молочной продукции)."""
        line_number = 1
        code = "0104600494009044215FwVw=="
        weight = 0.950

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/add_code",
                json={
                    "status": "ok",
                    "code": code,
                    "weight": weight
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/work_shift/add_code",
            json={
                "line_number": line_number,
                "code": code,
                "weight": weight
            }
        )
        assert resp.status_code == 200
        print(f"[E2E-SER-ADV] КМ с весом {weight} кг добавлен")

    def test_03_fill_aggregate_mode(self, client, test_context, mock_api):
        """Шаг 3: Наполнение партии режимом 'Агрегат' (Case 17)."""
        line_number = 1
        roll_code = "01004600494009044421rollAgg93dGVzdA=="

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/add_roll",
                json={"status": "ok", "added_count": 100, "mode": "aggregate"},
                status=200,
            )

        resp = client.post(
            "/api/web/v1/work_shift/add_roll",
            json={"line_number": line_number, "roll_code": roll_code}
        )
        assert resp.status_code == 200
        print(f"[E2E-SER-ADV] Ролик добавлен в партию (режим Агрегат)")

    def test_04_range_add_start_code(self, client, test_context, mock_api):
        """Шаг 4: Начало диапазона (Case 18)."""
        line_number = 1
        start_code = "01004600494009044421start00193dGVzdA=="

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/range/add_start_code",
                json={
                    "status": "start_added",
                    "start_code": start_code,
                    "range_locked": True
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/work_shift/range/add_start_code",
            json={"line_number": line_number, "code": start_code}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("range_locked") is True
        test_context.add("range_start_code", start_code)
        print(f"[E2E-SER-ADV] Начало диапазона добавлено")

    def test_05_range_add_finish_code(self, client, test_context, mock_api):
        """Шаг 5: Окончание диапазона (Case 18)."""
        line_number = 1
        finish_code = "01004600494009044421finish0993dGVzdA=="

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/range/add_finish_code",
                json={
                    "status": "range_finished",
                    "count": 10,
                    "start_code": test_context.get_last("range_start_code"),
                    "finish_code": finish_code
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/work_shift/range/add_finish_code",
            json={"line_number": line_number, "code": finish_code}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("count") == 10
        print(f"[E2E-SER-ADV] Диапазон завершен, добавлено {data.get('count')} КМ")

    def test_06_cancel_start_code(self, client, test_context, mock_api):
        """Шаг 6: Отмена начального кода диапазона."""
        line_number = 1
        start_code = test_context.get_last("range_start_code")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/range/cancel_start_code",
                json={
                    "status": "canceled",
                    "start_code": start_code,
                    "range_unlocked": True
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/work_shift/range/cancel_start_code",
            json={"line_number": line_number, "code": start_code}
        )
        assert resp.status_code == 200
        print(f"[E2E-SER-ADV] Начальный код диапазона отменен")

    def test_07_defect_single_code(self, client, test_context, mock_api):
        """Шаг 7: Удаление брака поштучно (Case 24)."""
        line_number = 1
        defect_code = "01004600494009044421defect00193dGVzdA=="

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/defect/add",
                json={
                    "status": "defect_added",
                    "defect_code": defect_code,
                    "defect_count": 1
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/work_shift/defect/add",
            json={
                "line_number": line_number,
                "code": defect_code,
                "reason": "print_quality_issue"
            }
        )
        assert resp.status_code == 200
        print(f"[E2E-SER-ADV] Брак добавлен: {defect_code}")

    def test_08_defect_range(self, client, test_context, mock_api):
        """Шаг 8: Удаление брака в режиме 'Диапазон' (Case 23)."""
        line_number = 1
        defect_start = "01004600494009044421defect001"
        defect_finish = "01004600494009044421defect005"

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/defect/add_range",
                json={
                    "status": "defects_added",
                    "count": 5,
                    "start_code": defect_start,
                    "finish_code": defect_finish
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/work_shift/defect/add_range",
            json={
                "line_number": line_number,
                "start_code": defect_start,
                "finish_code": defect_finish,
                "reason": "damaged"
            }
        )
        assert resp.status_code == 200
        print(f"[E2E-SER-ADV] Брак по диапазону удален: 5 КМ")

    def test_09_cancel_code_by_roll(self, client, test_context, mock_api):
        """Шаг 9: Отмена КМ по ролику (Case 20)."""
        line_number = 1
        roll_code = "01004600494009044421cancelRoll93dGVzdA=="

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/cancel/codes_by_roll",
                json={
                    "status": "canceled",
                    "roll_code": roll_code,
                    "canceled_count": 50
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/work_shift/cancel/codes_by_roll",
            json={"line_number": line_number, "roll_code": roll_code}
        )
        assert resp.status_code == 200
        print(f"[E2E-SER-ADV] КМ по ролику отменены")

    def test_10_cancel_range(self, client, test_context, mock_api):
        """Шаг 10: Отмена КМ по диапазону (Case 21)."""
        line_number = 1
        cancel_start = "01004600494009044421canc001"
        cancel_finish = "01004600494009044421canc010"

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/cancel/codes_range",
                json={
                    "status": "canceled",
                    "count": 10,
                    "start_code": cancel_start,
                    "finish_code": cancel_finish
                },
                status=200,
            )

        resp = client.post(
            "/api/web/v1/work_shift/cancel/codes_range",
            json={
                "line_number": line_number,
                "start_code": cancel_start,
                "finish_code": cancel_finish
            }
        )
        assert resp.status_code == 200
        print(f"[E2E-SER-ADV] КМ по диапазону отменены: 10 шт.")

    def test_11_finish_shift(self, client, test_context, mock_api):
        """Шаг 11: Завершение смены (Case 25)."""
        shift_id = test_context.get_last("adv_shift_id")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/finish",
                json={"id": shift_id, "status": "finished"},
                status=200,
            )

        resp = client.post(
            "/api/web/v1/work_shift/finish",
            json={"id": shift_id}
        )
        assert resp.status_code == 200
        print(f"[E2E-SER-ADV] Смена завершена: {shift_id}")

    def test_12_resume_shift(self, client, test_context, mock_api):
        """Шаг 12: Возобновление партии (Case 26)."""
        shift_id = test_context.get_last("adv_shift_id")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/resume",
                json={"id": shift_id, "status": "resumed"},
                status=200,
            )

        resp = client.post(
            "/api/web/v1/work_shift/resume",
            json={"id": shift_id}
        )
        assert resp.status_code == 200
        print(f"[E2E-SER-ADV] Партия возобновлена: {shift_id}")

    def test_13_finish_shift_again(self, client, test_context, mock_api):
        """Шаг 13: Повторное завершение смены."""
        shift_id = test_context.get_last("adv_shift_id")

        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/work_shift/finish",
                json={"id": shift_id, "status": "finished"},
                status=200,
            )

        resp = client.post(
            "/api/web/v1/work_shift/finish",
            json={"id": shift_id}
        )
        assert resp.status_code == 200
        print(f"[E2E-SER-ADV] Смена повторно завершена: {shift_id}")
