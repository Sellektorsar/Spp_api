from src.utils.http import APIClient
import requests
from src.models import NewDevice

def add(client: APIClient, body: NewDevice | dict | None = None, **kwargs) -> requests.Response:
    """
        Add

        Добавить устройство

        Endpoint: /api/web/v1/devices/add
        Method: POST

        Parameters:
        - mob_device_id (string) (required): 
        - name (string): 
        - type (any): 
        """
    endpoint = "/api/web/v1/devices/add"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)