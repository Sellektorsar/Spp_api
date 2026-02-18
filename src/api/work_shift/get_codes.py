from src.utils.http import APIClient
import requests
from src.models import WorkShiftInput

def get_codes(client: APIClient, body: WorkShiftInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Get Codes

        Вернуть список КМ в партии.

        Endpoint: /api/web/v1/work_shift/get_codes
        Method: POST

        Parameters:
        - work_shift_id (string) (required): 
        """
    endpoint = "/api/web/v1/work_shift/get_codes"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)