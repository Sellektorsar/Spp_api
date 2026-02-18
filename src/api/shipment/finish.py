from src.utils.http import APIClient
import requests
from src.models import ShipmentFinish

def finish(client: APIClient, body: ShipmentFinish | dict | None = None, **kwargs) -> requests.Response:
    """
        Finish

        Завершить отгрузку.

        Endpoint: /api/web/v1/shipment/finish
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - pin_code (string): 
        """
    endpoint = "/api/web/v1/shipment/finish"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)