from src.utils.http import APIClient
import requests
from src.models import UotFilterInput

def filter(client: APIClient, body: UotFilterInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Add

        

        Endpoint: /api/web/v1/uot/filter
        Method: POST

        Parameters:
        - skip (integer): 
        - limit (integer): 
        - id (string): 
        - inn (integer): 
        - organization_code (string): 
        """
    endpoint = "/api/web/v1/uot/filter"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)