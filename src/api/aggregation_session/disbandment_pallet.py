from src.utils.http import APIClient
import requests
from src.models import DisbandmentPalletInput

def disbandment_pallet(client: APIClient, body: DisbandmentPalletInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Disbandment Pallet

        Расформировать палету.

        Endpoint: /api/web/v1/aggregation_session/disbandment_pallet
        Method: POST

        Parameters:
        - id_agg_session (string) (required): 
        - pallet_code (any) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/disbandment_pallet"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)