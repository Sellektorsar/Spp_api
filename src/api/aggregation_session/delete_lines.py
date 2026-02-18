from src.utils.http import APIClient
import requests
from src.models import EditDashboardLines

def delete_lines(client: APIClient, body: EditDashboardLines | dict | None = None, **kwargs) -> requests.Response:
    """
        Delete Lines Agg Dashboard

        Удаление линий из дашборда.

        Endpoint: /api/web/v1/aggregation_session/dashboard/delete_lines
        Method: POST

        Parameters:
        - dashboard_id (string) (required): 
        - line_numbers (array) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/dashboard/delete_lines"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)