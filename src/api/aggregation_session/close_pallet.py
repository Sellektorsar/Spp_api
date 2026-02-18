from src.utils.http import APIClient
import requests
from src.models import AggSessionFinish

def close_pallet(client: APIClient, body: AggSessionFinish | dict | None = None, **kwargs) -> requests.Response:
    """
        Close Pallet

        Закрыть палет.

        Endpoint: /api/web/v1/aggregation_session/close_pallet
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - pin_code (string): 
        """
    endpoint = "/api/web/v1/aggregation_session/close_pallet"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)