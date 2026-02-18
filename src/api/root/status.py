from src.utils.http import APIClient
import requests

def status(client: APIClient, **kwargs) -> requests.Response:
    """
        Status

        Проверить работу приложения

        Endpoint: /api/status
        Method: GET

        Parameters:
        """
    endpoint = "/api/status"
    return client.request("GET", endpoint, **kwargs)
