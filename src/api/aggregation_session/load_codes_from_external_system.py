from src.utils.http import APIClient
import requests
from src.models import BufferKityLoadFromExternalSystem

def load_codes_from_external_system(client: APIClient, body: BufferKityLoadFromExternalSystem | dict | None = None, **kwargs) -> requests.Response:
    """
        Buffer Kity Load From External System

        

        Endpoint: /api/web/v1/aggregation_session/buffer/kity/load_codes_from_external_system
        Method: POST

        Parameters:
        - login (string) (required): 
        - password (string) (required): 
        - count (integer): 
        """
    endpoint = "/api/web/v1/aggregation_session/buffer/kity/load_codes_from_external_system"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)