from src.utils.http import APIClient
import requests
from src.models import PalletsAggSessionFilter

def filter(client: APIClient, body: PalletsAggSessionFilter | dict | None = None, **kwargs) -> requests.Response:
    """
        Pallets Filter Data

        Фильтрация по агрегационным сессиям.

        Endpoint: /api/web/v1/aggregation_session/pallets/filter
        Method: POST

        Parameters:
        - skip (integer): 
        - limit (integer): 
        - id_agg_session (string): 
        - start_date (string): 
        - end_date (string): 
        - line_number (integer): 
        - is_active (boolean): 
        - is_send_aggregation (boolean): 
        """
    endpoint = "/api/web/v1/aggregation_session/pallets/filter"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)