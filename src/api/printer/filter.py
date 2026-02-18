from src.utils.http import APIClient
import requests
from src.models import LayoutFilterInput

def filter(client: APIClient, body: LayoutFilterInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Layout Filter

        Фильтрация по макетам.

        Endpoint: /api/web/v1/printer/layout/filter
        Method: POST

        Parameters:
        - skip (integer): 
        - limit (integer): 
        - print_type (PRINTER_PRINT_TYPE): 
        - is_favorite (boolean): 
        """
    endpoint = "/api/web/v1/printer/layout/filter"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)