from src.utils.http import APIClient
import requests
from src.models import ReportID

def resend(client: APIClient, body: ReportID | dict | None = None, **kwargs) -> requests.Response:
    """
        Resend Report

        Переотправить отчет.

        Endpoint: /api/web/v1/report/resend
        Method: POST

        Parameters:
        - report_id (string) (required): 
        """
    endpoint = "/api/web/v1/report/resend"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)