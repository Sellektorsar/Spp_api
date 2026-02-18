from src.utils.http import APIClient
import requests
from src.models import CheckCodeInput

def check_code(client: APIClient, body: CheckCodeInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Check Code

        Проверка кода

        Endpoint: /api/web/v1/aggregation_session/check_code
        Method: POST

        Parameters:
        - code (string) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/check_code"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)