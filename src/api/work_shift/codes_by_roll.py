from src.utils.http import APIClient
import requests
from src.models import CancelCodesByRoll

def codes_by_roll(client: APIClient, body: CancelCodesByRoll | dict | None = None, **kwargs) -> requests.Response:
    """
        Cancel Codes By Roll

        Отменить КМ в партии по ролику.

        Endpoint: /api/web/v1/work_shift/cancel/codes_by_roll
        Method: POST

        Parameters:
        - work_shift_id (string) (required): 
        - unit_serial_number (string) (required): 
        """
    endpoint = "/api/web/v1/work_shift/cancel/codes_by_roll"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)