from src.utils.http import APIClient
import requests
from src.models import ShipmentFilterInput

def filter(client: APIClient, body: ShipmentFilterInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Filter Data

        Фильтрация по отгрузки.

        Endpoint: /api/web/v1/shipment/filter
        Method: POST

        Parameters:
        - skip (integer): 
        - limit (integer): 
        - shipment_id (string): 
        - start_date (string): 
        - end_date (string): 
        - line_number (integer): 
        - is_active (boolean): 
        - gtin (string): 
        - product_name (string): 
        - is_send_circulation (boolean): 
        - read_type (api__web__v1__shipment__models__READ_TYPE): 
        - is_send_report (boolean): 
        """
    endpoint = "/api/web/v1/shipment/filter"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)