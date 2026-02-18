from src.utils.http import APIClient
import requests
from src.models import AggSessionAddPackageWithCodes

def add_package_with_codes(client: APIClient, body: AggSessionAddPackageWithCodes | dict | None = None, **kwargs) -> requests.Response:
    """
        Vision Add Package With Codes

        Добавление кода агрегации и км для тех. зрения.

        Endpoint: /api/web/v1/aggregation_session/vision/add_package_with_codes
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - package_code (any) (required): 
        - codes (array) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/vision/add_package_with_codes"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)