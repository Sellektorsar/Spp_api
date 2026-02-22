"""
E2E Tests: User Management
Сценарий: управление пользователями и ролями доступа.

Шаги:
1. Создание пользователя с базовой ролью
2. Назначение расширенных прав
3. Проверка доступа к различным функциям
4. Изменение роли пользователя
5. Деактивация пользователя
6. Удаление пользователя
"""
import pytest
import responses
import uuid
import datetime
from typing import Dict, Any

from src.api.user.create import create as create_user
from src.api.user.filter import filter as filter_users
from src.api.user.get import get as get_user
from src.api.user.edit import edit as edit_user
from src.api.user.activate import activate as activate_user
from src.api.user.deactivate import deactivate as deactivate_user
from src.api.user.update import update as update_user
from src.api.user.me import me as get_current_user
from src.api.permissions.filter import filter as get_user_permissions
from src.api.role.get import get as update_user_permissions
from src.api.role.filter import filter as filter_roles
from src.api.role.get import get as get_role
from src.models import UserToCreate, UserFilterInput, UserEditInput, UserUpdateInput


@pytest.mark.e2e
@pytest.mark.order(5)
class TestUserManagement:
    """
    E2E Сценарий: Полный цикл управления пользователями и ролями.
    """

    def test_01_get_available_roles(self, client, test_context, mock_api):
        """Шаг 1: Получение списка доступных ролей."""
        role_id = str(uuid.uuid4())
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/role/filter",
                json={
                    "total_count": 3,
                    "result": [
                        {"id": role_id, "name": "Operator", "description": "Basic operator role"},
                        {"id": str(uuid.uuid4()), "name": "Admin", "description": "Administrator role"},
                        {"id": str(uuid.uuid4()), "name": "Manager", "description": "Manager role"},
                    ]
                },
                status=200,
            )

        resp = filter_roles(client, json={"limit": 10, "offset": 0})
        assert resp.status_code == 200
        data = resp.json()
        assert "result" in data
        assert data["total_count"] >= 1
        
        # Сохраняем ID первой роли для использования в следующих тестах
        if data["result"]:
            test_context.add("role_id", data["result"][0]["id"])
            test_context.add("role_name", data["result"][0]["name"])
            print(f"[E2E-USER] Найдено ролей: {data['total_count']}, первая роль: {data['result'][0]['name']}")

    def test_02_create_user_positive(self, client, test_context, mock_api):
        """Шаг 2: Позитивный сценарий создания пользователя."""
        role_id = test_context.get_last("role_id")
        assert role_id, "role_id от предыдущего шага отсутствует"
        
        user_id = str(uuid.uuid4())
        username = f"testuser_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/user/create",
                json={
                    "id": user_id,
                    "username": username,
                    "full_name": "Test User",
                    "is_active": True,
                    "role_id": role_id,
                    "job_title": "Test Operator"
                },
                status=200,
            )

        user_data = UserToCreate(
            username=username,
            full_name="Test User",
            password="SecurePassword123!",
            is_active=True,
            role_id=role_id,
            job_title="Test Operator"
        )
        
        resp = create_user(client, body=user_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["username"] == username
        assert data["is_active"] is True
        
        test_context.add("user_id", data["id"])
        test_context.add("username", username)
        print(f"[E2E-USER] Пользователь создан: {username} (ID: {data['id']})")

    def test_03_create_user_negative_duplicate_username(self, client, test_context, mock_api):
        """Шаг 3: Негативный сценарий - создание пользователя с дублирующим именем."""
        username = test_context.get_last("username")
        role_id = test_context.get_last("role_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/user/create",
                json={"detail": "Username already exists"},
                status=400,
            )

        user_data = UserToCreate(
            username=username,  # То же имя пользователя
            full_name="Duplicate User",
            password="SecurePassword123!",
            is_active=True,
            role_id=role_id,
            job_title="Duplicate Operator"
        )
        
        resp = create_user(client, body=user_data)
        assert resp.status_code == 400
        print(f"[E2E-USER] Проверка дублирования имени пользователя: статус {resp.status_code}")

    def test_04_create_user_negative_invalid_data(self, client, test_context, mock_api):
        """Шаг 4: Негативный сценарий - создание пользователя с невалидными данными."""
        role_id = test_context.get_last("role_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/user/create",
                json={"detail": "Validation error"},
                status=422,
            )

        # Пользователь с пустым именем (невалидные данные)
        user_data = UserToCreate(
            username="",  # Пустое имя
            full_name="Invalid User",
            password="SecurePassword123!",
            is_active=True,
            role_id=role_id,
            job_title="Invalid Operator"
        )
        
        resp = create_user(client, body=user_data)
        assert resp.status_code == 422
        print(f"[E2E-USER] Проверка валидации данных: статус {resp.status_code}")

    def test_05_filter_users(self, client, test_context, mock_api):
        """Шаг 5: Фильтрация пользователей."""
        username = test_context.get_last("username")
        user_id = test_context.get_last("user_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/user/filter",
                json={
                    "total_count": 1,
                    "result": [
                        {
                            "id": user_id,
                            "username": username,
                            "full_name": "Test User",
                            "is_active": True,
                            "job_title": "Test Operator"
                        }
                    ]
                },
                status=200,
            )

        filter_data = UserFilterInput(
            limit=10,
            offset=0,
            username=username
        )
        
        resp = filter_users(client, body=filter_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] >= 1
        
        # Проверяем, что наш пользователь есть в результатах
        found_user = next((u for u in data["result"] if u["username"] == username), None)
        assert found_user is not None
        print(f"[E2E-USER] Фильтрация пользователей: найдено {data['total_count']}")

    def test_06_get_user_details(self, client, test_context, mock_api):
        """Шаг 6: Получение детальной информации о пользователе."""
        user_id = test_context.get_last("user_id")
        username = test_context.get_last("username")
        
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/user/get",
                json={
                    "id": user_id,
                    "username": username,
                    "full_name": "Test User",
                    "is_active": True,
                    "job_title": "Test Operator",
                    "role_id": test_context.get_last("role_id"),
                    "registration_date": datetime.datetime.now().isoformat(),
                    "last_auth_date": None
                },
                status=200,
            )

        resp = get_user(client, params={"id": user_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == user_id
        assert data["username"] == username
        print(f"[E2E-USER] Детали пользователя получены: {username}")

    def test_07_get_user_permissions(self, client, test_context, mock_api):
        """Шаг 7: Получение прав пользователя."""
        user_id = test_context.get_last("user_id")
        
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/user/permissions/get",
                json={
                    "user_id": user_id,
                    "permissions": [
                        {"resource": "orders", "actions": ["read", "create"]},
                        {"resource": "reports", "actions": ["read"]},
                        {"resource": "warehouse", "actions": []}
                    ]
                },
                status=200,
            )

        resp = get_user_permissions(client, params={"user_id": user_id})
        assert resp.status_code == 200
        data = resp.json()
        assert "permissions" in data
        assert isinstance(data["permissions"], list)
        print(f"[E2E-USER] Права пользователя получены: {len(data['permissions'])} разрешений")

    def test_08_update_user_permissions(self, client, test_context, mock_api):
        """Шаг 8: Обновление прав пользователя."""
        user_id = test_context.get_last("user_id")
        
        new_permissions = [
            {"resource": "orders", "actions": ["read", "create", "update"]},
            {"resource": "reports", "actions": ["read", "create"]},
            {"resource": "warehouse", "actions": ["read", "update"]},
            {"resource": "users", "actions": ["read"]}
        ]
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/user/permissions/update",
                json={
                    "user_id": user_id,
                    "permissions": new_permissions,
                    "updated": True
                },
                status=200,
            )

        resp = update_user_permissions(client, json={"user_id": user_id, "permissions": new_permissions})
        assert resp.status_code == 200
        data = resp.json()
        assert data["updated"] is True
        test_context.add("updated_permissions", new_permissions)
        print(f"[E2E-USER] Права пользователя обновлены: {len(new_permissions)} разрешений")

    def test_09_edit_user_information(self, client, test_context, mock_api):
        """Шаг 9: Редактирование информации о пользователе."""
        user_id = test_context.get_last("user_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/user/edit",
                json={
                    "id": user_id,
                    "full_name": "Updated Test User",
                    "job_title": "Senior Test Operator",
                    "is_active": True
                },
                status=200,
            )

        edit_data = UserEditInput(
            id=user_id,
            full_name="Updated Test User",
            job_title="Senior Test Operator",
            is_active=True
        )
        
        resp = edit_user(client, body=edit_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["full_name"] == "Updated Test User"
        assert data["job_title"] == "Senior Test Operator"
        print(f"[E2E-USER] Информация о пользователе обновлена")

    def test_10_update_user_password(self, client, test_context, mock_api):
        """Шаг 10: Обновление пароля пользователя."""
        user_id = test_context.get_last("user_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/user/update",
                json={
                    "id": user_id,
                    "password_updated": True
                },
                status=200,
            )

        update_data = UserUpdateInput(
            id=user_id,
            password="NewSecurePassword456!"
        )
        
        resp = update_user(client, body=update_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["password_updated"] is True
        print(f"[E2E-USER] Пароль пользователя обновлен")

    def test_11_deactivate_user(self, client, test_context, mock_api):
        """Шаг 11: Деактивация пользователя."""
        user_id = test_context.get_last("user_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/user/deactivate",
                json={
                    "id": user_id,
                    "is_active": False,
                    "deactivated": True
                },
                status=200,
            )

        resp = deactivate_user(client, json={"id": user_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["deactivated"] is True
        print(f"[E2E-USER] Пользователь деактивирован")

    def test_12_verify_deactivated_user_access(self, client, test_context, mock_api):
        """Шаг 12: Проверка доступа деактивированного пользователя."""
        user_id = test_context.get_last("user_id")
        
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/user/get",
                json={"detail": "User is deactivated"},
                status=403,
            )

        resp = get_user(client, params={"id": user_id})
        assert resp.status_code == 403
        print(f"[E2E-USER] Доступ деактивированного пользователя ограничен")

    def test_13_reactivate_user(self, client, test_context, mock_api):
        """Шаг 13: Реактивация пользователя."""
        user_id = test_context.get_last("user_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/user/activate",
                json={
                    "id": user_id,
                    "is_active": True,
                    "activated": True
                },
                status=200,
            )

        resp = activate_user(client, json={"id": user_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["activated"] is True
        print(f"[E2E-USER] Пользователь реактивирован")

    def test_14_verify_reactivated_user_access(self, client, test_context, mock_api):
        """Шаг 14: Проверка доступа реактивированного пользователя."""
        user_id = test_context.get_last("user_id")
        username = test_context.get_last("username")
        
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/user/get",
                json={
                    "id": user_id,
                    "username": username,
                    "full_name": "Updated Test User",
                    "is_active": True,
                    "job_title": "Senior Test Operator"
                },
                status=200,
            )

        resp = get_user(client, params={"id": user_id})
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_active"] is True
        print(f"[E2E-USER] Доступ реактивированного пользователя восстановлен")

    def test_15_get_current_user_info(self, client, test_context, mock_api):
        """Шаг 15: Получение информации о текущем пользователе."""
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/user/me",
                json={
                    "id": str(uuid.uuid4()),
                    "username": "current_user",
                    "full_name": "Current User",
                    "is_active": True,
                    "job_title": "System Administrator",
                    "permissions": ["admin", "read", "write", "delete"]
                },
                status=200,
            )

        resp = get_current_user(client)
        assert resp.status_code == 200
        data = resp.json()
        assert "username" in data
        assert "permissions" in data
        print(f"[E2E-USER] Информация о текущем пользователе получена: {data['username']}")

    def test_16_boundary_test_max_users_per_page(self, client, test_context, mock_api):
        """Шаг 16: Граничный тест - максимальное количество пользователей на странице."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/user/filter",
                json={
                    "total_count": 100,
                    "result": [{"id": str(uuid.uuid4()), "username": f"user{i}", "is_active": True} for i in range(100)]
                },
                status=200,
            )

        # Запрос с максимальным лимитом
        filter_data = UserFilterInput(
            limit=100,  # Максимальный лимит
            offset=0
        )
        
        resp = filter_users(client, body=filter_data)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["result"]) <= 100
        print(f"[E2E-USER] Граничный тест: получено {len(data['result'])} пользователей")

    def test_17_boundary_test_empty_filter_results(self, client, test_context, mock_api):
        """Шаг 17: Граничный тест - пустые результаты фильтрации."""
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/user/filter",
                json={
                    "total_count": 0,
                    "result": []
                },
                status=200,
            )

        # Фильтр по несуществующему пользователю
        filter_data = UserFilterInput(
            limit=10,
            offset=0,
            username="nonexistent_user_12345"
        )
        
        resp = filter_users(client, body=filter_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_count"] == 0
        assert len(data["result"]) == 0
        print(f"[E2E-USER] Граничный тест: пустые результаты фильтрации")

    def test_18_error_test_invalid_user_id(self, client, test_context, mock_api):
        """Шаг 18: Тест обработки ошибок - невалидный ID пользователя."""
        if mock_api:
            mock_api.add(
                responses.GET,
                f"{client.base_url}/api/web/v1/user/get",
                json={"detail": "User not found"},
                status=404,
            )

        # Запрос с несуществующим ID
        invalid_id = "00000000-0000-0000-0000-000000000000"
        resp = get_user(client, params={"id": invalid_id})
        assert resp.status_code == 404
        print(f"[E2E-USER] Тест обработки ошибок: невалидный ID пользователя")

    def test_19_error_test_permission_denied(self, client, test_context, mock_api):
        """Шаг 19: Тест обработки ошибок - отказ в доступе."""
        user_id = test_context.get_last("user_id")
        
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/user/permissions/update",
                json={"detail": "Permission denied"},
                status=403,
            )

        # Попытка обновить права без необходимых привилегий
        new_permissions = [{"resource": "admin", "actions": ["all"]}]
        resp = update_user_permissions(client, json={"user_id": user_id, "permissions": new_permissions})
        assert resp.status_code == 403
        print(f"[E2E-USER] Тест обработки ошибок: отказ в доступе")

    def test_20_cleanup_test_user(self, client, test_context, mock_api):
        """Шаг 20: Очистка - удаление тестового пользователя."""
        user_id = test_context.get_last("user_id")
        
        # В API нет прямого метода удаления, поэтому деактивируем пользователя
        if mock_api:
            mock_api.add(
                responses.POST,
                f"{client.base_url}/api/web/v1/user/deactivate",
                json={
                    "id": user_id,
                    "is_active": False,
                    "deactivated": True
                },
                status=200,
            )

        resp = deactivate_user(client, json={"id": user_id})
        assert resp.status_code == 200
        print(f"[E2E-USER] Тестовый пользователь деактивирован для очистки")