from src.utils.http import APIClient
import requests
from src.models import MapRollDetailMetadataInput

def get_detail_metadata(client: APIClient, body: MapRollDetailMetadataInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Map Get Detail Metadata

        Получить метаданные для визуализации карты ролика.

        Endpoint: /api/web/v1/warehouse/map/get_detail_metadata
        Method: POST

        Parameters:
        - unit_serial_number (string) (required): 
        - index (integer) (required): 
        - limit (integer) (required): 
        """
    endpoint = "/api/web/v1/warehouse/map/get_detail_metadata"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)