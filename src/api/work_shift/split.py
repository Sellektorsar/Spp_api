from src.utils.http import APIClient
import requests
from src.models import WorkShiftSplitInput

def split(client: APIClient, body: WorkShiftSplitInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Split

        

        Endpoint: /api/web/v1/work_shift/split
        Method: POST

        Parameters:
        - work_shift_id (string) (required): 
        - count (integer): 
        """
    endpoint = "/api/web/v1/work_shift/split"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)