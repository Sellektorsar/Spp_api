from src.utils.http import APIClient
import requests
from src.models import SSHKey

def add(client: APIClient, body: SSHKey | dict | None = None, **kwargs) -> requests.Response:
    """
        Ssh Key Add

        

        Endpoint: /api/web/v1/application/ssh_key/add
        Method: POST

        Parameters:
        - public_ssh_key (string) (required): 
        """
    endpoint = "/api/web/v1/application/ssh_key/add"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)