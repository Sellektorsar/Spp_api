from src.utils.http import APIClient
import requests
from src.models import WorkShiftRenameInput

def rename(client: APIClient, body: WorkShiftRenameInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Finish

        

        Endpoint: /api/web/v1/work_shift/rename
        Method: POST

        Parameters:
        - work_shift_id (string) (required): 
        - new_name (string) (required): 
        """
    endpoint = "/api/web/v1/work_shift/rename"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)