from src.utils.http import APIClient
import requests
from src.models import WorkShiftInput

def resume(client: APIClient, body: WorkShiftInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Resume

        Возобновить производственную партию.

        Endpoint: /api/web/v1/work_shift/resume
        Method: POST

        Parameters:
        - work_shift_id (string) (required): 
        """
    endpoint = "/api/web/v1/work_shift/resume"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)