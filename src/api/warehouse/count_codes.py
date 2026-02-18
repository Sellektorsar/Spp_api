from src.utils.http import APIClient
import requests
from src.models import ContCodesInput

def count_codes(client: APIClient, body: ContCodesInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Count Codes

        

        Endpoint: /api/web/v1/warehouse/count_codes
        Method: POST

        Parameters:
        - unit_serial_number (string): 
        - first_code (string): 
        - second_code (string): 
        """
    endpoint = "/api/web/v1/warehouse/count_codes"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)