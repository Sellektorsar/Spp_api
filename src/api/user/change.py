from src.utils.http import APIClient
import requests
from src.models import ChangePasswordInput

def change(client: APIClient, body: ChangePasswordInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Change Password

        

        Endpoint: /api/web/v1/user/password/change
        Method: POST

        Parameters:
        - id (string) (required): 
        - password (string) (required): 
        """
    endpoint = "/api/web/v1/user/password/change"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)