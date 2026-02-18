from src.utils.http import APIClient
import requests
from src.models import GetLastUsedInput

def get_used_in_work_shift(client: APIClient, body: GetLastUsedInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Get Actions

        Фильтрация по полученным ролику.

        Endpoint: /api/web/v1/warehouse/get_used_in_work_shift
        Method: POST

        Parameters:
        - unit_serial_number (string) (required): 
        """
    endpoint = "/api/web/v1/warehouse/get_used_in_work_shift"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)