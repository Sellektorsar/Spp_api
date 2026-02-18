from src.utils.http import APIClient
import requests
from src.models import AggSessionVisionAddCodes

def add_codes(client: APIClient, body: AggSessionVisionAddCodes | dict | None = None, **kwargs) -> requests.Response:
    """
        Vision Add Codes

        Добавление км для тех. зрения.

        Endpoint: /api/web/v1/aggregation_session/vision/add_codes
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - codes (array) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/vision/add_codes"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)