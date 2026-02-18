from src.utils.http import APIClient
import requests

def tips(client: APIClient, **kwargs) -> requests.Response:
    """
    194. [DEPRECATED] 194. 23.3. Метод получения списка GTIN, по которым создавались заказы (orders/gtins/tips)
    
    Endpoint: api/network_proxy/api/network/v1/orders/gtins/tips
    Method: GET
    """
    endpoint = "api/network_proxy/api/network/v1/orders/gtins/tips"
    return client.request("GET", endpoint, **kwargs)
