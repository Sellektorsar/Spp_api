"""
API для интеграции рабочей смены с внешними системами (1C)
"""

from typing import Any
from src.utils.http import APIClient


def update_work_shift_integration(client: APIClient, json: dict) -> Any:
    """
    Обновление настроек интеграции рабочей смены с 1С
    
    Args:
        client: HTTP клиент
        json: Данные для интеграции
            - line_number: номер линии
            - integration_enabled: включена ли интеграция
            - integration_type: тип интеграции (e.g., '1c')
            - settings: дополнительные настройки
    
    Returns:
        Ответ сервера
    """
    return client.post('/api/web/v1/work_shift/integration/update', json=json)


def get_work_shift_integration(client: APIClient, line_number: str) -> Any:
    """
    Получение настроек интеграции рабочей смены
    
    Args:
        client: HTTP клиент
        line_number: номер линии
    
    Returns:
        Ответ сервера с настройками интеграции
    """
    return client.get(f'/api/web/v1/work_shift/integration/get?line_number={line_number}')


def sync_with_1c(client: APIClient, line_number: str) -> Any:
    """
    Синхронизация данных с 1С
    
    Args:
        client: HTTP клиент
        line_number: номер линии
    
    Returns:
        Ответ сервера со статусом синхронизации
    """
    return client.post('/api/web/v1/work_shift/integration/sync', json={'line_number': line_number})
