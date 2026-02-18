from src.utils.http import APIClient
import requests
from src.models import WorkShiftCodeInput

def add_start_code(client: APIClient, body: WorkShiftCodeInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Add Start Code

        Добавить начальный код ролика.

        Endpoint: /api/web/v1/work_shift/range/add_start_code
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - code (string) (required): 
        """
    endpoint = "/api/web/v1/work_shift/range/add_start_code"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)