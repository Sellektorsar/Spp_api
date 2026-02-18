from src.utils.http import APIClient
import requests
from src.models import CancelCode

def code(client: APIClient, body: CancelCode | dict | None = None, **kwargs) -> requests.Response:
    """
        Cancel Code

        Отменить КМ в партии по коду.

        Endpoint: /api/web/v1/work_shift/cancel/code
        Method: POST

        Parameters:
        - work_shift_id (string) (required): 
        - code (string) (required): 
        """
    endpoint = "/api/web/v1/work_shift/cancel/code"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)