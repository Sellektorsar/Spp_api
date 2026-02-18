from src.utils.http import APIClient
import requests

def get_owner_profile(client: APIClient, **kwargs) -> requests.Response:
    """
        Get Owner Profile

        Вернуть профиль владельца

        Endpoint: /api/web/v1/get_owner_profile
        Method: GET

        Parameters:
        """
    endpoint = "/api/web/v1/get_owner_profile"
    return client.request("GET", endpoint, **kwargs)
