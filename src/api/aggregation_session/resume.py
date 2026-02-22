"""
API для возобновления прерванной сессии агрегации
"""

from typing import Any
from src.utils.http import APIClient


def resume(client: APIClient, json: dict) -> Any:
    """
    Возобновление прерванной сессии агрегации
    
    Args:
        client: HTTP клиент
        json: Данные для возобновления
            - session_id: ID сессии
            - line_number: номер линии
    
    Returns:
        Ответ сервера
    """
    return client.post('/api/web/v1/aggregation_session/resume', json=json)


def pause(client: APIClient, json: dict) -> Any:
    """
    Приостановка сессии агрегации
    
    Args:
        client: HTTP клиент
        json: Данные для приостановки
            - session_id: ID сессии
            - line_number: номер линии
            - reason: причина приостановки
    
    Returns:
        Ответ сервера
    """
    return client.post('/api/web/v1/aggregation_session/pause', json=json)
