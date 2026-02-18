from src.utils.http import APIClient
import requests

def orders(client: APIClient, **kwargs) -> requests.Response:
    """
    208. [DEPRECATED] 208. 23.17. Метод создания заказа на эмиссию КМ (orders)
    
    Endpoint: api/network_proxy/api/network/v1/orders
    Method: POST
    """
    endpoint = "api/network_proxy/api/network/v1/orders"
    return client.request("POST", endpoint, **kwargs)
