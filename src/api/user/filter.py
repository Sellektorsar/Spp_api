from src.utils.http import APIClient
import requests
from src.models import UserFilterInput

def filter(client: APIClient, body: UserFilterInput | dict | None = None, **kwargs) -> requests.Response:
    """
        User Filter

        

        Endpoint: /api/web/v1/user/filter
        Method: POST

        Parameters:
        - skip (integer): 
        - limit (integer): 
        - full_name (string): 
        - job_title (string): 
        - role_id (string): 
        - is_active (boolean): 
        - registration_date_start (string): 
        - registration_date_end (string): 
        - update_user_info_date_start (string): 
        - update_user_info_date_end (string): 
        - last_auth_date_start (string): 
        - last_auth_date_end (string): 
        - sorting (array): 
        """
    endpoint = "/api/web/v1/user/filter"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)