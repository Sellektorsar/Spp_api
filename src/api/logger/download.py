from src.utils.http import APIClient
import requests

def download(client: APIClient, **kwargs) -> requests.Response:
    """
        Service Shipment Download Log

        

        Endpoint: /api/web/v1/logger/service/shipment/download
        Method: POST

        Parameters:
        """
    endpoint = "/api/web/v1/logger/service/shipment/download"
    return client.request("POST", endpoint, **kwargs)
