from src.utils.http import APIClient
import requests
from src.models import ReportID

def remove_code(client: APIClient, body: ReportID | dict | None = None, **kwargs) -> requests.Response:
    """
        Remove Code

        

        Endpoint: /api/web/v1/report/remove_code
        Method: POST

        Parameters:
        - report_id (string) (required): 
        """
    endpoint = "/api/web/v1/report/remove_code"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)