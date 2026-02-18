from src.utils.http import APIClient
import requests
from src.models import DefectRangeCode

def add_range(client: APIClient, body: DefectRangeCode | dict | None = None, **kwargs) -> requests.Response:
    """
        Cut Range Codes

        Отменить КМ в партии по диапазону.

        Endpoint: /api/web/v1/work_shift/defect/add_range
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - start_code (string) (required): 
        - end_code (string) (required): 
        """
    endpoint = "/api/web/v1/work_shift/defect/add_range"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)