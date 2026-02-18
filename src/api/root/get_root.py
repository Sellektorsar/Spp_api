from src.utils.http import APIClient
import requests

def get_root(client: APIClient, **kwargs) -> requests.Response:
    """
        Network Proxy

        

        Endpoint: /api/network_proxy/{path}
        Method: GET

        Parameters:
        """
    endpoint = "/api/network_proxy/{path}"
    return client.request("GET", endpoint, **kwargs)
