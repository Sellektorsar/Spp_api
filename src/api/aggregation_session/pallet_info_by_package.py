from src.utils.http import APIClient
import requests
from src.models import PackageInfoInput

def pallet_info_by_package(client: APIClient, body: PackageInfoInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Pallet Info By Package

        Получить информацию для палеты по ее упаковке

        Endpoint: /api/web/v1/aggregation_session/pallets/pallet_info_by_package
        Method: POST

        Parameters:
        - code (any) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/pallets/pallet_info_by_package"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)