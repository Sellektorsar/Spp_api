from src.utils.http import APIClient
import requests
from src.models import AddSetInput

def add(client: APIClient, body: AddSetInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Add Set

        

        Endpoint: /api/web/v1/set/add
        Method: POST

        Parameters:
        - set_gtin (string) (required): 
        - set_name (string): 
        - product_group (ProductGroup) (required): 
        - structure (array) (required): 
        """
    endpoint = "/api/web/v1/set/add"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)