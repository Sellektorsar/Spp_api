from src.utils.http import APIClient
import requests

def put_root(client: APIClient, **kwargs) -> requests.Response:
    """
        Network Proxy

        

        Endpoint: /api/network_proxy/{path}
        Method: PUT

        Parameters:
        """
    endpoint = "/api/network_proxy/{path}"
    return client.request("PUT", endpoint, **kwargs)
