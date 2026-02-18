from src.utils.http import APIClient
import requests
from src.models import WorkShiftFinishInput

def finish(client: APIClient, body: WorkShiftFinishInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Finish

        Завершить производственную партию.

        Endpoint: /api/web/v1/work_shift/finish
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - pin_code (string): 
        """
    endpoint = "/api/web/v1/work_shift/finish"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)