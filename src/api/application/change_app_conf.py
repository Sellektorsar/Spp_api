from src.utils.http import APIClient
import requests
from src.models import ChangeAppConf

def change_app_conf(client: APIClient, body: ChangeAppConf | dict | None = None, **kwargs) -> requests.Response:
    """
        Change App Conf

        

        Endpoint: /api/web/v1/application/change_app_conf
        Method: POST

        Parameters:
        - product_group (array): 
        - production_type (array): 
        """
    endpoint = "/api/web/v1/application/change_app_conf"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)