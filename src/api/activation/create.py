from src.utils.http import APIClient
import requests
from src.models import ActivationCreateInput

def create(client: APIClient, body: ActivationCreateInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Activation Create

        Активировать SPP.

        Endpoint: /api/web/v1/activation/create
        Method: POST

        Parameters:
        - mcdn_token (string) (required): 
        - user (UserWithPassword) (required): 
        - owner_profile (OwnerProfile) (required): 
        """
    endpoint = "/api/web/v1/activation/create"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)