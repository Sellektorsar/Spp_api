from src.utils.http import APIClient
import requests
from src.models import GetRollByCodeInput

def get_roll_by_code(client: APIClient, body: GetRollByCodeInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Check Nesting

        Загрузить ролик по КМ.

        Endpoint: /api/web/v1/warehouse/get_roll_by_code
        Method: POST

        Parameters:
        - code (string) (required): 
        """
    endpoint = "/api/web/v1/warehouse/get_roll_by_code"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)