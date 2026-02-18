from src.utils.http import APIClient
import requests
from src.models import SetStatusInput

def set_report_status(client: APIClient, body: SetStatusInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Set Report Status

        

        Endpoint: /api/web/v1/report/set_report_status
        Method: POST

        Parameters:
        - report_id (string) (required): 
        - status (ReportStatus) (required): 
        """
    endpoint = "/api/web/v1/report/set_report_status"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)