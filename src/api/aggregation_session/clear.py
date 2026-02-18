from src.utils.http import APIClient
import requests
from src.models import AggSessionActive

def clear(client: APIClient, body: AggSessionActive | dict | None = None, **kwargs) -> requests.Response:
    """
        Vision Buffer Clear

        

        Endpoint: /api/web/v1/aggregation_session/vision/buffer/clear
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/vision/buffer/clear"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)