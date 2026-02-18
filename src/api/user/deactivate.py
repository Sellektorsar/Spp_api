from src.utils.http import APIClient
import requests
from src.models import UserId

def deactivate(client: APIClient, body: UserId | dict | None = None, **kwargs) -> requests.Response:
    """
        Deactivate User

        

        Endpoint: /api/web/v1/user/deactivate
        Method: POST

        Parameters:
        - id (string) (required): 
        """
    endpoint = "/api/web/v1/user/deactivate"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)