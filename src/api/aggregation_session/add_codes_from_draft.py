from src.utils.http import APIClient
import requests
from src.models import AggSessionVisionAddCode

def add_codes_from_draft(client: APIClient, body: AggSessionVisionAddCode | dict | None = None, **kwargs) -> requests.Response:
    """
        Vision Add Codes From Draft

        

        Endpoint: /api/web/v1/aggregation_session/vision/add_codes_from_draft
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - code (string) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/vision/add_codes_from_draft"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)