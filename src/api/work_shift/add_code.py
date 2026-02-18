from src.utils.http import APIClient
import requests
from src.models import WorkShiftCodeWithVariableWeight

def add_code(client: APIClient, body: WorkShiftCodeWithVariableWeight | dict | None = None, **kwargs) -> requests.Response:
    """
        Add Code

        Добавить код.

        Endpoint: /api/web/v1/work_shift/add_code
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - code (string) (required): 
        - variable_weight (string): 
        """
    endpoint = "/api/web/v1/work_shift/add_code"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)