from src.utils.http import APIClient
import requests
from src.models import GetStatsDash

def get_stats_with_gtin(client: APIClient, body: GetStatsDash | dict | None = None, **kwargs) -> requests.Response:
    """
        Get Stats Agg Dashboard With Gtin

        Получение статистики в разрезе ГТИНа.

        Endpoint: /api/web/v1/aggregation_session/dashboard/get_stats_with_gtin
        Method: POST

        Parameters:
        - start_date (string) (required): 
        - end_date (string) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/dashboard/get_stats_with_gtin"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)