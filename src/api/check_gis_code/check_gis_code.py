from src.utils.http import APIClient
import requests
from src.models import CheckGISCode

def check_gis_code(client: APIClient, body: CheckGISCode | dict | None = None, **kwargs) -> requests.Response:
    """
        Check Gis Code

        

        Endpoint: /api/web/v1/check_gis_code
        Method: POST

        Parameters:
        - code (any) (required): 
        """
    endpoint = "/api/web/v1/check_gis_code"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)