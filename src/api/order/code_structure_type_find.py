from src.utils.http import APIClient
import requests
from src.models import InputOrderCodeStructure

def code_structure_type_find(client: APIClient, body: InputOrderCodeStructure | dict | None = None, **kwargs) -> requests.Response:
    """
        Get Code Structure

        

        Endpoint: /api/web/v1/order/code_structure_type_find
        Method: POST

        Parameters:
        - product_group (string) (required): 
        - template_id (integer): 
        """
    endpoint = "/api/web/v1/order/code_structure_type_find"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)