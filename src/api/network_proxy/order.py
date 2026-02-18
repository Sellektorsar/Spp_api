from src.utils.http import APIClient
import requests

def order(client: APIClient, **kwargs) -> requests.Response:
    """
    198. [DEPRECATED] 198. 23.7. Метод скачивания заказа
    
    Endpoint: api/network_proxy/api/network/v1/download/order
    Method: GET
    """
    endpoint = "api/network_proxy/api/network/v1/download/order"
    return client.request("GET", endpoint, **kwargs)
