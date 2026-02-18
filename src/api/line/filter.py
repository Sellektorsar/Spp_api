from src.utils.http import APIClient
import requests
from src.models import LineFilterInput

def filter(client: APIClient, body: LineFilterInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Filter Data

        Фильтрация по рабочим линиям.

        Endpoint: /api/web/v1/line/filter
        Method: POST

        Parameters:
        - skip (integer): 
        - limit (integer): 
        - line_type (array): 
        - production_type (ProductionType): 
        - line_number (integer): 
        - name (string): 
        - is_deleted (boolean): 
        """
    endpoint = "/api/web/v1/line/filter"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)