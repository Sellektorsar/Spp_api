from src.utils.http import APIClient
import requests
from src.models import ShipmentActiveInput

def active(client: APIClient, body: ShipmentActiveInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Active Shipment

        Получить id активной отгрузки

        Endpoint: /api/web/v1/shipment/active
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        """
    endpoint = "/api/web/v1/shipment/active"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)