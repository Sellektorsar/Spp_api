from src.utils.http import APIClient
import requests
from src.models import DeleteGtin

def delete(client: APIClient, body: DeleteGtin | dict | None = None, **kwargs) -> requests.Response:
    """
        Edit

        Удалить записи в реестр.

        Endpoint: /api/web/v1/gtin/delete
        Method: POST

        Parameters:
        - gtin (string) (required): 
        """
    endpoint = "/api/web/v1/gtin/delete"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)