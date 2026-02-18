from src.utils.http import APIClient
import requests
from src.models import AggSessionActive

def active(client: APIClient, body: AggSessionActive | dict | None = None, **kwargs) -> requests.Response:
    """
        Pallets Get Active Session

        Получить id активной сессии

        Endpoint: /api/web/v1/aggregation_session/pallets/active
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/pallets/active"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)