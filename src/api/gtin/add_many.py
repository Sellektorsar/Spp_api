from src.utils.http import APIClient
import requests
from src.models import AddManyGtins

def add_many(client: APIClient, body: AddManyGtins | dict | None = None, **kwargs) -> requests.Response:
    """
        Add Many

        Добавить записи в реестр.

        Endpoint: /api/web/v1/gtin/add_many
        Method: POST

        Parameters:
        - data (array) (required): 
        """
    endpoint = "/api/web/v1/gtin/add_many"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)