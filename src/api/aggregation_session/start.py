from src.utils.http import APIClient
import requests
from src.models import PalletsAggSessionStartInput

def start(client: APIClient, body: PalletsAggSessionStartInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Pallets Start Session

        Начать сессию.

        Endpoint: /api/web/v1/aggregation_session/pallets/start
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - pallet_size (integer): 
        - start_date (string): 
        - read_type (api__web__v1__aggregation_session__models__READ_TYPE) (required): 
        - print_type (PRINT_TYPE) (required): 
        - product_group (ProductGroup): 
        """
    endpoint = "/api/web/v1/aggregation_session/pallets/start"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)