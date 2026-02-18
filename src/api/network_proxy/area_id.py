from src.utils.http import APIClient
import requests

def area_id(client: APIClient, **kwargs) -> requests.Response:
    """
    202. [DEPRECATED] 202. 23.11. Метод получения получателя заказа (orders/receivers/{area-id})
    
    Endpoint: api/network_proxy/api/network/v1/orders/receivers/{area-id}
    Method: GET
    """
    endpoint = "api/network_proxy/api/network/v1/orders/receivers/{area-id}"
    return client.request("GET", endpoint, **kwargs)
