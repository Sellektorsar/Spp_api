from src.utils.http import APIClient
import requests
from src.models import AuthDevice

def auth(client: APIClient, body: AuthDevice | dict | None = None, **kwargs) -> requests.Response:
    """
        Auth

        Авторизация для устройств

        Endpoint: /api/web/v1/devices/auth
        Method: POST

        Parameters:
        - token (string) (required): 
        """
    endpoint = "/api/web/v1/devices/auth"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)