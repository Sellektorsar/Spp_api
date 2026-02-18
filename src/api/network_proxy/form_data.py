from src.utils.http import APIClient
import requests

def form_data(client: APIClient, **kwargs) -> requests.Response:
    """
    195. [DEPRECATED] 195. 23.4. Метод получения данных для формы создания заказа (orders/form-data)
    
    Endpoint: api/network_proxy/api/network/v1/orders/form-data
    Method: GET
    """
    endpoint = "api/network_proxy/api/network/v1/orders/form-data"
    return client.request("GET", endpoint, **kwargs)
