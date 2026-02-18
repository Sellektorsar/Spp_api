from src.utils.http import APIClient
import requests

def approve(client: APIClient, **kwargs) -> requests.Response:
    """
    205. [DEPRECATED] 205. 23.14. Метод подтверждения заказа (orders/approve)
    
    Endpoint: api/network_proxy/api/network/v1/orders/approve
    Method: POST
    """
    endpoint = "api/network_proxy/api/network/v1/orders/approve"
    return client.request("POST", endpoint, **kwargs)
