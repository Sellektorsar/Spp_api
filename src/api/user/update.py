from src.utils.http import APIClient
import requests
from src.models import UpdateUserPermissionInput

def update(client: APIClient, body: UpdateUserPermissionInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Get User Permissions

        

        Endpoint: /api/web/v1/user/permissions/update
        Method: POST

        Parameters:
        - user_id (string) (required): 
        - user_permissions (array) (required): 
        """
    endpoint = "/api/web/v1/user/permissions/update"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)