from src.utils.http import APIClient
import requests
from src.models import GtinFilterInput

def filter(client: APIClient, body: GtinFilterInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Gtin Filter

        

        Endpoint: /api/web/v1/gtin/filter
        Method: POST

        Parameters:
        - skip (integer): 
        - limit (integer): 
        - gtin (string): 
        - good_name (string): 
        - is_required_vsd (boolean): 
        - is_required_variable_weight (boolean): 
        - package_gtin (string): 
        - product_group (ProductGroup): 
        """
    endpoint = "/api/web/v1/gtin/filter"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)