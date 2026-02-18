from src.utils.http import APIClient
import requests
from src.models import CheckPalletCode

def check_pallet_code(client: APIClient, body: CheckPalletCode | dict | None = None, **kwargs) -> requests.Response:
    """
        Pallets Check Pallet Code

        Проверить палету в БД

        Endpoint: /api/web/v1/aggregation_session/pallets/check_pallet_code
        Method: POST

        Parameters:
        - pallet_code (string) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/pallets/check_pallet_code"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)