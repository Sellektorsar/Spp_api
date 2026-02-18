from src.utils.http import APIClient
import requests
from src.models import DeleteSetInput

def delete(client: APIClient, body: DeleteSetInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Delete Set

        

        Endpoint: /api/web/v1/set/delete
        Method: POST

        Parameters:
        - set_gtin (string) (required): 
        """
    endpoint = "/api/web/v1/set/delete"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)