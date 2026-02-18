from src.utils.http import APIClient
import requests

def contract_areas(client: APIClient, **kwargs) -> requests.Response:
    """
    209. [DEPRECATED] 209. 23.18. Метод получения информации о площадке-получателе КМ (codes-transfer/contract-areas)
    
    Endpoint: api/network_proxy/api/network/v1/codes-transfer/contract-areas
    Method: GET
    """
    endpoint = "api/network_proxy/api/network/v1/codes-transfer/contract-areas"
    return client.request("GET", endpoint, **kwargs)
