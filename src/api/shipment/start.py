from src.utils.http import APIClient
import requests
from src.models import ShipmentStartInput

def start(client: APIClient, body: ShipmentStartInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Start

        Начать отгрузку.

        Endpoint: /api/web/v1/shipment/start
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - name (string): 
        - start_date (string): 
        - read_type (api__web__v1__shipment__models__READ_TYPE) (required): 
        - product_group (ProductGroup): 
        - local_start_date (string): 
        """
    endpoint = "/api/web/v1/shipment/start"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)