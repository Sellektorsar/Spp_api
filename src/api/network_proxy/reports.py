from src.utils.http import APIClient
import requests

def reports(client: APIClient, **kwargs) -> requests.Response:
    """
    193. [DEPRECATED] 193. 23.2. Метод получения данных документа по заказу (orders/info/reports)
    
    Endpoint: api/network_proxy/api/network/v1/orders/info/reports
    Method: GET
    """
    endpoint = "api/network_proxy/api/network/v1/orders/info/reports"
    return client.request("GET", endpoint, **kwargs)
