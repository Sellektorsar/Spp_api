from src.utils.http import APIClient
import requests
from src.models import ServerIpInput

def set_server_ip(client: APIClient, body: ServerIpInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Set Ip Adrr Server

        Добавление внешнего ip адреса сервера

        Endpoint: /api/web/v1/printer/cups/set_server_ip
        Method: POST

        Parameters:
        - server_ip (string) (required): 
        """
    endpoint = "/api/web/v1/printer/cups/set_server_ip"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)