from src.utils.http import APIClient
import requests
from src.models import ShipmentID

def resume(client: APIClient, body: ShipmentID | dict | None = None, **kwargs) -> requests.Response:
    """
        Resume

        Возобновить отгрузку.

        Endpoint: /api/web/v1/shipment/resume
        Method: POST

        Parameters:
        - shipment_id (string) (required): 
        """
    endpoint = "/api/web/v1/shipment/resume"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)