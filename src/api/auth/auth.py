from src.utils.http import APIClient
import requests

def auth(client: APIClient, **kwargs) -> requests.Response:
    """
        Authenticate

        Получить bearer токен для авторизации.

        Endpoint: /api/web/v1/auth
        Method: POST

        Parameters:
        """
    endpoint = "/api/web/v1/auth"
    return client.request("POST", endpoint, **kwargs)
