from src.utils.http import APIClient
import requests

def manual(client: APIClient, **kwargs) -> requests.Response:
    """
    192. [DEPRECATED] 192. 23.1. Метод отклонения заказа вручную (orders/reject/manual)
    
    Endpoint: api/network_proxy/api/network/v1/orders/reject/manual
    Method: PUT
    """
    endpoint = "api/network_proxy/api/network/v1/orders/reject/manual"
    return client.request("PUT", endpoint, **kwargs)
