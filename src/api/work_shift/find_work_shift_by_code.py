from src.utils.http import APIClient
import requests
from src.models import Code

def find_work_shift_by_code(client: APIClient, body: Code | dict | None = None, **kwargs) -> requests.Response:
    """
        Find Work Shift By Code

        

        Endpoint: /api/web/v1/work_shift/find_work_shift_by_code
        Method: POST

        Parameters:
        - code (string) (required): 
        """
    endpoint = "/api/web/v1/work_shift/find_work_shift_by_code"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)