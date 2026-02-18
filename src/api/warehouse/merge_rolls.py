from src.utils.http import APIClient
import requests
from src.models import MergeInput

def merge_rolls(client: APIClient, body: MergeInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Merge Rolls

        Слияние двух роликов в третий.

        Endpoint: /api/web/v1/warehouse/merge_rolls
        Method: POST

        Parameters:
        - first_code (string) (required): 
        - second_code (string) (required): 
        """
    endpoint = "/api/web/v1/warehouse/merge_rolls"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)