from src.utils.http import APIClient
import requests

def related_area_id(client: APIClient, **kwargs) -> requests.Response:
    """
    206. [DEPRECATED] 206. 23.15. Метод получения связанных площадок (orders/issuers/{related-area-id})
    
    Endpoint: api/network_proxy/api/network/v1/orders/issuers/{related-area-id}
    Method: GET
    """
    endpoint = "api/network_proxy/api/network/v1/orders/issuers/{related-area-id}"
    return client.request("GET", endpoint, **kwargs)
