from src.utils.http import APIClient
import requests
from src.models import Recipient

def add_recipient(client: APIClient, body: Recipient | dict | None = None, **kwargs) -> requests.Response:
    """
        Add Rec

        Добавить получателя уведомлений.

        Endpoint: /api/web/v1/notification/add_recipient
        Method: POST

        Parameters:
        - email (string) (required): 
        """
    endpoint = "/api/web/v1/notification/add_recipient"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)