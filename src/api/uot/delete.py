from src.utils.http import APIClient
import requests
from src.models import DeleteUot

def delete(client: APIClient, body: DeleteUot | dict | None = None, **kwargs) -> requests.Response:
    """
        Delete

        

        Endpoint: /api/web/v1/uot/delete
        Method: POST

        Parameters:
        - inn (string) (required): 
        """
    endpoint = "/api/web/v1/uot/delete"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)