from src.utils.http import APIClient
import requests
from src.models import WorkShiftRollInput

def add_roll(client: APIClient, body: WorkShiftRollInput | dict | None = None, **kwargs) -> requests.Response:
    """
        Add Roll

        Добавить ролик целиком.

        Endpoint: /api/web/v1/work_shift/add_roll
        Method: POST

        Parameters:
        - line_number (integer) (required): 
        - unit_serial_number (string) (required): Идентификатор ролика или КМ из ролика
        """
    endpoint = "/api/web/v1/work_shift/add_roll"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)