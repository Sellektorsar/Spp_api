from src.utils.http import APIClient
import requests
from src.models import PalletsAggSessionAddPallet

def add_pallet(client: APIClient, body: PalletsAggSessionAddPallet | dict | None = None, **kwargs) -> requests.Response:
    """
        Pallets Add Pallets

        Добавить палету.

        Endpoint: /api/web/v1/aggregation_session/pallets/add_pallet
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - package_code (any) (required): 
        - pallet_code (string) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/pallets/add_pallet"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)