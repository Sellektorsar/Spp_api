from src.utils.http import APIClient
import requests

def filter(client: APIClient, body: dict | None = None, **kwargs) -> requests.Response:
    """
        Filter Data

        Фильтрация по устройствам.

        Endpoint: /api/web/v1/devices/filter
        Method: POST

        Parameters:
        - skip (integer): 
        - limit (integer): 
        - mob_device_id (string): 
        - device_id (string): 
        - is_active (boolean): 
        - type (DEVICE_TYPE): 
        - start_last_active_date (string): 
        - end_last_active_date (string): 
        """
    endpoint = "/api/web/v1/devices/filter"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)