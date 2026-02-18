from src.utils.http import APIClient
import requests
from src.models import GetRoleInput

def get(client: APIClient, body: GetRoleInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Filter Data

        

        Endpoint: /api/web/v1/role/get
        Method: POST

        Parameters:
        - id (string) (required): 
        """
    endpoint = "/api/web/v1/role/get"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)