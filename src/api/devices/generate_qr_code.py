from src.utils.http import APIClient
import requests
from src.models import QR_CODE_Device

def generate_qr_code(client: APIClient, body: QR_CODE_Device | dict | None = None, **kwargs) -> requests.Response:
    """
        Generate Qr

        Генерация qr code с ссылкой на сервер и token устройства

        Endpoint: /api/web/v1/devices/generate_qr_code
        Method: POST

        Parameters:
        - device_id (string) (required): 
        """
    endpoint = "/api/web/v1/devices/generate_qr_code"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)