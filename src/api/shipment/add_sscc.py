from src.utils.http import APIClient
import requests
from src.models import ShipmentAddPackage

def add_sscc(client: APIClient, body: ShipmentAddPackage | dict | None = None, **kwargs) -> requests.Response:
    """
        Add Sscc

        Добавить агрегат, собранный ранее в агрегационной сессии

        Endpoint: /api/web/v1/shipment/add_sscc
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - sscc_code (any) (required): 
        - is_forced (boolean): 
        """
    endpoint = "/api/web/v1/shipment/add_sscc"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)