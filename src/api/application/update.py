from src.utils.http import APIClient
import requests

def update(client: APIClient, **kwargs) -> requests.Response:
    """
        Update App

        Обновить приложение

        Endpoint: /api/web/v1/application/update
        Method: GET

        Parameters:
        """
    endpoint = "/api/web/v1/application/update"
    return client.request("GET", endpoint, **kwargs)
