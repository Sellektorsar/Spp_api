from src.utils.http import APIClient
import requests
from src.models import UserToCreate

def create(client: APIClient, body: UserToCreate | dict | None = None, **kwargs) -> requests.Response:
    """
        Create New User

        Создать нового пользователя.

        Endpoint: /api/web/v1/user/create
        Method: POST

        Parameters:
        - username (string) (required): 
        - full_name (string): 
        - is_active (boolean) (required): 
        - job_title (string): 
        - password (string) (required): 
        - role_id (string) (required): 
        """
    endpoint = "/api/web/v1/user/create"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)