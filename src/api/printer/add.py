from src.utils.http import APIClient
import requests
from src.models import AddInput

def add(client: APIClient, body: AddInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Add

        Добавить принтер.

        Endpoint: /api/web/v1/printer/add
        Method: POST

        Parameters:
        - name (string) (required): 
        - printer_cups_name (string) (required): 
        - print_type (PRINTER_PRINT_TYPE) (required): 
        - host (string) (required): 
        - port (integer): 
        - owner_name (string): 
        """
    endpoint = "/api/web/v1/printer/add"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)