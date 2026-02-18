from src.utils.http import APIClient
import requests

def generate_by_file_(client: APIClient, **kwargs) -> requests.Response:
    """
    174. 15.5. Метод генерации этикеток агрегационных стикеров с кодами КИГУ из файла (barcodes/generate_by_file)
    
    Endpoint: api/web/v1/barcodes/generate_by_file.
    Method: POST
    """
    endpoint = "api/web/v1/barcodes/generate_by_file."
    return client.request("POST", endpoint, **kwargs)
