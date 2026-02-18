from src.utils.http import APIClient
import requests
from src.models import FindCodeInput

def find(client: APIClient, body: FindCodeInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Find

        Найти данные по коду/упаковке/палете.

        Endpoint: /api/web/v1/aggregation_session/find
        Method: POST

        Parameters:
        - code (any) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/find"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)