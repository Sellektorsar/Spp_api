"""
API для работы с бракованными кодами в смене
"""

from typing import Any
from src.utils.http import APIClient


def add_defect(client: APIClient, json: dict) -> Any:
    """
    Добавление бракованного кода
    
    Args:
        client: HTTP клиент
        json: Данные с кодом брака
            - line_number: номер линии
            - code: код
            - reason: причина брака
    
    Returns:
        Ответ сервера
    """
    return client.post('/api/web/v1/work_shift/defect/add', json=json)


def remove_defect(client: APIClient, json: dict) -> Any:
    """
    Удаление бракованного кода
    
    Args:
        client: HTTP клиент
        json: Данные с кодом для удаления
            - line_number: номер линии
            - code: код
    
    Returns:
        Ответ сервера
    """
    return client.post('/api/web/v1/work_shift/defect/remove', json=json)


def list_defects(client: APIClient, line_number: str) -> Any:
    """
    Получение списка бракованных кодов
    
    Args:
        client: HTTP клиент
        line_number: номер линии
    
    Returns:
        Ответ сервера со списком бракованных кодов
    """
    return client.get(f'/api/web/v1/work_shift/defect/list?line_number={line_number}')


def get_defect_stats(client: APIClient, line_number: str) -> Any:
    """
    Получение статистики по бракованным кодам
    
    Args:
        client: HTTP клиент
        line_number: номер линии
    
    Returns:
        Ответ сервера со статистикой
    """
    return client.get(f'/api/web/v1/work_shift/defect/stats?line_number={line_number}')
