from src.utils.http import APIClient
import requests
from src.models import DisbandmentPackageInput

def disbandment_package(client: APIClient, body: DisbandmentPackageInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Disbandment Package

        Расформировать упаковку.

        Endpoint: /api/web/v1/aggregation_session/disbandment_package
        Method: POST

        Parameters:
        - package_code (any) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/disbandment_package"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)