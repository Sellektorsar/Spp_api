from src.utils.http import APIClient
import requests

def load(client: APIClient, **kwargs) -> requests.Response:
    """
        License Load

        Загрузить файл лицензии.

        Endpoint: /api/web/v1/license/load
        Method: POST

        Parameters:
        """
    endpoint = "/api/web/v1/license/load"
    return client.request("POST", endpoint, **kwargs)
