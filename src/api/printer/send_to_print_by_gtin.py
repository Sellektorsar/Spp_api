from src.utils.http import APIClient
import requests
from src.models import NetworkPrintCupsGtinInput

def send_to_print_by_gtin(client: APIClient, body: NetworkPrintCupsGtinInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Send To Print Cups By Gtin

        Отправить запрос на печать с  помощью cups по gtin

        Endpoint: /api/web/v1/printer/cups/send_to_print_by_gtin
        Method: POST

        Parameters:
        - gtin (string) (required): 
        - type (api__web__v1__aggregation_session__models__SSCC_TYPE) (required): 
        - count_codes (integer) (required): 
        - count_copies (integer) (required): 
        - printer_id (string) (required): 
        - layout_id (string) (required): 
        """
    endpoint = "/api/web/v1/printer/cups/send_to_print_by_gtin"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)