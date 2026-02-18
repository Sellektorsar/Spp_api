from src.utils.http import APIClient
import requests

def update_data_gtin(client: APIClient, **kwargs) -> requests.Response:
    """
        Update Data Gtin

        Обновление всех данных реестра gtin.

        Endpoint: /api/web/v1/gtin/update_data_gtin
        Method: POST

        Parameters:
        """
    endpoint = "/api/web/v1/gtin/update_data_gtin"
    return client.request("POST", endpoint, **kwargs)
