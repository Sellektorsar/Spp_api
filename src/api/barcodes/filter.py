from src.utils.http import APIClient
import requests
from src.models import BarcodesGeneratedFilter

def filter(client: APIClient, body: BarcodesGeneratedFilter | dict | None = None, **kwargs) -> requests.Response:
    """
        Generated Filter

        

        Endpoint: /api/web/v1/barcodes/generated/filter
        Method: POST

        Parameters:
        - skip (integer): 
        - limit (integer): 
        """
    endpoint = "/api/web/v1/barcodes/generated/filter"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)