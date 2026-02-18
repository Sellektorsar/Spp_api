from src.utils.http import APIClient
import requests
from src.models import RenameInput

def rename(client: APIClient, body: RenameInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Rename

        Переименовать рабочую линию.

        Endpoint: /api/web/v1/line/rename
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - new_name (string) (required): 
        """
    endpoint = "/api/web/v1/line/rename"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)