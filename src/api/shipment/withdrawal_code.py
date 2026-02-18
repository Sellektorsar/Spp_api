from src.utils.http import APIClient
import requests
from src.models import ShipmentWithdrawalCode

def withdrawal_code(client: APIClient, body: ShipmentWithdrawalCode | dict | None = None, **kwargs) -> requests.Response:
    """
        Withdrawal Code

        Изъять агрегат, собранный ранее

        Endpoint: /api/web/v1/shipment/withdrawal_code
        Method: POST

        Parameters:
        - shipment_id (string) (required): 
        - sscc_code (any) (required): 
        """
    endpoint = "/api/web/v1/shipment/withdrawal_code"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)