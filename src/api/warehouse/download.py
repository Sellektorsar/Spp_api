from src.utils.http import APIClient
import requests
from src.models import DownloadWarehouseFile

def download(client: APIClient, body: DownloadWarehouseFile | dict | None = None, **kwargs) -> requests.Response:
    """
        Download Codes

        Получить всю информацию по ролику.

        Endpoint: /api/web/v1/warehouse/download
        Method: POST

        Parameters:
        - unit_serial_number (string) (required): Идентификатор ролика
        - file_type (any): 
        """
    endpoint = "/api/web/v1/warehouse/download"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)