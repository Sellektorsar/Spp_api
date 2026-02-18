from src.utils.http import APIClient
import requests
from src.models import LoadInput

def load(client: APIClient, body: LoadInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Load

        Загрузить ролик для работы.

        Endpoint: /api/web/v1/warehouse/load
        Method: POST

        Parameters:
        - unit_serial_number (string) (required): Идентификатор ролика или КМ из ролика
        """
    endpoint = "/api/web/v1/warehouse/load"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)