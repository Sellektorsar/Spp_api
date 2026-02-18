from src.utils.http import APIClient
import requests
from src.models import SetFilterInput

def filter(client: APIClient, body: SetFilterInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Set Filter

        

        Endpoint: /api/web/v1/set/filter
        Method: POST

        Parameters:
        - skip (integer): 
        - limit (integer): 
        - set_gtin (string): 
        - set_name (string): 
        - product_group (ProductGroup): 
        """
    endpoint = "/api/web/v1/set/filter"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)