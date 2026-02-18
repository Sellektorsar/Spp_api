from src.utils.http import APIClient
import requests

def codes_transfer(client: APIClient, **kwargs) -> requests.Response:
    """
    201. [DEPRECATED] 201. 23.10. Метод передачи КМ из заказа (codes-transfer)
    
    Endpoint: api/network_proxy/api/network/v1/codes-transfer
    Method: POST
    """
    endpoint = "api/network_proxy/api/network/v1/codes-transfer"
    return client.request("POST", endpoint, **kwargs)
