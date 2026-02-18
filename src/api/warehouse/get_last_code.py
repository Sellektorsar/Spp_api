from src.utils.http import APIClient
import requests
from src.models import GetLastCodeInput

def get_last_code(client: APIClient, body: GetLastCodeInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Get Last Code

        Получить метаданные для визуализации карты ролика.

        Endpoint: /api/web/v1/warehouse/get_last_code
        Method: POST

        Parameters:
        - first_code (string) (required): 
        - second_code (string) (required): 
        """
    endpoint = "/api/web/v1/warehouse/get_last_code"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)