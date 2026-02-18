from src.utils.http import APIClient
import requests
from src.models import EditSetInput

def edit(client: APIClient, body: EditSetInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Edit Set

        

        Endpoint: /api/web/v1/set/edit
        Method: POST

        Parameters:
        - set_gtin (string) (required): 
        - set_name (string): 
        - product_group (ProductGroup): 
        - structure (array): 
        """
    endpoint = "/api/web/v1/set/edit"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)