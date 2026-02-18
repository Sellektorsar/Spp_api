from src.utils.http import APIClient
import requests
from src.models import ChangeExpDateInput

def change_exp_date(client: APIClient, body: ChangeExpDateInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Change Exp Date

        Загрузить ролик для работы.

        Endpoint: /api/web/v1/warehouse/change_exp_date
        Method: POST

        Parameters:
        - unit_serial_number (string) (required): Идентификатор ролика
        - expired_date (string) (required): 
        """
    endpoint = "/api/web/v1/warehouse/change_exp_date"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)