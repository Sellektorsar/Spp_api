from src.utils.http import APIClient
import requests
from src.models import DashboardUpdate

def update(client: APIClient, body: DashboardUpdate | dict | None = None, **kwargs) -> requests.Response:
    """
        Update Lines Agg Dashboard

        Обновление данных в дашборде.

        Endpoint: /api/web/v1/aggregation_session/dashboard/update
        Method: POST

        Parameters:
        - dashboard_id (string) (required): 
        - name (string): 
        - hide_inactive_lines (boolean): 
        - line_numbers (array): 
        """
    endpoint = "/api/web/v1/aggregation_session/dashboard/update"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)