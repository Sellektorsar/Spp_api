from src.utils.http import APIClient
import requests
from src.models import AggSessionCancelCode

def withdrawal_code(client: APIClient, body: AggSessionCancelCode | dict | None = None, **kwargs) -> requests.Response:
    """
        Withdrawal Code

        Изъять код из агрегата.

        Endpoint: /api/web/v1/aggregation_session/withdrawal_code
        Method: POST

        Parameters:
        - code (string) (required): 
        - package_code (any) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/withdrawal_code"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)