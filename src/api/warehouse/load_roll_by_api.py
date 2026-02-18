from src.utils.http import APIClient
import requests
from src.models import InputLoadAPI

def load_roll_by_api(client: APIClient, body: InputLoadAPI | dict | None = None, **kwargs) -> requests.Response:
    """
        Load Roll By Api

        Загрузить ролик

        Endpoint: /api/web/v1/warehouse/load_roll_by_api
        Method: POST

        Parameters:
        - unit_serial_number (string) (required): Идентификатор ролика
        """
    endpoint = "/api/web/v1/warehouse/load_roll_by_api"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)