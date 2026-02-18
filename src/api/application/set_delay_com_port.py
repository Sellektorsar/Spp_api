from src.utils.http import APIClient
import requests

def set_delay_com_port(client: APIClient, **kwargs) -> requests.Response:
    """
    21. [DEPRECATED] 21. 4.7. Метод установки задержки для COM-порта (application/set_delay_com_port)
    
    Endpoint: api/web/v1/application/set_delay_com_port
    Method: POST
    """
    endpoint = "api/web/v1/application/set_delay_com_port"
    return client.request("POST", endpoint, **kwargs)
