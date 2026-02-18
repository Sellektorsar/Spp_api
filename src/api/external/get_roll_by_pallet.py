from src.utils.http import APIClient
import requests
from src.models import ExternalGetRollInput

def get_roll_by_pallet(client: APIClient, body: ExternalGetRollInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Get Roll By Pallet

        

        Endpoint: /api/web/v1/external/warehouse/get_roll_by_pallet
        Method: POST

        Parameters:
        - pallet_id (string) (required): Идентификатор палеты
        """
    endpoint = "/api/web/v1/external/warehouse/get_roll_by_pallet"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)