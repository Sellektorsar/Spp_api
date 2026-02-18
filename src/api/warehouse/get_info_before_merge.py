from src.utils.http import APIClient
import requests
from src.models import MergeInput

def get_info_before_merge(client: APIClient, body: MergeInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Get Info Before Merge

        Получение предварительной информации перед слиянием.

        Endpoint: /api/web/v1/warehouse/get_info_before_merge
        Method: POST

        Parameters:
        - first_code (string) (required): 
        - second_code (string) (required): 
        """
    endpoint = "/api/web/v1/warehouse/get_info_before_merge"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)