from src.utils.http import APIClient
import requests
from src.models import DeleteDevice

def delete(client: APIClient, body: DeleteDevice | dict | None = None, **kwargs) -> requests.Response:
    """
        Delete

        Удаление устройства

        Endpoint: /api/web/v1/devices/delete
        Method: POST

        Parameters:
        - device_id (string) (required): 
        """
    endpoint = "/api/web/v1/devices/delete"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)