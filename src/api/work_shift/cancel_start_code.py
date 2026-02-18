from src.utils.http import APIClient
import requests
from src.models import CancelStartCodeInput

def cancel_start_code(client: APIClient, body: CancelStartCodeInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Cancel Start Code

        Отменить начальный код ролика.

        Endpoint: /api/web/v1/work_shift/range/cancel_start_code
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        """
    endpoint = "/api/web/v1/work_shift/range/cancel_start_code"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)