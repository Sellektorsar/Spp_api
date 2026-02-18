from src.utils.http import APIClient
import requests
from src.models import SSHKey

def remove(client: APIClient, body: SSHKey | dict | None = None, **kwargs) -> requests.Response:
    """
        Ssh Key Remove

        

        Endpoint: /api/web/v1/application/ssh_key/remove
        Method: POST

        Parameters:
        - public_ssh_key (string) (required): 
        """
    endpoint = "/api/web/v1/application/ssh_key/remove"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)