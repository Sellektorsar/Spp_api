from src.utils.http import APIClient
import requests
from src.models import AggSessionFinishDelete

def delete(client: APIClient, body: AggSessionFinishDelete | dict | None = None, **kwargs) -> requests.Response:
    """
        Pallets Delete

        Удалить сессию.

        Endpoint: /api/web/v1/aggregation_session/pallets/delete
        Method: POST

        Parameters:
        - aggregation_session_id (string) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/pallets/delete"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)