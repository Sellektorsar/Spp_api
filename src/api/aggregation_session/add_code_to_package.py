from src.utils.http import APIClient
import requests
from src.models import AggSessionAddCodeToPackage

def add_code_to_package(client: APIClient, body: AggSessionAddCodeToPackage | dict | None = None, **kwargs) -> requests.Response:
    """
        Add Code To Package

        Добавить код в упаковку.

        Endpoint: /api/web/v1/aggregation_session/add_code_to_package
        Method: POST

        Parameters:
        - code (string) (required): 
        - package_code (any) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/add_code_to_package"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)