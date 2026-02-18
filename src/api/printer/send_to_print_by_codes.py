from src.utils.http import APIClient
import requests
from src.models import NetworkPrintCupsCodesInput

def send_to_print_by_codes(client: APIClient, body: NetworkPrintCupsCodesInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Send To Print Cups By Codes

        Отправить запрос на печать с помощью cups

        Endpoint: /api/web/v1/printer/cups/send_to_print_by_codes
        Method: POST

        Parameters:
        - data (array) (required): 
        """
    endpoint = "/api/web/v1/printer/cups/send_to_print_by_codes"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)