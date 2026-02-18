from src.utils.http import APIClient
import requests

def get_app_conf(client: APIClient, **kwargs) -> requests.Response:
    """
        Get App Conf

        Получить конфигурацию приложения.

        Endpoint: /api/web/v1/application/get_app_conf
        Method: GET

        Parameters:
        """
    endpoint = "/api/web/v1/application/get_app_conf"
    return client.request("GET", endpoint, **kwargs)
