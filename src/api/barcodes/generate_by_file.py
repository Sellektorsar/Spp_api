from src.utils.http import APIClient
import requests

def generate_by_file(client: APIClient, **kwargs) -> requests.Response:
    """
        Generate By File

        

        Endpoint: /api/web/v1/barcodes/generate_by_file
        Method: POST

        Parameters:
        - layout_id (string) (required): 
        """
    endpoint = "/api/web/v1/barcodes/generate_by_file"
    return client.request("POST", endpoint, **kwargs)
