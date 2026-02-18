from src.utils.http import APIClient
import requests
from src.models import ReportStatisticsInput

def statistics(client: APIClient, body: ReportStatisticsInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Filter Data

        Получение статистики по отчетам.

        Endpoint: /api/web/v1/report/statistics
        Method: POST

        Parameters:
        - created_date_start (string): 
        - created_date_end (string): 
        """
    endpoint = "/api/web/v1/report/statistics"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)