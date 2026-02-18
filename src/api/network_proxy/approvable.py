from src.utils.http import APIClient
import requests

def approvable(client: APIClient, **kwargs) -> requests.Response:
    """
    200. [DEPRECATED] 200. 23.9. Метод получения списка заказов для подтверждения (orders/approvable)
    
    Endpoint: api/network_proxy/api/network/v1/orders/approvable
    Method: POST
    """
    endpoint = "api/network_proxy/api/network/v1/orders/approvable"
    return client.request("POST", endpoint, **kwargs)
