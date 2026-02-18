from src.utils.http import APIClient
import requests

def me(client: APIClient, **kwargs) -> requests.Response:
    """
        Read Users Me

        Получить информацию о текущем активном пользователе.

        Endpoint: /api/web/v1/user/me
        Method: GET

        Parameters:
        """
    endpoint = "/api/web/v1/user/me"
    return client.request("GET", endpoint, **kwargs)
