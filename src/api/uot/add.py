from src.utils.http import APIClient
import requests
from src.models import UOT

def add(client: APIClient, body: UOT | dict | None = None, **kwargs) -> requests.Response:
    """
        Add

        Добавление

        Endpoint: /api/web/v1/uot/add
        Method: POST

        Parameters:
        - inn (string) (required): 
        - org_full_name (string): 
        - issuer_id (string): 
        - organization_code (string) (required): 
        """
    endpoint = "/api/web/v1/uot/add"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)