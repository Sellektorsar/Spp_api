"""
API для фильтрации разрешений пользователей
"""

from typing import Any, Optional
from src.utils.http import APIClient


def filter(client: APIClient, json: Optional[dict] = None) -> Any:
    """
    Фильтрация разрешений/прав пользователей
    
    Args:
        client: HTTP клиент
        json: Фильтры для поиска разрешений
            - user_id: ID пользователя
            - role_id: ID роли
            - permission_type: тип разрешения
            - resource: ресурс
    
    Returns:
        Ответ сервера со списком разрешений
    """
    return client.post('/api/web/v1/permissions/filter', json=json or {})


def get_by_user(client: APIClient, user_id: str) -> Any:
    """
    Получение разрешений пользователя
    
    Args:
        client: HTTP клиент
        user_id: ID пользователя
    
    Returns:
        Ответ сервера с разрешениями пользователя
    """
    return client.get(f'/api/web/v1/users/{user_id}/permissions')


def get_by_role(client: APIClient, role_id: str) -> Any:
    """
    Получение разрешений роли
    
    Args:
        client: HTTP клиент
        role_id: ID роли
    
    Returns:
        Ответ сервера с разрешениями роли
    """
    return client.get(f'/api/web/v1/roles/{role_id}/permissions')
