from src.utils.http import APIClient
import requests
from src.models import UpdateDataGtinFlag

def change_flag_update_gtin_registry(client: APIClient, body: UpdateDataGtinFlag | dict | None = None, **kwargs) -> requests.Response:
    """
        Change Flag Update Gtin Registry

        Смена значения флага для обновления всех данных реестра gtin.

        Endpoint: /api/web/v1/gtin/change_flag_update_gtin_registry
        Method: POST

        Parameters:
        - update_data_gtin (boolean) (required): 
        """
    endpoint = "/api/web/v1/gtin/change_flag_update_gtin_registry"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)