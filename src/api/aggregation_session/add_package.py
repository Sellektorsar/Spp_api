from src.utils.http import APIClient
import requests
from src.models import PalletsAggSessionAddPackage

def add_package(client: APIClient, body: PalletsAggSessionAddPackage | dict | None = None, **kwargs) -> requests.Response:
    """
        Pallets Add Package

        Добавить упаковку.

        Endpoint: /api/web/v1/aggregation_session/pallets/add_package
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - package_code (any) (required): 
        - is_forced (boolean): 
        """
    endpoint = "/api/web/v1/aggregation_session/pallets/add_package"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)