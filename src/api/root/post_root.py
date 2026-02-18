from src.utils.http import APIClient
import requests

def post_root(client: APIClient, **kwargs) -> requests.Response:
    """
        Network Proxy

        

        Endpoint: /api/network_proxy/{path}
        Method: POST

        Parameters:
        """
    endpoint = "/api/network_proxy/{path}"
    return client.request("POST", endpoint, **kwargs)
