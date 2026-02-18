from src.utils.http import APIClient
import requests
from src.models import CreateDash

def create(client: APIClient, body: CreateDash | dict | None = None, **kwargs) -> requests.Response:
    """
        Create Agg Dashboard

        Создание дашборда.

        Endpoint: /api/web/v1/aggregation_session/dashboard/create
        Method: POST

        Parameters:
        - name (string) (required): 
        - hide_inactive_lines (boolean): 
        - line_numbers (array): 
        """
    endpoint = "/api/web/v1/aggregation_session/dashboard/create"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)