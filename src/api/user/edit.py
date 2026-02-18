from src.utils.http import APIClient
import requests
from src.models import EditUserInfoInput

def edit(client: APIClient, body: EditUserInfoInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Edit User Info

        

        Endpoint: /api/web/v1/user/edit
        Method: POST

        Parameters:
        - user_id (string) (required): 
        - full_name (string): 
        - job_title (string): 
        - role_id (string): 
        """
    endpoint = "/api/web/v1/user/edit"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)