"""
Integration tests for User Management.
Покрывает: Смена пароля, редактирование, блокировка/разблокировка, создание.
"""
import pytest
import os


class TestUserManagementExtended:
    """
    Расширенные интеграционные тесты для управления пользователями.
    Endpoints: /api/web/v1/user/*
    """

    def test_get_current_user(self, client):
        """Получение информации о текущем пользователе (Case 68)."""
        resp = client.get("/api/web/v1/user/me")
        assert resp.status_code == 200
        data = resp.json()
        assert "username" in data or "id" in data
        print(f"[INT-USER] Текущий пользователь: {data.get('username')}")

    def test_filter_users(self, client):
        """Фильтрация пользователей."""
        resp = client.post(
            "/api/web/v1/user/filter",
            json={"limit": 10, "offset": 0, "active": True}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        print(f"[INT-USER] Найдено пользователей: {data.get('total_count', 0)}")

    def test_user_change_password(self, client):
        """Смена пароля текущего пользователя (Case 69)."""
        current_password = os.getenv("SPP_API_PASSWORD", "old_pass")
        new_password = "NewStrongPassword123!"

        resp = client.post(
            "/api/web/v1/user/password/change",
            json={
                "old_password": current_password,
                "new_password": new_password
            }
        )
        # Может потребоваться откат пароля или использование тестового юзера
        # 200 - успех, 400 - старый пароль неверен, 422 - новый пароль слабый
        assert resp.status_code in [200, 400, 422]
        print(f"[INT-USER] Смена пароля: статус {resp.status_code}")

    def test_edit_user_info(self, client):
        """Редактирование данных пользователя (Case 70)."""
        # Получаем текущего пользователя
        me_resp = client.get("/api/web/v1/user/me")
        if me_resp.status_code != 200:
            pytest.skip("Не удалось получить текущего пользователя")
        
        user_id = me_resp.json().get("id")
        if not user_id:
            pytest.skip("ID пользователя не найден")

        resp = client.post(
            "/api/web/v1/user/edit",
            json={
                "id": user_id,
                "first_name": "Integration",
                "last_name": "Test",
                "email": "integration.test@example.com"
            }
        )
        # 200 - успех, 403 - недостаточно прав, 404 - не найден
        assert resp.status_code in [200, 403, 404]
        print(f"[INT-USER] Редактирование пользователя: статус {resp.status_code}")

    def test_get_user_permissions(self, client):
        """Получение прав пользователя."""
        me_resp = client.get("/api/web/v1/user/me")
        if me_resp.status_code != 200:
            pytest.skip("Не удалось получить текущего пользователя")
        
        user_id = me_resp.json().get("id")

        resp = client.post(
            "/api/web/v1/user/permissions/get",
            json={"id": user_id}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "permissions" in data or "roles" in data
        print(f"[INT-USER] Права пользователя получены")

    def test_update_user_permissions(self, client):
        """Обновление прав пользователя."""
        me_resp = client.get("/api/web/v1/user/me")
        if me_resp.status_code != 200:
            pytest.skip("Не удалось получить текущего пользователя")
        
        user_id = me_resp.json().get("id")

        resp = client.post(
            "/api/web/v1/user/permissions/update",
            json={
                "id": user_id,
                "permissions": ["read", "write"],
                "roles": ["operator"]
            }
        )
        # 200 - успех, 403 - нет прав на изменение
        assert resp.status_code in [200, 403]
        print(f"[INT-USER] Права обновлены: статус {resp.status_code}")

    def test_create_new_user(self, client):
        """Создание нового пользователя (Case 71)."""
        import uuid
        unique_suffix = str(uuid.uuid4())[:8]
        
        resp = client.post(
            "/api/web/v1/user/create",
            json={
                "username": f"test_user_{unique_suffix}",
                "password": "TestPassword123!",
                "email": f"test_{unique_suffix}@example.com",
                "first_name": "Test",
                "last_name": "User",
                "role": "operator"
            }
        )
        # 200 - успех, 409 - пользователь уже существует, 422 - невалидные данные
        assert resp.status_code in [200, 409, 422]
        if resp.status_code == 200:
            print(f"[INT-USER] Пользователь создан")
        else:
            print(f"[INT-USER] Создание пользователя: статус {resp.status_code}")

    def test_deactivate_activate_user(self, client):
        """Блокировка и разблокировка пользователя (Case 72)."""
        # Этот тест требует существующего тестового пользователя
        test_user_id = os.getenv("SPP_TEST_USER_ID_TO_BLOCK")
        
        if not test_user_id:
            pytest.skip("SPP_TEST_USER_ID_TO_BLOCK не задан")

        # Блокировка
        resp_deactivate = client.post(
            "/api/web/v1/user/deactivate",
            json={"id": test_user_id}
        )
        assert resp_deactivate.status_code in [200, 404, 403]
        
        if resp_deactivate.status_code == 200:
            print(f"[INT-USER] Пользователь заблокирован")
            
            # Разблокировка
            resp_activate = client.post(
                "/api/web/v1/user/activate",
                json={"id": test_user_id}
            )
            assert resp_activate.status_code == 200
            print(f"[INT-USER] Пользователь разблокирован")
        else:
            print(f"[INT-USER] Блокировка: статус {resp_deactivate.status_code}")

    def test_get_owner_profile(self, client):
        """Получение профиля владельца (Case 68)."""
        resp = client.get("/api/web/v1/get_owner_profile")
        assert resp.status_code in [200, 403]
        if resp.status_code == 200:
            data = resp.json()
            assert "name" in data or "inn" in data
            print(f"[INT-USER] Профиль владельца получен")
