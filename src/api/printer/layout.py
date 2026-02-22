"""
API для работы с макетами принтеров
"""

from typing import Any, Optional
from src.utils.http import APIClient


def filter_layouts(client: APIClient, json: Optional[dict] = None) -> Any:
    """
    Фильтрация макетов этикеток
    
    Args:
        client: HTTP клиент
        json: Фильтры для поиска макетов
            - is_favorite: фильтровать только избранные
            - name: фильтр по имени
            - offset: смещение
            - limit: лимит
    
    Returns:
        Ответ сервера со списком макетов
    """
    return client.post('/api/web/v1/printer/layout/filter', json=json or {})


def get_layout(client: APIClient, layout_id: str) -> Any:
    """
    Получение информации о макете
    
    Args:
        client: HTTP клиент
        layout_id: ID макета
    
    Returns:
        Ответ сервера с информацией о макете
    """
    return client.get(f'/api/web/v1/printer/layout/{layout_id}')


def update_layout(client: APIClient, layout_id: str, json: dict) -> Any:
    """
    Обновление макета
    
    Args:
        client: HTTP клиент
        layout_id: ID макета
        json: Данные для обновления
    
    Returns:
        Ответ сервера
    """
    return client.post(f'/api/web/v1/printer/layout/{layout_id}/update', json=json)


def delete_layout(client: APIClient, layout_id: str) -> Any:
    """
    Удаление макета
    
    Args:
        client: HTTP клиент
        layout_id: ID макета
    
    Returns:
        Ответ сервера
    """
    return client.post(f'/api/web/v1/printer/layout/{layout_id}/delete')
