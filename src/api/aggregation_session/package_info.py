from src.utils.http import APIClient
import requests
from src.models import PackageInfoInput

def package_info(client: APIClient, body: PackageInfoInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Pallets Package Info

        Получить информацию для упаковки или палеты

        Endpoint: /api/web/v1/aggregation_session/pallets/package_info
        Method: POST

        Parameters:
        - code (any) (required): 
        """
    endpoint = "/api/web/v1/aggregation_session/pallets/package_info"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)