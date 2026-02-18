from src.utils.http import APIClient
import requests

def refresh_conf_data(client: APIClient, **kwargs) -> requests.Response:
    """
        Refresh Conf Data

        

        Endpoint: /api/web/v1/application/refresh_conf_data
        Method: GET

        Parameters:
        """
    endpoint = "/api/web/v1/application/refresh_conf_data"
    return client.request("GET", endpoint, **kwargs)
