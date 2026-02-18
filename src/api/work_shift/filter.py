from src.utils.http import APIClient
import requests
from src.models import WorkShiftFilterInput

def filter(client: APIClient, body: WorkShiftFilterInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Filter Data

        Фильтрация по производственным партиям.

        Endpoint: /api/web/v1/work_shift/filter
        Method: POST

        Parameters:
        - skip (integer): 
        - limit (integer): 
        - id (string): 
        - start_date (string): 
        - end_date (string): 
        - line_number (integer): 
        - is_active (boolean): 
        - is_send_report (boolean): 
        - gtin (string): 
        """
    endpoint = "/api/web/v1/work_shift/filter"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)