from src.utils.http import APIClient
import requests
from src.models import StatsInput

def get_stats(client: APIClient, body: StatsInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Get Stats

        

        Endpoint: /api/web/v1/stats/get_stats
        Method: POST

        Parameters:
        - start_date (string) (required): 
        - end_date (string) (required): 
        """
    endpoint = "/api/web/v1/stats/get_stats"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)