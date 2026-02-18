from src.utils.http import APIClient
import requests
from src.models import UserId

def get(client: APIClient, body: UserId | dict | None = None, **kwargs) -> requests.Response:
    """
        Get User Permissions

        

        Endpoint: /api/web/v1/user/permissions/get
        Method: POST

        Parameters:
        - id (string) (required): 
        """
    endpoint = "/api/web/v1/user/permissions/get"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)