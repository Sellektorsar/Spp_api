from src.utils.http import APIClient
import requests
from src.models import InfoDashInput

def get_info(client: APIClient, body: InfoDashInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Get Info Agg Dashboard

        Получение информации о дашборде.

        Endpoint: /api/web/v1/aggregation_session/dashboard/get_info
        Method: POST

        Parameters:
        - dashboard_id (string) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/dashboard/get_info"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)