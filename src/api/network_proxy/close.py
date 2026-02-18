from src.utils.http import APIClient
import requests

def close(client: APIClient, **kwargs) -> requests.Response:
    """
    197. [DEPRECATED] 197. 23.6. Метод закрытия заказа (orders/action/close)
    
    Endpoint: api/network_proxy/api/network/v1/orders/action/close
    Method: GET
    """
    endpoint = "api/network_proxy/api/network/v1/orders/action/close"
    return client.request("GET", endpoint, **kwargs)
