from src.utils.http import APIClient
import requests

def statistics(client: APIClient, **kwargs) -> requests.Response:
    """
    204. [DEPRECATED] 204. 23.13. Метод получения статистики по заказам (orders/statistics)
    
    Endpoint: api/network_proxy/api/network/v1/orders/statistics
    Method: GET
    """
    endpoint = "api/network_proxy/api/network/v1/orders/statistics"
    return client.request("GET", endpoint, **kwargs)
