from src.utils.http import APIClient
import requests
from src.models import AggSessionInput

def detail(client: APIClient, body: AggSessionInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Hierarchy Detail

        Получить иерархию вложенности в сессии.

        Endpoint: /api/web/v1/aggregation_session/hierarchy/detail
        Method: POST

        Parameters:
        - id_agg_session (string) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/hierarchy/detail"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)