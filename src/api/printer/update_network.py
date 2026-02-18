from src.utils.http import APIClient
import requests

def update_network(client: APIClient, **kwargs) -> requests.Response:
    """
        Update Network Printers By Cups

        Обновление актуальности принтеров с помощью cups

        Endpoint: /api/web/v1/printer/cups/update_network
        Method: POST

        Parameters:
        """
    endpoint = "/api/web/v1/printer/cups/update_network"
    return client.request("POST", endpoint, **kwargs)
