from src.utils.http import APIClient
import requests
from src.models import DownloadShipmentCodes

def download(client: APIClient, body: DownloadShipmentCodes | dict | None = None, **kwargs) -> requests.Response:
    """
        Download Codes

        Скачать csv файл отгрузки

        Endpoint: /api/web/v1/shipment/codes/download
        Method: POST

        Parameters:
        - shipment_id (string) (required): 
        - file_type (any): 
        """
    endpoint = "/api/web/v1/shipment/codes/download"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)