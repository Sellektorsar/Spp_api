from src.utils.http import APIClient
import requests
from src.models import DisableSendReport

def change(client: APIClient, body: DisableSendReport | dict | None = None, **kwargs) -> requests.Response:
    """
        Disable Send Report

        Изменить флаг запрещающий отправку отчетов.

        Endpoint: /api/web/v1/application/disable_send_report/change
        Method: POST

        Parameters:
        - disable_send_report (boolean) (required): 
        """
    endpoint = "/api/web/v1/application/disable_send_report/change"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)