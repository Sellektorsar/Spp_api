from src.utils.http import APIClient
import requests
from src.models import LayoutToggleFavorite

def toggle_favorite(client: APIClient, body: LayoutToggleFavorite | dict | None = None, **kwargs) -> requests.Response:
    """
        Layout Toggle Favorite

        

        Endpoint: /api/web/v1/printer/layout/toggle_favorite
        Method: POST

        Parameters:
        - layout_id (string) (required): 
        - is_favorite (boolean) (required): 
        """
    endpoint = "/api/web/v1/printer/layout/toggle_favorite"
    if body:
        if hasattr(body, "model_dump"):
            kwargs["json"] = body.model_dump(mode='json', by_alias=True, exclude_none=True)
        else:
            kwargs["json"] = body
    return client.request("POST", endpoint, **kwargs)