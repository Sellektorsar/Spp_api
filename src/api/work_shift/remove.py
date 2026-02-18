from src.utils.http import APIClient
import requests
from src.models import WorkShiftCodeInput

def remove(client: APIClient, body: WorkShiftCodeInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Remove Defect

        Вернуть вырезанный брак

        Endpoint: /api/web/v1/work_shift/defect/remove
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - code (string) (required): 
        """
    endpoint = "/api/web/v1/work_shift/defect/remove"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)