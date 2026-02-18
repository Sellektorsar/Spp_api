from src.utils.http import APIClient
import requests
from src.models import LicenseFilterInput

def filter(client: APIClient, body: LicenseFilterInput | dict | None = None, **kwargs) -> requests.Response:
    """
        License Filter

        Фильтрация по лицензиям.

        Endpoint: /api/web/v1/license/filter
        Method: POST

        Parameters:
        - skip (integer): 
        - limit (integer): 
        """
    endpoint = "/api/web/v1/license/filter"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)