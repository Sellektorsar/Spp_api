from src.utils.http import APIClient
import requests
from src.models import ChangeIsArchivedAttr

def change(client: APIClient, body: ChangeIsArchivedAttr | dict | None = None, **kwargs) -> requests.Response:
    """
        Change Is Archived State

        Изменить атрибут is_archived ролика.

        Endpoint: /api/web/v1/warehouse/is_archived/change
        Method: POST

        Parameters:
        - unit_serial_number (string) (required): 
        - is_archived (boolean) (required): 
        """
    endpoint = "/api/web/v1/warehouse/is_archived/change"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)