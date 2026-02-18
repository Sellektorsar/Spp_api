from src.utils.http import APIClient
import requests
from src.models import FrontLog

def set_log_from_frontend(client: APIClient, body: FrontLog | dict | None = None, **kwargs) -> requests.Response:
    """
        Set Log From Frontend

        

        Endpoint: /api/web/v1/application/set_log_from_frontend
        Method: POST

        Parameters:
        - log (string) (required): 
        """
    endpoint = "/api/web/v1/application/set_log_from_frontend"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)