from src.utils.http import APIClient
import requests
from src.models import BlockDevice

def block(client: APIClient, body: BlockDevice | dict | None = None, **kwargs) -> requests.Response:
    """
        Block

        Блокировка устройства

        Endpoint: /api/web/v1/devices/block
        Method: POST

        Parameters:
        - device_id (string) (required): 
        """
    endpoint = "/api/web/v1/devices/block"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)