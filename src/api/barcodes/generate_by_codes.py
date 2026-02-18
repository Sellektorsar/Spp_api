from src.utils.http import APIClient
import requests
from src.models import BarcodesInput

def generate_by_codes(client: APIClient, body: BarcodesInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Generate By Codes

        Получить pdf файл с штрих-кодами всех входных номеров агрегации.

        Endpoint: /api/web/v1/barcodes/generate_by_codes
        Method: POST

        Parameters:
        - data (array) (required): 
        """
    endpoint = "/api/web/v1/barcodes/generate_by_codes"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)